"""Theorem 25.3 (Monte Carlo estimator; importance sampling).
(a) mu_N = (1/N) sum f(U_i) is unbiased with Var = sigma^2 / N, so RMSE = sigma / sqrt(N) whatever the dimension.
(b) For q > 0 where f p != 0: E_p[f] = E_q[f p / q], unbiased; Var_q = E_q[(f p/q)^2] - mu^2, zero for q* = f p / mu (f >= 0).
Checks: (a) int_0^1 e^x dx = e - 1, sigma^2 = (e^2 - 1)/2 - (e - 1)^2; (b) P(Z > 4) with q = N(4, 1):
weight phi(x)/phi(x - 4) = exp(8 - 4x); exact second moment e^16 Pbar(8)."""
import math

import numpy as np

rng = np.random.default_rng(2503)
mu = math.e - 1
sigma2 = (math.e**2 - 1) / 2 - mu**2
print(f"(a) e - 1 = {mu:.5f}; sigma^2 = {sigma2:.5f}")
print("    N      sd of 2,000 estimates   sigma/sqrt(N)   mean of estimates")
ns, sds = [], []
for n in (100, 400, 1600, 6400):
    est = np.exp(rng.random((2000, n))).mean(axis=1)
    ns.append(n)
    sds.append(est.std(ddof=1))
    print(f"    {n:<6} {sds[-1]:<23.5f} {math.sqrt(sigma2 / n):<15.5f} {est.mean():.5f}")
slope = np.polyfit(np.log(ns), np.log(sds), 1)[0]
print(f"    log-log slope of sd vs N: {slope:.3f} (theory -0.5)")
assert abs(slope + 0.5) < 0.03

tail = lambda z: 0.5 * math.erfc(z / math.sqrt(2))
p = tail(4.0)
naive_rel = math.sqrt((1 - p) / (100_000 * p))
second = math.exp(16) * tail(8.0)
is_rel = math.sqrt((second - p**2) / 10_000) / p
naive = np.mean(rng.standard_normal(100_000) > 4)
x = rng.normal(4.0, 1.0, 10_000)
w = np.where(x > 4, np.exp(8 - 4 * x), 0.0)
print(f"(b) exact P(Z > 4) = {p:.4e}")
print(f"    naive,  N = 100,000: estimate {naive:.4e}; theory relative SE {naive_rel:.3f}")
print(f"    IS N(4,1), N = 10,000: estimate {w.mean():.4e}; sample relative SE {w.std(ddof=1) / math.sqrt(w.size) / w.mean():.4f}; theory {is_rel:.4f}")
print(f"    variance per sample: naive {p * (1 - p):.3e} vs IS {second - p**2:.3e} -> {p * (1 - p) / (second - p**2):,.0f}x fewer samples")
assert abs(w.mean() - p) / p < 4 * is_rel
