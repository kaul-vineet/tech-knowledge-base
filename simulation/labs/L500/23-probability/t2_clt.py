"""Theorem 23.2 (central limit theorem, Lindeberg-Levy).
For iid X_i with finite variance: Z_n = (sum - n mu) / (sigma sqrt n) -> N(0, 1) in distribution.
Check: Exponential(1) sums (skewness 2 / sqrt n); Kolmogorov distance sup|F_n - Phi| on 20,000 draws."""
import math

import numpy as np

rng = np.random.default_rng(2302)
REPS = 20_000
phi_cdf = np.vectorize(lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2))))

print("n     P(Z_n <= 1.96)  KS distance to N(0,1)  skewness 2/sqrt(n)")
dists = []
for n in (1, 4, 16, 64, 256):
    sums = rng.gamma(n, 1.0, REPS) if n > 64 else rng.exponential(1.0, (REPS, n)).sum(axis=1)
    z = np.sort((sums - n) / math.sqrt(n))
    f = phi_cdf(z)
    ecdf_hi = np.arange(1, REPS + 1) / REPS
    ecdf_lo = np.arange(0, REPS) / REPS
    d = float(max(np.max(ecdf_hi - f), np.max(f - ecdf_lo)))
    dists.append(d)
    print(f"{n:<5} {np.mean(z <= 1.96):<15.4f} {d:<22.4f} {2 / math.sqrt(n):.3f}")
assert all(a > b for a, b in zip(dists, dists[1:3])), dists  # distance falls while it is above sampling noise
assert dists[-1] < 1.36 / math.sqrt(REPS) * 1.5  # at n = 256 it is near the KS noise floor (1.36/sqrt(REPS) = 0.0096)
print(f"exact P(Z <= 1.96) = {phi_cdf(1.96):.4f}; KS noise floor for 20,000 draws ~ {1.36 / math.sqrt(REPS):.4f}")
