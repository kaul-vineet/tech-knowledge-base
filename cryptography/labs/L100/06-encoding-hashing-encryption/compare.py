"""Side-by-side: encoding (base64/hex) vs hashing (SHA-256) vs encryption (AES-256-GCM)."""
import base64
import hashlib
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SECRET = b"db_password=Sup3rS3cret"


def encode(data: bytes) -> dict:
    return {"base64": base64.b64encode(data).decode(), "hex": data.hex()}  # encoding: new alphabet, no key, no secrecy


def hash_(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()  # hashing: deterministic, one-way


def encrypt(data: bytes, key: bytes) -> bytes:
    nonce = os.urandom(12)  # encryption: key + fresh nonce -> randomised, reversible only with the key
    return nonce + AESGCM(key).encrypt(nonce, data, None)


def decrypt(blob: bytes, key: bytes) -> bytes:
    return AESGCM(key).decrypt(blob[:12], blob[12:], None)


if __name__ == "__main__":
    key = AESGCM.generate_key(bit_length=256)
    enc = encode(SECRET)
    blob = encrypt(SECRET, key)
    rows = [
        ("encoding/base64", enc["base64"], "none",
         "yes, by anyone" if base64.b64decode(enc["base64"]) == SECRET else "?"),
        ("encoding/hex", enc["hex"], "none", "yes, by anyone" if bytes.fromhex(enc["hex"]) == SECRET else "?"),
        ("hash/SHA-256", hash_(SECRET), "none", "no (one-way)"),
        ("encrypt/AES-GCM", base64.b64encode(blob).decode(), "secret",
         "only with key" if decrypt(blob, key) == SECRET else "?"),
    ]
    print(f"{'technique':16} {'key':7} {'reversible?':15} output (truncated)")
    for name, out, k, rev in rows:
        print(f"{name:16} {k:7} {rev:15} {out[:44]}")

    try:
        decrypt(blob, AESGCM.generate_key(bit_length=256))
    except InvalidTag:
        print("decrypt with wrong key -> InvalidTag")
    print("hash is deterministic  ->", hash_(SECRET) == hash_(SECRET))
    print("encryption randomised  ->", encrypt(SECRET, key) != encrypt(SECRET, key))
    print("RFC 4648 vectors       ->", base64.b64encode(b"foobar") == b"Zm9vYmFy",
          base64.b16encode(b"foobar") == b"666F6F626172")
    print("Common mistakes:")
    print(" - 'encrypting' with base64 in config files / HTTP Basic auth without TLS")
    print(" - storing passwords with SHA-256 or encryption instead of Argon2id")
    print(" - using a hash where a keyed MAC (HMAC) or AEAD is needed")
