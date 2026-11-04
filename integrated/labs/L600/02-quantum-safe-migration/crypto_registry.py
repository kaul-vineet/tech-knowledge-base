"""The crypto registry: services ask by PURPOSE ("key exchange for messaging"); policy + feature flags pick the adapter.

Flags come from application-architecture L400 #20 (file-based, owned, expiring). Every resolution is appended to AUDIT,
so a runtime seam test can prove that what went on the wire was chosen here - not by code that bypassed the registry.
"""
from datetime import date
from pathlib import Path

import _kb  # noqa: F401
import adapters
from flags import Flags, gate_flags  # noqa: F401  (application-architecture L400 #20)

HERE = Path(__file__).resolve().parent
TODAY = date(2026, 10, 30)                      # fake clock for flag expiry and baseline due dates
KEX = {k.id: k for k in (adapters.X25519Kex(), adapters.X25519MLKEM768Kex())}
SIG = {s.id: s for s in (adapters.Ed25519Sig(), adapters.MLDSA65Sig(), adapters.MLDSA87Sig())}
AEAD = {a.id: a for a in (adapters.Aes256Gcm(),)}
POLICY = {"messaging": {"kex_pq": "X25519MLKEM768", "kex_classic": "X25519", "sig": "ML-DSA-65", "aead": "A256GCM"}}
SERVER_GROUPS = {1: ["X25519"], 2: ["X25519MLKEM768", "X25519"]}     # what each server version can negotiate
FLAGS = Flags(HERE / "flags.json", today=TODAY)
AUDIT = []


def _log(service, kind, alg_id, role="client"):
    AUDIT.append({"service": service, "kind": kind, "id": alg_id, "role": role})


def pq_required(service):
    return FLAGS.enabled(f"pq_required.{service}")


def expected_offers(service):
    """The groups a client of this service must offer right now (no audit entry: used by checks and the scanner)."""
    p, required = POLICY[service], pq_required(service)
    hybrid = required or FLAGS.enabled(f"pq_hybrid_kex.{service}")
    return ([p["kex_pq"]] if hybrid else []) + ([] if required else [p["kex_classic"]])


def kex_offers(service):
    ids = expected_offers(service)
    for i in ids:
        _log(service, "kex", i)
    return [KEX[i] for i in ids]


def classic_fallback(service):
    """Kept for v1 compatibility during the rollout only."""
    _log(service, "kex", POLICY[service]["kex_classic"])
    return KEX[POLICY[service]["kex_classic"]]


def kex(group_id, service, role="client"):
    _log(service, "kex", group_id, role)
    return KEX[group_id]


def signer(service, role="server"):
    _log(service, "sig", POLICY[service]["sig"], role)
    return SIG[POLICY[service]["sig"]]


def verifier(service, alg_id):
    if alg_id != POLICY[service]["sig"]:
        raise KeyError(f"{alg_id} is not the signature policy for {service}")
    _log(service, "sig", alg_id)
    return SIG[alg_id]


def aead(service, role="client"):
    _log(service, "aead", POLICY[service]["aead"], role)
    return AEAD[POLICY[service]["aead"]]


def server_groups(version):
    return list(SERVER_GROUPS[version])


def describe(service, purpose):
    """Static view for the inventory scanner: what a registry call resolves to under the current flags."""
    if purpose == "kex":
        offers = expected_offers(service)
        return {"algorithm": " + ".join(offers) + " (via registry)", "usage": "key-establishment",
                "pq": KEX[offers[0]].pq, "classical_fallback": any(not KEX[o].pq for o in offers)}
    if purpose == "sig":
        sid = POLICY[service]["sig"]
        return {"algorithm": f"{sid} (via registry)", "usage": "signature", "pq": SIG[sid].pq, "classical_fallback": False}
    return {"algorithm": f"{POLICY[service]['aead']} (via registry)", "usage": "symmetric", "pq": False,
            "classical_fallback": False}


def reset():
    AUDIT.clear()
    FLAGS.overrides.clear()
