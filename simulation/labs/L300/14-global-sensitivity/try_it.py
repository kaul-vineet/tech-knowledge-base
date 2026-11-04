"""tryIt experiments for lesson 14 (run: python try_it.py)."""
import numpy as np

import sensitivity as sa

# 1. Move the OAT nominal point: outdoor 26 C instead of 22 C. Predict: does OAT now 'see' the window?
sa.NOMINAL[0] = 26.0
print(f"OAT swings at outdoor=26 C: " + ", ".join(f"{n} {s:.1f}" for n, s in zip(sa.NAMES, sa.oat())))
sa.NOMINAL[0] = 22.0

# 2. Remove the interaction (window term 24*w*dT -> 12*dT, same average effect). Predict: S1 vs ST?
additive = lambda x: 150 + 16 * (x[:, 0] - 22) + 1.0 * (x[:, 1] - 40) + 3 * (x[:, 3] - 8)
s1, st = sa.sobol(f=additive)
print("additive model: " + ", ".join(f"{n} S1 {a:.3f} ST {b:.3f}" for n, a, b in zip(sa.NAMES, s1, st))
      + f"; sum S1 = {s1.sum():.3f}")
