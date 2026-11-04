"""Session keys with a partner API: X25519 key agreement -> HKDF -> AES-256-GCM."""
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def session_key(peer_public):
    mine = x25519.X25519PrivateKey.generate()
    shared = mine.exchange(peer_public)
    key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"api v1").derive(shared)
    return mine.public_key(), key


def seal(key, message):
    nonce = os.urandom(12)
    return nonce + AESGCM(key).encrypt(nonce, message, b"api v1")
