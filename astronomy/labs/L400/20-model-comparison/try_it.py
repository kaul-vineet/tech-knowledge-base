"""tryIt for lesson 20 (fixed select(): BIC).
1. Generate the data from an NFW halo instead (V200 = 130 km/s, c = 10): does BIC switch models?
2. Keep only the optical part of the curve (R <= 8 kpc, 11 points): can BIC still tell disk from halo?
"""
import importlib.util
from pathlib import Path

import numpy as np

import galaxy as g

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("compare_fixed", HERE / "solution" / "compare.py")
fixed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixed)

if __name__ == "__main__":
    rng = np.random.default_rng(21)
    err = 2.0 + 4.0 * g.R / g.R.max()
    v = np.sqrt(g.v_disk2(g.R, 0.8) + g.v_nfw2(g.R, 130.0, 10.0)) + rng.normal(0, err)
    best, rows = fixed.select(g.R, v, err)
    print("1. NFW truth -> BIC picks", best, {r["model"]: float(r["bic"]) for r in rows})
    v, err = g.observed()
    inner = g.R <= 8.0
    best, rows = fixed.select(g.R[inner], v[inner], err[inner])
    print("2. R <= 8 kpc ->", best, {r["model"]: (float(r["bic"]), r["params"][0]) for r in rows[:2]}, "(bic, mass-to-light)")
