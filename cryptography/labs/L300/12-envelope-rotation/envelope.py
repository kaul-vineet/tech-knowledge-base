"""Envelope encryption with a versioned key-encryption key (KEK) and a rewrap job.
Each record gets its own data key (DEK); the DEK is wrapped by the KEK version named in the record header.
Learning code: in production the KEK stays inside a KMS/HSM or OpenBao transit and never leaves it."""
import base64
import json
import os
import random

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SEED = 12  # seeds the injected fault (where the rewrap job crashes), so every run fails the same way


class UnknownKey(Exception):
    """The record names a KEK version that is not (or no longer) in the keyring."""


class KeyInUse(Exception):
    """Raised by the hardened retire() you write in the build task."""


def b64(b: bytes) -> str:
    return base64.b64encode(b).decode()


class Keyring:
    """KEK versions by number: the primary wraps new DEKs, every version still present can unwrap."""

    def __init__(self, name="orders-kek"):
        self.name, self.versions, self.primary = name, {}, 0
        self.rotate()

    def kid(self, version: int) -> str:
        return f"{self.name}:v{version}"  # key ID: written into every record header

    def rotate(self) -> str:
        self.primary += 1  # rotation = add a new version and make it primary; old versions stay
        self.versions[self.primary] = AESGCM.generate_key(bit_length=256)
        return self.kid(self.primary)

    def kek(self, kid: str) -> AESGCM:
        name, _, v = kid.rpartition(":v")
        if name != self.name or int(v) not in self.versions:
            raise UnknownKey(f"no KEK for {kid}")
        return AESGCM(self.versions[int(v)])


def wrap(ring: Keyring, dek: bytes):
    kid, n = ring.kid(ring.primary), os.urandom(12)
    return kid, b64(n + ring.kek(kid).encrypt(n, dek, kid.encode()))  # AAD = kid: a wrapped DEK cannot be relabelled


def unwrap(ring: Keyring, kid: str, wdek: str) -> bytes:
    raw = base64.b64decode(wdek)
    return ring.kek(kid).decrypt(raw[:12], raw[12:], kid.encode())


def seal(ring: Keyring, plaintext: bytes, context: str) -> dict:
    dek, n = AESGCM.generate_key(bit_length=256), os.urandom(12)  # fresh DEK per record
    kid, wdek = wrap(ring, dek)
    ct = AESGCM(dek).encrypt(n, plaintext, context.encode())  # data encrypted once, with the DEK
    return {"kid": kid, "wdek": wdek, "n": b64(n), "ct": b64(ct), "ctx": context}


def open_(ring: Keyring, rec: dict) -> bytes:
    dek = unwrap(ring, rec["kid"], rec["wdek"])
    return AESGCM(dek).decrypt(base64.b64decode(rec["n"]), base64.b64decode(rec["ct"]), rec["ctx"].encode())


def rewrap(ring: Keyring, rec: dict) -> dict:
    kid, wdek = wrap(ring, unwrap(ring, rec["kid"], rec["wdek"]))  # only the 32-byte DEK is re-encrypted
    return {**rec, "kid": kid, "wdek": wdek}  # n and ct are untouched


def count_by_kid(store: dict) -> dict:
    kids = [rec["kid"] for rec in store.values()]
    return {k: kids.count(k) for k in sorted(set(kids))}


def rewrap_job(ring: Keyring, store: dict, log=print, crash_after=None) -> int:
    target, done = ring.kid(ring.primary), 0
    for rid, rec in store.items():
        if rec["kid"] == target:  # idempotent: records already on the primary are skipped, so a rerun resumes
            continue
        if crash_after is not None and done == crash_after:
            raise RuntimeError(f"rewrap job crashed after {done} records")  # injected fault
        store[rid] = rewrap(ring, rec)
        done += 1
        log(json.dumps({"event": "rewrap", "id": rid, "from": rec["kid"], "to": target}))
    log(json.dumps({"metric": "records_by_kid", **count_by_kid(store)}))  # observability: who still needs which KEK
    return done


def retire(ring: Keyring, store: dict, version: int) -> None:
    del ring.versions[version]  # BUG on purpose: never asks whether a record still uses this version


def try_all(ring, store) -> str:
    bad = {}
    for rid, rec in store.items():
        try:
            open_(ring, rec)
        except UnknownKey as e:
            bad[rid] = str(e)
    return f"{len(store) - len(bad)}/{len(store)} decrypt" + (f"; LOST {list(bad)} ({set(bad.values())})" if bad else "")


if __name__ == "__main__":
    rng = random.Random(SEED)
    ring = Keyring()
    store = {f"order-{i}": seal(ring, f"card=4111-{rng.randrange(1000, 9999)}".encode(), f"order-{i}") for i in range(1, 7)}
    print("sealed 6 records with", ring.kid(1), "| header:", {k: store["order-1"][k] for k in ("kid", "ctx")})
    print("rotate ->", ring.rotate(), "| old records still:", try_all(ring, store))
    before = store["order-1"]["ct"]
    rewrap_job(ring, store)
    print("data ciphertext unchanged by rewrap:", store["order-1"]["ct"] == before)
    retire(ring, store, 1)
    print("retire v1 after a full rewrap:", try_all(ring, store))

    print("--- fault: rotate again, the rewrap job crashes, the operator deletes v2 anyway")
    print("rotate ->", ring.rotate())
    try:
        rewrap_job(ring, store, crash_after=rng.randrange(1, 5))  # seeded crash point
    except RuntimeError as e:
        print("job:", e, "| counts:", count_by_kid(store))
    retire(ring, store, 2)
    print("after retire v2:", try_all(ring, store))
