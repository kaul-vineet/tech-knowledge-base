"""Try it (run from the lab folder): python try_it/try_it.py

1. Lease length: 10 s (default) vs 20 s. Predict lease expiries, rejected commits and p95 queue time.
2. Scheduler policy: floor+budget (ADR 0002) vs best-fidelity vs fastest. Predict p95 queue time and floor misses.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import jobservice  # noqa: E402
import loadtest  # noqa: E402

KEYS = ("lease_expiries", "rejected_commits", "attempts", "p95_queue_s", "shots_exact", "mean_est_fidelity", "below_floor",
        "per_backend")


def lease(seconds):
    old, jobservice.LEASE_S = jobservice.LEASE_S, seconds
    try:
        return {"lease_s": seconds, **{k: loadtest.run()[k] for k in KEYS[:5]}}
    finally:
        jobservice.LEASE_S = old


def policy(name):
    m = loadtest.run(policy=name)
    return {"policy": name, **{k: m[k] for k in ("p95_queue_s", "mean_est_fidelity", "below_floor", "per_backend")}}


if __name__ == "__main__":
    for s in (10.0, 20.0):
        print(json.dumps(lease(s)))
    for p in ("floor+budget", "best-fidelity", "fastest"):
        print(json.dumps(policy(p)))
