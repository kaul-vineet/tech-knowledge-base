"""buildTask solution (lesson 11): add the FILL RATE (share of demand served from stock) and compare it with CRN.

python solution/fill_rate.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import inventory as inv  # noqa: E402


def simulate(s, S, demand, lead):
    r = inv.simulate(s, S, demand, lead)
    r["fill_rate"] = 1 - r["lost"] / int(np.sum(demand))  # NEW: units served / units demanded
    return r


def compare_fill(a, b, reps=30):
    diffs = []
    for rep in range(reps):
        d, lead = inv.streams(rep)  # CRN: the same weather, demand and lead times for both policies
        diffs.append(simulate(*b, d, lead)["fill_rate"] - simulate(*a, d, lead)["fill_rate"])
    return inv.ci(diffs)


if __name__ == "__main__":
    for pol in ((20, 80), (30, 80), (30, 90)):
        m, h = inv.ci([simulate(*pol, *inv.streams(r))["fill_rate"] for r in range(30)])
        print(f"s={pol[0]} S={pol[1]}: fill rate {m:.3f} +/- {h:.3f}")
    m, h = compare_fill((30, 80), (30, 90))
    print(f"fill rate S=90 minus S=80 (CRN): {m:+.4f} +/- {h:.4f}")
