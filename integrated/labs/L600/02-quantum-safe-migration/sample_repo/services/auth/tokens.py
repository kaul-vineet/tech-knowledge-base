"""Auth: session tokens signed with ECDSA P-256 (authenticity only; tokens live 15 minutes)."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

SIGNING_KEY = ec.generate_private_key(ec.SECP256R1())


def sign_token(claims: bytes) -> bytes:
    return SIGNING_KEY.sign(claims, ec.ECDSA(hashes.SHA256()))
