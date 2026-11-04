"""Messaging v1 (before migration): X25519 key agreement, Ed25519-signed server share, AES-GCM payloads.
Patient messages must stay confidential for 12 years."""
from cryptography.hazmat.primitives.asymmetric import ed25519, x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SERVER_SIGNER = ed25519.Ed25519PrivateKey.generate()


def server_share():
    key = x25519.X25519PrivateKey.generate()
    pub = key.public_key().public_bytes_raw()
    return key, pub, SERVER_SIGNER.sign(pub)


def seal(key: bytes, nonce: bytes, message: bytes) -> bytes:
    return AESGCM(key).encrypt(nonce, message, None)
