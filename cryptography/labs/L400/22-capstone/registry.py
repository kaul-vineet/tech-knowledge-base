"""Capstone registry: lesson 17's registry (AEADs, signatures, policy phases) plus the KEMs used to SHARE a document
key with an external recipient (HPKE, RFC 9180). Still the only capstone file that names concrete algorithms."""
import importlib.util
from pathlib import Path

from cryptography.hazmat.primitives import hpke
from cryptography.hazmat.primitives.asymmetric import mlkem, x25519

_spec = importlib.util.spec_from_file_location("l17_registry", Path(__file__).resolve().parents[1] / "17-crypto-agility" / "registry.py")
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

Alg, REGISTRY, PHASES, POLICY, LEGACY_V1_AEAD = _base.Alg, _base.REGISTRY, _base.PHASES, _base.POLICY, _base.LEGACY_V1_AEAD
UnknownAlgorithm, DisallowedAlgorithm = _base.UnknownAlgorithm, _base.DisallowedAlgorithm
get, required_signatures, signing_algorithms = _base.get, _base.required_signatures, _base.signing_algorithms
new_aead_key, aead, new_signer, sign, verify = _base.new_aead_key, _base.aead, _base.new_signer, _base.sign, _base.verify

REGISTRY["HPKE-XWING"] = Alg("HPKE-XWING", "kem", "active", hpke.KEM.MLKEM768_X25519, pq=True)  # PQ/T hybrid
REGISTRY["HPKE-X25519"] = Alg("HPKE-X25519", "kem", "deprecated", hpke.KEM.X25519)  # read old shares only
POLICY["share_kem"] = "HPKE-XWING"
POLICY["phase"] = "classic"  # the capstone token signs with Ed25519 only (ML-DSA in the token: pending SoftHSM CI)


def new_recipient(kem_id: str):
    get(kem_id, "kem", for_new_data=True)
    if kem_id == "HPKE-XWING":
        return hpke.MLKEM768X25519PrivateKey(mlkem.MLKEM768PrivateKey.generate(), x25519.X25519PrivateKey.generate())
    return x25519.X25519PrivateKey.generate()


def _suite(kem_id: str, for_new_data: bool):
    return hpke.Suite(get(kem_id, "kem", for_new_data).impl, hpke.KDF.HKDF_SHA256, hpke.AEAD.AES_256_GCM)


def share_seal(kem_id: str, recipient_pub, data: bytes, info: bytes) -> bytes:
    return _suite(kem_id, True).encrypt(data, recipient_pub, info=info)


def share_open(kem_id: str, recipient_priv, blob: bytes, info: bytes) -> bytes:
    return _suite(kem_id, False).decrypt(blob, recipient_priv, info=info)


def share_overhead(kem_id: str) -> int:
    return get(kem_id, "kem").impl.enc_length() + 16  # encapsulated key + AEAD tag
