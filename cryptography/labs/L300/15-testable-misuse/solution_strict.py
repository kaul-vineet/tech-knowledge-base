"""Build task solution: strict wrappers - exact sizes, canonical encodings, no compatibility shims."""
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from wycheproof_check import L, report, run

TAG, IV, SIG = 16, 12, 64


def aead_open(key: bytes, iv: bytes, ct: bytes, tag: bytes, aad: bytes) -> bytes:
    if len(tag) != TAG or len(iv) != IV:  # the API promises 128-bit tags and 96-bit nonces: enforce it
        raise ValueError(f"need a {TAG}-byte tag and {IV}-byte IV, got {len(tag)}/{len(iv)}")
    return AESGCM(key).decrypt(iv, ct + tag, aad)  # high-level API: no tag-length knob to misuse


def sig_verify(pk: bytes, msg: bytes, sig: bytes) -> bool:
    if len(sig) != SIG:  # exactly one byte string per signature: no trailing data
        return False
    if int.from_bytes(sig[32:], "little") >= L:  # canonical S only (the library checks too: defence in depth)
        return False
    try:
        Ed25519PublicKey.from_public_bytes(pk).verify(sig, msg)
        return True
    except InvalidSignature:
        return False


if __name__ == "__main__":
    report(run(aead_open, sig_verify))
