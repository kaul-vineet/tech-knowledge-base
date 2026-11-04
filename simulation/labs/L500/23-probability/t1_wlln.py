"""Theorem 23.1 (weak law of large numbers, Chebyshev proof).
For iid X_i with mean mu and variance sigma^2: P(|mean_n - mu| >= eps) <= sigma^2 / (n eps^2) -> 0.
Check: Exponential(1) (mu = 1, sigma^2 = 1), eps = 0.2, 10,000 sample means per n."""
import numpy as np

rng = np.random.default_rng(2301)
MU, VAR, EPS, REPS = 1.0, 1.0, 0.2, 10_000

print("n      Chebyshev bound  observed P(|mean - 1| >= 0.2)")
previous = 1.0
for n in (25, 100, 400, 1600):
    hits = 0
    for _ in range(REPS // 1000):  # chunks keep memory small (1000 x n doubles)
        means = rng.exponential(1.0, (1000, n)).mean(axis=1)
        hits += int(np.sum(np.abs(means - MU) >= EPS))
    p = hits / REPS
    bound = min(1.0, VAR / (n * EPS**2))
    assert p <= bound, (n, p, bound)  # the theorem: never above the bound
    assert p <= previous  # and the probability shrinks with n
    previous = p
    print(f"{n:<6} {bound:<16.4f} {p:.4f}")
print("bound holds for every n; it is loose (Chebyshev uses only the variance)")
