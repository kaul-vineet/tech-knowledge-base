"""Try it 1: common random numbers (CRN). Give both arms the SAME streams and analyse paired differences.

Predict first: the default (independent streams, Welch CI) needs 55 replications per arm for a half-width of 0.3 min.
How many does a paired design need? python try_it/crn.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import model  # noqa: E402
import stats  # noqa: E402

A, B, SEED, H, N0 = {"lam": 0.8, "mu": 1.0}, {"lam": 0.8, "mu": 1.05}, 13, 0.3, 10


def paired(n_max=200):
    a, b, n = [], [], N0
    while True:
        for rep in range(len(a), n):
            s = model.seed_for(SEED, 0, rep)  # same stream for both arms: the only change is mu
            a.append(model.run_once(A, s))
            b.append(model.run_once(B, s))
        d = [y - x for x, y in zip(a, b)]
        m, hw = stats.mean_ci(d)
        n_req = math.ceil(n * (hw / H) ** 2)
        if n_req <= n or n >= n_max:
            r = sum((x - stats.mean_sd(a)[0]) * (y - stats.mean_sd(b)[0]) for x, y in zip(a, b)) / (
                (n - 1) * stats.mean_sd(a)[1] * stats.mean_sd(b)[1])
            return n, m, hw, r
        n = n_req


if __name__ == "__main__":
    n, m, hw, r = paired()
    print("independent streams (default run): n = 55 per arm, difference -0.895 +/- 0.293 min, cost 220,000 customers")
    print(f"common random numbers (paired)   : n = {n} per arm, difference {m:.3f} +/- {hw:.3f} min, "
          f"cost {2 * n * 2000:,} customers, correlation between arms {r:.3f}")
