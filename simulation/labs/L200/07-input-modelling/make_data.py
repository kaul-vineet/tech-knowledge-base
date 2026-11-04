"""Writes service_times.csv: 200 SYNTHETIC service times (minutes) at a bike-repair desk.

Stands in for a measured sample (no openly licensed one was selected; see KNOWN-GAPS). The "true" process is
lognormal so we can check whether the fitting code finds it. Values are rounded to 0.01 min like a stopwatch log.
python make_data.py   (only needed to regenerate the committed CSV)
"""
from pathlib import Path

import numpy as np

OUT = Path(__file__).with_name("service_times.csv")


def make(seed=2026, n=200):
    rng = np.random.default_rng(seed)
    return np.round(rng.lognormal(mean=1.3, sigma=0.6, size=n), 2)


if __name__ == "__main__":
    rows = "\n".join(f"{v:.2f}" for v in make())
    OUT.write_text("minutes\n" + rows + "\n", encoding="utf-8")
    print(f"wrote {OUT.name}")
