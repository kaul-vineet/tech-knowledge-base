"""Crypto side of project 01 (helper for pqmsg.py): hybrid X25519+ML-KEM-768 welcomes, epoch secrets, the versioned
message envelope and the reader contract. Reused, not copied:
  cryptography L400 #18 pq_hybrid + solution_strict  - key package, encapsulation, strict share-length check
  cryptography L400 #17 registry + agile_envelope    - AEAD by identifier, canonical header bytes as AAD
  cryptography L400 #20 group_keys.kdf               - HKDF labels for epoch-derived keys
  application-architecture L300 #14 contract.like    - the reader's contract (field + type matchers)"""
import base64
import contextlib
import hashlib
import hmac
import io
import os

from _kb import load

pq = load("pq", "pq_hybrid")
strict = load("pq", "solution_strict")
reg = load("agility", "registry")
agile = load("agility", "agile_envelope")
kdf = load("group", "group_keys").kdf
contract = load("contract", "contract")

KEK_AEAD = "A256GCM"  # wraps the epoch secret inside a welcome
SUITES = {2: "A256GCM", 3: "C20P1305"}  # envelope version -> AEAD id (v3 = the agility drill: a cipher swap)
LEGACY_V1_AEAD = reg.LEGACY_V1_AEAD  # v1 history carried no identifier
like = contract.like
READER_CONTRACT = {"v": like(2), "aead": like("A256GCM"), "epoch": like(1), "sender": like("alice"),
                   "ikey": like("0b9c..."), "n": like("base64 nonce")}


class EnvelopeError(Exception):
    """Unknown envelope version: refuse, never guess (no silent fallback)."""


def b64e(b: bytes) -> str:
    return base64.b64encode(b).decode()


def b64d(s: str) -> bytes:
    return base64.b64decode(s)


def _welcome_aad(epoch: int, name: str) -> bytes:
    return agile.canon({"epoch": epoch, "to": name, "kem": pq.GROUP})


class Device:
    """A member device (or the service sealer identity): one hybrid key package, epoch secrets learned from the log."""

    def __init__(self, name: str):
        self.name = name
        self.st, self.key_package = pq.client_hello()  # 1,184 B ML-KEM-768 + 32 B X25519 = 1,216 B
        self.keys = {}

    def fork(self) -> "Device":
        """Same identity (key package), empty key cache: a restarted node or a fresh install replaying the log."""
        d = Device.__new__(Device)
        d.name, d.st, d.key_package, d.keys = self.name, self.st, self.key_package, {}
        return d

    def learn(self, entry: dict):
        w = entry["welcomes"].get(self.name)
        if w is None or entry["epoch"] in self.keys:
            return self.keys.get(entry["epoch"])
        with contextlib.redirect_stdout(io.StringIO()):  # solution_strict logs handshake_abort JSON before raising
            k, _ = strict.client_finish(self.st, b64d(w["kem_ct"]))  # exact length or HandshakeError
        self.keys[entry["epoch"]] = reg.aead(KEK_AEAD, k).decrypt(b64d(w["n"]), b64d(w["wrapped"]),
                                                                  _welcome_aad(entry["epoch"], self.name))
        return self.keys[entry["epoch"]]


def welcome(key_package: bytes, epoch_secret: bytes, epoch: int, name: str) -> dict:
    kem_ct, k = pq.server_respond(key_package)  # 1,088 B ML-KEM ciphertext + 32 B X25519 share = 1,120 B
    n = os.urandom(12)  # one encryption per fresh hybrid key: a random nonce is trivially unique here
    return {"kem_ct": b64e(kem_ct), "n": b64e(n),
            "wrapped": b64e(reg.aead(KEK_AEAD, k, for_new_data=True).encrypt(n, epoch_secret, _welcome_aad(epoch, name)))}


def welcome_bytes(w: dict) -> int:
    return sum(len(b64d(w[k])) for k in ("kem_ct", "n", "wrapped"))  # raw bytes on the wire


def fingerprint(epoch_secret: bytes, sender: str, text: str) -> str:
    """Keyed payload fingerprint for idempotency checks: the log never holds a plain hash of a plaintext."""
    return hmac.new(kdf(epoch_secret, b"fp"), f"{sender}\x00{text}".encode(), hashlib.sha256).hexdigest()[:32]


def seal(epoch_secret: bytes, epoch: int, sender: str, ikey: str, text: str, nonce: bytes, version: int = 2) -> dict:
    if version == 1:  # legacy writer (history only): no algorithm id, header not authenticated
        h = {"v": 1, "epoch": epoch, "sender": sender, "ikey": ikey, "n": b64e(nonce)}
        ct = reg.aead(LEGACY_V1_AEAD, kdf(epoch_secret, b"app")).encrypt(nonce, text.encode(), b"")
    else:
        h = {"v": version, "aead": SUITES[version], "kem": pq.GROUP, "epoch": epoch, "sender": sender, "ikey": ikey,
             "n": b64e(nonce)}
        ct = reg.aead(h["aead"], kdf(epoch_secret, b"app"), for_new_data=True).encrypt(nonce, text.encode(), agile.canon(h))
    return {"type": "msg", "h": h, "ct": b64e(ct), "fp": fingerprint(epoch_secret, sender, text)}


def open_msg(keys: dict, entry: dict):
    """Plaintext, or None when this reader holds no key for the entry's epoch (removed / not yet joined)."""
    h = entry["h"]
    if h.get("v") == 1:
        alg, aad = LEGACY_V1_AEAD, b""
    elif h.get("v") in SUITES:
        alg, aad = h["aead"], agile.canon(h)  # the whole header is AAD: relabelling breaks the tag
    else:
        raise EnvelopeError(f"unknown envelope version {h.get('v')!r}")
    if h["epoch"] not in keys:
        return None
    return reg.aead(alg, kdf(keys[h["epoch"]], b"app")).decrypt(b64d(h["n"]), b64d(entry["ct"]), aad).decode()


def contract_problems(header: dict, accepted_versions) -> list:
    """Consumer-driven check of a writer's header against READER_CONTRACT plus the versions the log accepts."""
    rules, problems = {}, []
    example = contract._example(READER_CONTRACT, rules)
    for path in rules:
        field = path[2:]
        if field not in header:
            problems.append(f"missing {field}")
        elif type(header[field]) is not type(example[field]):
            problems.append(f"{field}: {type(header[field]).__name__}, contract says {type(example[field]).__name__}")
    if header.get("v") not in accepted_versions:
        problems.append(f"version {header.get('v')} not accepted by the log (accepts {sorted(accepted_versions)})")
    return problems
