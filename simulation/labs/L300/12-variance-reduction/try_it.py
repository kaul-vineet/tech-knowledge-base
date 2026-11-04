"""tryIt experiments for lesson 12 (run: python try_it.py)."""
import numpy as np

import variance_reduction as vr

n = 20_000
base = vr.plain(n)["var_per_eval"]

# 1. Antithetic sampling on a SYMMETRIC model: y = (sum(u) - 6)^2. Predict: does it still help?
u = np.random.default_rng(1).random((n // 2, vr.N_TASKS))
f = lambda x: (x.sum(axis=1) - vr.N_TASKS / 2) ** 2
a, b = f(u), f(1 - u)
y = f(np.random.default_rng(2).random((n, vr.N_TASKS)))
print(f"symmetric model: rho={np.corrcoef(a, b)[0, 1]:+.2f}, variance ratio antithetic vs plain = "
      f"{np.var(y, ddof=1) / (2 * np.var((a + b) / 2, ddof=1)):.2f}x")

# 2. Control variate with beta fixed at 1 ("just subtract C - 7.2") instead of the fitted beta. Predict: better or worse?
y, c = vr.overtime(np.random.default_rng(vr.SEED).random((n, vr.N_TASKS)))
for beta in (0.609, 1.0, 1.5):
    print(f"control variate beta={beta}: variance ratio {np.var(y) / np.var(y - beta * (c - 7.2)):.2f}x")
