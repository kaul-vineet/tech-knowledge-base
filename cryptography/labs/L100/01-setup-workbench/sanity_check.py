"""Crypto workbench sanity check: versions + one known-answer test per building block."""
import hashlib
import platform
import secrets
import sys

import cryptography
from cryptography.hazmat.backends.openssl import backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PINNED = "50.0.2"  # version pinning: keep in sync with ../../../requirements.txt
# NIST FIPS 180 example: SHA-256("abc")
NIST_ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def argon2id_available() -> bool:
    try:
        from cryptography.hazmat.primitives.kdf.argon2 import Argon2id  # noqa: F401
    except ImportError:
        return False
    # backend feature check: needs OpenSSL >= 3.2 under the hood; a tiny derive proves it works.
    try:
        Argon2id(salt=b"0" * 16, length=32, iterations=1, lanes=1, memory_cost=8).derive(b"x")
        return True
    except Exception:
        return False


def run_checks() -> dict:
    key = AESGCM.generate_key(bit_length=256)
    nonce = secrets.token_bytes(12)
    ct = AESGCM(key).encrypt(nonce, b"hello", None)
    return {
        "python": platform.python_version(),
        "machine": f"{platform.system()} {platform.machine()}",  # e.g. Darwin arm64 / Windows AMD64
        "cryptography": cryptography.__version__,
        "cryptography_pinned": cryptography.__version__ == PINNED,
        "openssl": backend.openssl_version_text(),  # bundled engine, not the system openssl CLI
        "sha256_known_answer": hashlib.sha256(b"abc").hexdigest() == NIST_ABC,  # KAT: published in == published out
        "secrets_token_len": len(secrets.token_bytes(32)),
        "aesgcm_roundtrip": AESGCM(key).decrypt(nonce, ct, None) == b"hello",
        "argon2id_available": argon2id_available(),
    }


if __name__ == "__main__":
    results = run_checks()
    for name, value in results.items():
        print(f"{name:22} {value}")
    ok = all(v for k, v in results.items() if isinstance(v, bool))
    print("WORKBENCH OK" if ok else "WORKBENCH NOT READY")
    sys.exit(0 if ok else 1)
