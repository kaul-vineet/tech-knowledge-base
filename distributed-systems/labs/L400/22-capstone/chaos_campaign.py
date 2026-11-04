"""Capstone chaos campaign: every fault from the earlier lessons, alone and all at once, on 3 seeds. Order-level
faults hit a stable 10% cohort (lab 20's harness.cohort, ADR-020); infrastructure faults hit the whole run. The
hypothesis is the same for every experiment: all eight correctness checks in checks.py keep holding."""
from checks import evaluate
from pipeline import N_ORDERS, Pipeline
from reuse import SAGA, load

HARNESS = load("L400/20-chaos-engineering/harness.py", "cap_harness")
ORDER_FAULTS = ("shipping-outage", "crash-after-charge")
INFRA_FAULTS = ("relay-crash", "bus-duplicates", "lost-acks", "burst", "raft-leader-crash")
EXPERIMENTS = {"baseline": (), **{f: (f,) for f in ORDER_FAULTS + INFRA_FAULTS}, "everything": ORDER_FAULTS + INFRA_FAULTS}
SEEDS, BLAST_PCT = (22, 23, 24), 10.0


def experiment(name, seed):
    faults = EXPERIMENTS[name]
    cohort = HARNESS.cohort([f"o{i}" for i in range(1, N_ORDERS + 1)], BLAST_PCT, f"{name}-{seed}")
    p = Pipeline(seed, faults, frozenset(cohort)).run()
    results = evaluate(p)
    bad_orders = {line.split(":")[0] for line in SAGA.audit(p.orders, p.payments, p.shipping)}
    compensated = sum(r["step"] == "saga" and r["status"] == "compensated" for r in p.log.entries())
    return {"experiment": name, "seed": seed, "faults": list(faults), "hypothesis": "all 8 checks hold",
            "held": all(ok for ok, _ in results.values()), "failed": [k for k, (ok, _) in results.items() if not ok],
            "blast_radius_pct": round(100 * len(cohort) / N_ORDERS, 1) if set(faults) & set(ORDER_FAULTS) else None,
            "harmed_orders": len(bad_orders), "compensated": compensated, "ticks": p.t,
            "duplicates_absorbed": sum(c.duplicates for c in p.bus.subscribers)}, results


def campaign():
    return [experiment(name, seed) for name in EXPERIMENTS for seed in SEEDS]
