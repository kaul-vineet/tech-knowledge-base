"""Writes the two versions of the input (SYNTHETIC variable-star light curve, seeded): data/lightcurve_v1.csv, _v2.csv.

Truth: period 0.3011 d (an RRc-like pulsator), 300 irregular samples over 30 nights from two telescopes.
v1 (as first delivered): telescope B wrote JD - 2460000 instead of MJD - 60000 (MJD = JD - 2400000.5), so its
times are 0.5 d late - the classic JD/MJD half-day mix-up. v2 (corrected release): both in MJD - 60000.
python make_data.py   (rewrites the same bytes every time)
"""
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PERIOD, SEED = 0.3011, 16


def light_curve(seed=SEED):
    rng = np.random.default_rng(seed)
    nights = np.repeat(np.arange(30), 10)
    t = nights + 0.55 + rng.uniform(0, 0.35, nights.size)  # ~8.4 h of darkness per night
    tel = np.where(rng.uniform(0, 1, t.size) < 0.5, "A", "B")
    phase = 2 * np.pi * t / PERIOD
    mag = 12.0 + 0.30 * np.sin(phase) + 0.10 * np.sin(2 * phase + 0.7) + rng.normal(0, 0.02, t.size)
    return np.sort(t), tel[np.argsort(t)], mag[np.argsort(t)]


def write(path, t, tel, mag):
    lines = ["time_mjd_minus_60000,telescope,mag"] + [f"{a:.6f},{b},{c:.4f}" for a, b, c in zip(t, tel, mag)]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    t, tel, mag = light_curve()
    write(HERE / "data" / "lightcurve_v2.csv", t, tel, mag)
    write(HERE / "data" / "lightcurve_v1.csv", np.where(tel == "B", t + 0.5, t), tel, mag)
    print("wrote data/lightcurve_v1.csv and data/lightcurve_v2.csv,", t.size, "rows each")
