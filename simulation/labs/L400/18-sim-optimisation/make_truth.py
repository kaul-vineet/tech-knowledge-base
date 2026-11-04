"""Writes truth.json: every one of the 81 designs simulated 100 times on streams no optimiser uses (50,000+).

This is the referee, not part of any optimiser's budget: it lets the lab score the design each method picks.
python make_truth.py      (about 1-2 minutes; test_optimise.py re-checks three designs)
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parents[1] / "L200" / "11-supply-chain-inventory"))
import inventory  # noqa: E402

S_GRID, Q_GRID, DAYS, REPS, OFFSET = range(10, 55, 5), range(20, 110, 10), 180, 100, 50_000


def true_cost(s, q, reps=REPS):
    c = np.array([inventory.simulate(s, s + q, *inventory.streams(OFFSET + r, DAYS))["cost_per_day"] for r in range(reps)])
    return {"mean": round(float(c.mean()), 4), "se": round(float(c.std(ddof=1)) / math.sqrt(reps), 4)}


if __name__ == "__main__":
    truth = {json.dumps([s, q]): true_cost(s, q) for s in S_GRID for q in Q_GRID}
    (HERE / "truth.json").write_text(json.dumps(truth, indent=0) + "\n", encoding="utf-8")
    best = min(truth, key=lambda k: truth[k]["mean"])
    print(f"wrote {len(truth)} designs; best {best}: {truth[best]}")
