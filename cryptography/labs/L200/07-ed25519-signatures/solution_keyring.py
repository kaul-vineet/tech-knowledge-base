"""Build-task solution: verify a release against a KEYRING (several trusted public keys, e.g. during key rotation)."""
import hashlib
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def key_id(pub: Ed25519PublicKey) -> str:
    return hashlib.sha256(pub.public_bytes_raw()).hexdigest()[:16]  # short fingerprint of the raw 32-byte key


def verify_with_keyring(keyring: list, path: Path, sig_path: Path):
    """Return the key_id of the trusted key that made the signature, or None."""
    data, sig = path.read_bytes(), sig_path.read_bytes()
    for pub in keyring:
        try:
            pub.verify(sig, data)
            return key_id(pub)
        except InvalidSignature:
            continue
    return None
