"""tryIt experiments for lesson 1 (run: python try_it.py)."""
import random

import numpy as np

# 1. No seed: two generators give different numbers.
print("unseeded equal?", np.random.default_rng().random() == np.random.default_rng().random())

# 2. Python's random and numpy with the SAME seed are different generators (Mersenne Twister vs PCG64).
print("random.Random(42):", round(random.Random(42).random(), 6), "| numpy default_rng(42):", round(float(np.random.default_rng(42).random()), 6))
