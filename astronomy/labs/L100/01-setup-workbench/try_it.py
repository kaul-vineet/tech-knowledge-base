"""tryIt experiments for lesson 1 (run: python try_it.py)."""
import numpy as np

import check_env

# 1. Two unseeded generators. Predict: same star field?
a, b = np.random.default_rng().random(3), np.random.default_rng().random(3)
print("unseeded fields equal?", bool(np.all(a == b)))

# 2. Seed 42 vs seed 43. Predict: how different are the first stars?
print("seed 42 first star:", check_env.synthetic_stars(42)[0], "| seed 43 first star:", check_env.synthetic_stars(43)[0])
