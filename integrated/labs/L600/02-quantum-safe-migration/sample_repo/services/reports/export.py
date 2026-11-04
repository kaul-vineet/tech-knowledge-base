"""Reports: exports are sealed with AES-256-GCM. (The old RSA export signer was removed in 2024 - no RSA here.)"""
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def seal_export(key: bytes, data: bytes) -> bytes:
    nonce = os.urandom(12)
    return nonce + AESGCM(key).encrypt(nonce, data, b"report-export")
