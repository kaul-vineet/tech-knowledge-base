"""Algorithm registry: the ONLY module that names concrete algorithms (fitness function: agility_lint.py).
Every other module asks for an algorithm by its identifier ("A256GCM", "ML-DSA-65") and lets the registry
and the policy decide. Swapping AES-GCM for ChaCha20-Poly1305 or Ed25519 for ML-DSA is a registry/policy change."""
import os
from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519, mldsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305


class UnknownAlgorithm(Exception):
    """The identifier is not in the registry (or names the wrong kind of algorithm)."""


class DisallowedAlgorithm(Exception):
    """The identifier is known but policy forbids this use (deprecated for new data, or disallowed)."""


@dataclass
class Alg:
    id: str
    kind: str  # "aead" or "sig"
    status: str  # "active" -> any use; "deprecated" -> read/verify only; "disallowed" -> refuse
    impl: object
    key_len: int = 0
    pq: bool = False  # believed secure against a quantum attacker (FIPS 204 for ML-DSA)


REGISTRY = {a.id: a for a in [
    Alg("A256GCM", "aead", "active", AESGCM, 32),
    Alg("C20P1305", "aead", "active", ChaCha20Poly1305, 32),
    Alg("Ed25519", "sig", "active", ed25519.Ed25519PrivateKey),
    Alg("ML-DSA-65", "sig", "active", mldsa.MLDSA65PrivateKey, pq=True),
]}

# Which signature algorithms a verifier REQUIRES in each migration phase (dual-signing = "transition").
PHASES = {"classic": ["Ed25519"], "transition": ["Ed25519", "ML-DSA-65"], "pq-only": ["ML-DSA-65"]}
POLICY = {"aead_default": "A256GCM", "aead_prefs": ["A256GCM", "C20P1305"], "phase": "transition"}
LEGACY_V1_AEAD = "A256GCM"  # v1 envelopes carried no identifier: the format version implied the cipher


def get(alg_id: str, kind: str, for_new_data: bool = False) -> Alg:
    a = REGISTRY.get(alg_id)
    if a is None or a.kind != kind:
        raise UnknownAlgorithm(f"{alg_id!r} is not a registered {kind}")
    if a.status == "disallowed" or (for_new_data and a.status != "active"):
        raise DisallowedAlgorithm(f"{alg_id} is {a.status}")
    return a


def required_signatures() -> list:
    return list(PHASES[POLICY["phase"]])


def signing_algorithms() -> list:
    return [s for s in required_signatures() if get(s, "sig").status == "active"]


def new_aead_key(alg_id: str) -> bytes:
    return os.urandom(get(alg_id, "aead", for_new_data=True).key_len)


def aead(alg_id: str, key: bytes, for_new_data: bool = False):
    return get(alg_id, "aead", for_new_data).impl(key)


def new_signer(alg_id: str):
    return get(alg_id, "sig", for_new_data=True).impl.generate()


def sign(alg_id: str, private_key, data: bytes) -> bytes:
    get(alg_id, "sig", for_new_data=True)
    return private_key.sign(data)


def verify(alg_id: str, public_key, signature: bytes, data: bytes) -> bool:
    get(alg_id, "sig")  # raises for unknown or disallowed algorithms
    try:
        public_key.verify(signature, data)
        return True
    except InvalidSignature:
        return False
