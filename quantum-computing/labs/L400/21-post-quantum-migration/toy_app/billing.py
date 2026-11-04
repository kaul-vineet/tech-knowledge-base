"""Card tokens are encrypted to the payment partner's RSA key (RSA-OAEP) and archived for 10 years."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


def partner_keypair():
    return rsa.generate_private_key(public_exponent=65537, key_size=3072)


def encrypt_token(partner_public, token):
    return partner_public.encrypt(token, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
