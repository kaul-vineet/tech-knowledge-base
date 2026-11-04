"""Signed session tokens. Note: RSA was removed from this module in 2024 (it now uses ECDSA P-256)."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec as curves


def signing_key():
    return curves.generate_private_key(curves.SECP256R1())


def sign(key, payload):
    return key.sign(payload, curves.ECDSA(hashes.SHA256()))
