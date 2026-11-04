"""Seeded SYNTHETIC 'TESS-like' light curves for the capstone: 12 stars, 27 days at 10-minute cadence with a
1-day mid-sector gap. Writes data/S01.csv ... data/S12.csv (time_d, flux, flux_err) and data/truth.json.
truth.json is for SCORING only (run_capstone.py, tests) - the pipeline never reads it.
python make_data.py   (same bytes every time; run_capstone.py calls it if data/ is missing)
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "L300" / "15-honest-uncertainty"))
import transit_fit as tf  # noqa: E402  (lesson 15's trapezoid model, times in hours)

T = np.arange(0.0, 27.0, 10 / 1440)
T = T[(T < 13.0) | (T >= 14.0)]  # data downlink gap
STARS = {  # kind, params (period d, t0 d, depth, T14 h, T12 h), noise ppm
    "S01": ("planet", (3.1234, 1.20, 0.0080, 2.6, 0.30), 600),
    "S02": ("planet", (7.4120, 2.70, 0.0030, 3.4, 0.35), 500),
    "S03": ("planet", (12.3510, 5.10, 0.0050, 4.2, 0.45), 700),
    "S04": ("eb_secondary", (2.8460, 0.90, 0.0200, 3.0, 0.60), 800),
    "S05": ("eb_odd_even", (4.8000, 1.70, 0.0120, 3.2, 0.60), 700),
    "S06": ("rotator", (4.5000, 0.00, 0.0080, 0, 0), 600),
    "S07": ("ramp", (0, 0, 0.0020, 0, 0), 500),
    "S08": ("quiet", None, 400), "S09": ("quiet", None, 600), "S10": ("quiet", None, 800),
    "S11": ("quiet", None, 1000), "S12": ("quiet", None, 500),
}


def transits(t, period, t0, depth, t14, t12):
    phase_h = ((t - t0 + period / 2) % period - period / 2) * 24.0
    return tf.model((0.0, depth, t14, t12), phase_h) - 1.0


def flux(name, seed=22):
    kind, p, noise = STARS[name]
    rng = np.random.default_rng(seed + int(name[1:]))
    f = 1.0 + rng.normal(0, noise * 1e-6, T.size)
    f *= 1 + 0.0015 * np.sin(2 * np.pi * T / 11.0)  # slow instrumental drift
    if kind == "planet":
        f += transits(T, *p)
    elif kind == "eb_secondary":
        f += transits(T, *p) + transits(T, p[0], p[1] + p[0] / 2, 0.006, p[3], p[4])
    elif kind == "eb_odd_even":  # true period 2P: alternate eclipses 1.2% and 0.6% deep
        f += transits(T, 2 * p[0], p[1], p[2], p[3], p[4]) + transits(T, 2 * p[0], p[1] + p[0], 0.006, p[3], p[4])
    elif kind == "rotator":
        f += p[2] * np.sin(2 * np.pi * T / p[0]) + 0.3 * p[2] * np.sin(4 * np.pi * T / p[0] + 1.0)
    elif kind == "ramp":
        after = T >= 14.0
        f[after] -= p[2] * np.exp(-(T[after] - 14.0) / 0.5)
    return f, np.full(T.size, noise * 1e-6)


def write(folder=HERE / "data"):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    truth = {}
    for name, (kind, p, noise) in STARS.items():
        f, e = flux(name)
        lines = ["time_d,flux,flux_err"] + [f"{a:.6f},{b:.7f},{c:.7f}" for a, b, c in zip(T, f, e)]
        (folder / f"{name}.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
        truth[name] = {"kind": kind, "period_d": p[0] if p and kind != "rotator" and kind != "ramp" else None,
                       "depth": p[2] if kind == "planet" else None, "noise_ppm": noise}
    (folder / "truth.json").write_text(json.dumps(truth, indent=1) + "\n", encoding="utf-8")
    return folder


if __name__ == "__main__":
    print("wrote", write(), len(T), "points per star")
