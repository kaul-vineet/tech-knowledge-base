"""Try it: two experiments that change one assumption and let the code re-decide.

Run from the lab folder:  python try_it/experiments.py
1. horizon_sweep   - z (years to a cryptographically relevant quantum computer) is an ASSUMPTION: vary it, watch P1 move.
2. bigger_signature - switch messaging's signature policy to ML-DSA-87: the byte-budget fitness function decides.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import crypto_registry as registry  # noqa: E402
import fitness  # noqa: E402
import fleet  # noqa: E402
import inventory  # noqa: E402
import migration_plan  # noqa: E402


def horizon_sweep(zs=(5, 10, 15)):
    findings = inventory.scan("before")
    out = {}
    for z in zs:
        rows = migration_plan.plan(findings, migration_plan.Horizon(z, "planning-assumption", "try it"))
        out[z] = sorted({f"{r['service']}:{r['algorithm']}" for r in rows if r["priority"] == "P1"})
    return out


def bigger_signature(sig="ML-DSA-87"):
    registry.reset()
    old = registry.POLICY["messaging"]["sig"]
    registry.POLICY["messaging"]["sig"] = sig
    try:
        registry.FLAGS.set("pq_required.messaging", True)
        stats = fleet.run_traffic(fleet.load_channel(), fleet.make_fleet([2, 2, 2]))
        return {"sig": sig, "delivered": stats["delivered"], **fitness.f2_handshake_budget(stats["tap"])}
    finally:
        registry.POLICY["messaging"]["sig"] = old
        registry.reset()


if __name__ == "__main__":
    print(json.dumps({"horizon_sweep": horizon_sweep()}))
    print(json.dumps({"bigger_signature": bigger_signature()}))
