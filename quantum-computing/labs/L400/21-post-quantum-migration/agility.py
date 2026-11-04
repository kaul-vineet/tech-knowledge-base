"""Crypto agility for lab 21: one KEM interface, algorithms chosen by NAME from a registry, versioned envelopes.

Swapping X25519 -> X25519+ML-KEM-768 is a one-line config change for every caller of establish()/accept().
Hybrid combiner: the two shared secrets are concatenated and fed to HKDF-SHA256 - the generic composite
(Z' = Z || T into a SP 800-56C KDF) that NIST IR 8547 sec. 3.2.1 allows. ML-KEM-768 from cryptography >= 47 (FIPS 203).
"""
import json
import time

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import mlkem, x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


class X25519Kem:
    name = "x25519"

    def keygen(self):
        sk = x25519.X25519PrivateKey.generate()
        return sk, sk.public_key().public_bytes_raw()

    def encaps(self, pk):
        eph = x25519.X25519PrivateKey.generate()
        return eph.exchange(x25519.X25519PublicKey.from_public_bytes(pk)), eph.public_key().public_bytes_raw()

    def decaps(self, sk, ct):
        return sk.exchange(x25519.X25519PublicKey.from_public_bytes(ct))


class MlKem768:
    name = "ml-kem-768"

    def keygen(self):
        sk = mlkem.MLKEM768PrivateKey.generate()
        return sk, sk.public_key().public_bytes_raw()

    def encaps(self, pk):
        return mlkem.MLKEM768PublicKey.from_public_bytes(pk).encapsulate()

    def decaps(self, sk, ct):
        return sk.decapsulate(ct)


class Hybrid:
    def __init__(self, pq, classic):
        self.pq, self.classic, self.name = pq, classic, f"{classic.name}+{pq.name}"

    def keygen(self):
        (s1, p1), (s2, p2) = self.pq.keygen(), self.classic.keygen()
        return (s1, s2, len(p1)), p1 + p2

    def encaps(self, pk):
        cut = len(pk) - 32                                      # X25519 public keys are 32 bytes
        (z1, c1), (z2, c2) = self.pq.encaps(pk[:cut]), self.classic.encaps(pk[cut:])
        return self.combine(z1, z2), c1 + c2

    def decaps(self, sk, ct):
        s1, s2, _ = sk
        return self.combine(self.pq.decaps(s1, ct[:-32]), self.classic.decaps(s2, ct[-32:]))

    def combine(self, z_pq, z_classic):
        return HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=f"{self.name} v1".encode()).derive(z_pq + z_classic)


REGISTRY = {k.name: k for k in (X25519Kem(), MlKem768(), Hybrid(MlKem768(), X25519Kem()))}
CONFIG = {"kem": "x25519+ml-kem-768"}                 # the ONE place the algorithm is chosen


def establish(peer_pk, kem=None):
    """Sender side: returns (shared key, envelope). The envelope names the algorithm, so receivers can follow."""
    k = REGISTRY[kem or CONFIG["kem"]]
    key, ct = k.encaps(peer_pk)
    return key, json.dumps({"v": 1, "kem": k.name, "ct": ct.hex()})


def accept(sk, envelope):
    env = json.loads(envelope)
    return REGISTRY[env["kem"]].decaps(sk, bytes.fromhex(env["ct"]))


def measure(name, rounds=50):
    """Sizes (exact) and local time per keygen+encaps+decaps (illustrative; varies by machine)."""
    k = REGISTRY[name]
    establish(k.keygen()[1], name)                       # warm-up
    t = time.perf_counter()
    for _ in range(rounds):
        sk, pk = k.keygen()
        key, envelope = establish(pk, name)
        assert accept(sk, envelope) == key
    ct = bytes.fromhex(json.loads(envelope)["ct"])
    return {"kem": name, "public_key_bytes": len(pk), "ciphertext_bytes": len(ct),
            "ms_per_exchange": round((time.perf_counter() - t) / rounds * 1000, 3)}
