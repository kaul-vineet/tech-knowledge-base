"""Payments: wrap each card-token archive DEK to the vault's RSA key (key transport = key establishment)."""
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

VAULT_KEY = rsa.generate_private_key(public_exponent=65537, key_size=3072)


def wrap_dek():
    dek = os.urandom(32)
    oaep = padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    return dek, VAULT_KEY.public_key().encrypt(dek, oaep)
