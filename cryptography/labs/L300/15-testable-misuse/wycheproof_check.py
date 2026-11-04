"""Run Project Wycheproof-format vectors against OUR wrappers (the code we wrote around pyca/cryptography).
The library already passes; wrapper conveniences are where bugs hide. The two wrappers below are lenient on purpose."""
import json
from pathlib import Path

from cryptography.exceptions import InvalidSignature, InvalidTag
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

VECTORS = Path(__file__).resolve().parent / "vectors"
L = 2**252 + 27742317777372353535851937790883648493  # Ed25519 group order (RFC 8032)


# ---- wrappers under test: "convenient", i.e. lenient (the fault) ----
def aead_open(key: bytes, iv: bytes, ct: bytes, tag: bytes, aad: bytes) -> bytes:
    """AES-GCM open. BUG: accepts whatever tag length arrives (>= 4 bytes) instead of exactly 16."""
    dec = Cipher(algorithms.AES(key), modes.GCM(iv, tag, min_tag_length=max(4, len(tag)))).decryptor()
    dec.authenticate_additional_data(aad)
    return dec.update(ct) + dec.finalize()  # raises InvalidTag if the (possibly short) tag is wrong


def sig_verify(pk: bytes, msg: bytes, sig: bytes) -> bool:
    """Ed25519 verify. BUG: ignores bytes after 64 and 'fixes' S >= L with a compatibility shim."""
    r, s = sig[:32], int.from_bytes(sig[32:64], "little") % L  # non-canonical S silently reduced
    try:
        Ed25519PublicKey.from_public_bytes(pk).verify(r + s.to_bytes(32, "little"), msg)
        return True
    except InvalidSignature:
        return False


# ---- harness: the same loop works for any Wycheproof file of these types ----
def load(name: str) -> dict:
    return json.loads((VECTORS / name).read_text(encoding="utf-8"))


def aead_cases():
    for g in load("aes_gcm_subset.json")["testGroups"]:
        for t in g["tests"]:
            yield "aes_gcm_subset.json", t
    for t in load("derived_vectors.json")["aead"]:
        yield "derived_vectors.json", t


def eddsa_cases():
    for g in load("ed25519_subset.json")["testGroups"]:
        for t in g["tests"]:
            yield "ed25519_subset.json", {**t, "pk": g["publicKey"]["pk"]}
    pk = load("ed25519_subset.json")["testGroups"][0]["publicKey"]["pk"]  # derived from tcId 1 of that group
    for t in load("derived_vectors.json")["eddsa"]:
        yield "derived_vectors.json", {**t, "pk": pk}


def run(aead_open=aead_open, sig_verify=sig_verify) -> list:
    """Returns one row per test: (file, tcId, flags, expected, got). 'acceptable' would pass either way."""
    rows = []
    for f, t in aead_cases():
        h = {k: bytes.fromhex(t[k]) for k in ("key", "iv", "aad", "msg", "ct", "tag")}
        try:
            got = "valid" if aead_open(h["key"], h["iv"], h["ct"], h["tag"], h["aad"]) == h["msg"] else "wrong plaintext"
        except (InvalidTag, ValueError):  # a strict wrapper may refuse bad sizes with ValueError
            got = "invalid"
        rows.append((f, t["tcId"], t["flags"], t["result"], got))
    for f, t in eddsa_cases():
        ok = sig_verify(bytes.fromhex(t["pk"]), bytes.fromhex(t["msg"]), bytes.fromhex(t["sig"]))
        rows.append((f, t["tcId"], t["flags"], t["result"], "valid" if ok else "invalid"))
    return rows


def failures(rows) -> list:
    return [r for r in rows if r[3] != "acceptable" and r[3] != r[4]]


def report(rows) -> None:
    for f in dict.fromkeys(r[0] for r in rows):
        mine = [r for r in rows if r[0] == f]
        print(f"{f:<22} {len(mine) - len(failures(mine))}/{len(mine)} pass")
    for f, tc, flags, want, got in failures(rows):
        print(f"  FAIL tcId {tc} {flags}: expected {want}, wrapper said {got}")


if __name__ == "__main__":
    report(run())
