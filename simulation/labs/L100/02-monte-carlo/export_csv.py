"""Write the lab's 100,000 seeded project totals to mc_totals.csv for a no-code tool (KNIME, marimo, Orange).

python export_csv.py   -> mc_totals.csv; the tool's P50 / P90 should match the lab's printed values.
"""
import csv
from pathlib import Path

import numpy as np

from monte_carlo import sample_totals

OUT = Path(__file__).with_name("mc_totals.csv")


def export(path=OUT, n=100_000, seed=42):
    totals = sample_totals(n, seed)  # same seed and N as monte_carlo.py -> same samples
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["total_days"])
        w.writerows([f"{t:.6f}"] for t in totals)
    return totals


if __name__ == "__main__":
    totals = export()
    print(f"wrote {len(totals)} rows to {OUT.name}")
    print("P50 / P90 completion (days):", np.round(np.percentile(totals, [50, 90]), 2))
