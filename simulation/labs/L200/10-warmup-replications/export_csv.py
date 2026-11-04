"""Write per-replication mean waits for two scenarios to replications.csv (Orange Box Plot, JupyterLab, Superset).

Scenario A deletes nothing, scenario B deletes the warm-up the lab proposes (169): same 40 short runs as warmup.py step 2.
python export_csv.py
"""
import csv
from pathlib import Path

import numpy as np

from warmup import waits

OUT = Path(__file__).with_name("replications.csv")
SCENARIOS = {"delete 0": 0, "delete 169": 169}


def export(path=OUT):
    runs = [waits(1_000, seed) for seed in range(101, 141)]  # identical seeds to warmup.py step 2
    rows = [(name, i + 1, float(r[cut:].mean())) for name, cut in SCENARIOS.items() for i, r in enumerate(runs)]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scenario", "replication", "mean_wait_min"])
        w.writerows((s, i, f"{m:.6f}") for s, i, m in rows)
    return rows


if __name__ == "__main__":
    rows = export()
    print(f"wrote {len(rows)} rows to {OUT.name}")
    for name in SCENARIOS:
        means = [m for s, _, m in rows if s == name]
        print(f"{name:>10}: mean of 40 replication means {np.mean(means):.2f} min (true 4.0)")
