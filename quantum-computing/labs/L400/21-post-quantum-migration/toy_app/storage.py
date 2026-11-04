"""At-rest encryption with AES-256-GCM and integrity hashes with SHA-256 (symmetric: not broken by Shor)."""
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt_blob(key, blob):
    nonce = os.urandom(12)
    return nonce + AESGCM(key).encrypt(nonce, blob, None), hashlib.sha256(blob).hexdigest()
