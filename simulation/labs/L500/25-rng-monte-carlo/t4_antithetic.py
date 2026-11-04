"""Theorem 25.4 (antithetic variates, covariance argument).
For a pair (f(U), f(1 - U)): Var[(f(U) + f(1 - U))/2] = sigma^2 (1 + rho) / 2, rho = Corr(f(U), f(1 - U)).
Against 2 independent draws (variance sigma^2 / 2) the gain is 1 / (1 + rho): a win iff rho < 0, which holds for
every monotone f (U and 1 - U are counter-monotone; Chebyshev's association inequality). Symmetric f gives rho = +1."""
import math

import numpy as np

rng = np.random.default_rng(2504)
mu = math.e - 1
sigma2 = (math.e**2 - 1) / 2 - mu**2
rho = (math.e - mu**2) / sigma2  # E[e^U e^(1-U)] = e
print(f"f(u) = e^u: rho = (e - (e-1)^2) / sigma^2 = {rho:.4f}; predicted gain 1/(1 + rho) = {1 / (1 + rho):.1f}x")
u = rng.random((4000, 500))
plain = np.exp(rng.random((4000, 1000))).mean(axis=1)  # 1000 evaluations
anti = ((np.exp(u) + np.exp(1 - u)) / 2).mean(axis=1)  # 500 pairs = 1000 evaluations
gain = plain.var() / anti.var()
print(f"  same 1,000 evaluations: var plain {plain.var():.3e}, antithetic {anti.var():.3e}, observed gain {gain:.1f}x")
g = lambda v: (v - 0.5) ** 2  # symmetric: g(U) = g(1 - U), rho = +1
plain_g = g(rng.random((4000, 1000))).mean(axis=1)
anti_g = ((g(u) + g(1 - u)) / 2).mean(axis=1)
print(f"f(u) = (u - 0.5)^2 (symmetric): observed gain {plain_g.var() / anti_g.var():.2f}x (theory 1/(1 + 1) = 0.50x)")
assert abs(gain / (1 / (1 + rho)) - 1) < 0.1 and abs(plain_g.var() / anti_g.var() - 0.5) < 0.05
