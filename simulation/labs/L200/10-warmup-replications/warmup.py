"""L200 warm-up, replications and confidence: an IT help desk opens on Monday with 30 weekend tickets waiting.

Question: long-run mean wait at 80% load (M/M/1: 4.0 min). The backlog biases early waits HIGH: find it, delete it.
python warmup.py
"""
import math
import random
from statistics import NormalDist

import numpy as np

LAM, MU, BACKLOG = 0.8, 1.0, 30
TRUE_WQ = LAM / (MU * (MU - LAM))  # 4.0 min


def waits(m, seed, lam=LAM, mu=MU, backlog=BACKLOG):
    rng = random.Random(seed)  # one independent stream per replication
    w = sum(rng.expovariate(mu) for _ in range(backlog))  # first arrival waits for the whole backlog
    out = np.empty(m)
    for i in range(m):
        out[i] = w
        w = max(0.0, w + rng.expovariate(mu) - rng.expovariate(lam))  # Lindley rule (lesson 6)
    return out


def welch(runs, window):
    """Welch's moving average of the across-replication mean (Currie & Cheng, WSC 2016, section 3.1.1)."""
    ybar = runs.mean(axis=0)  # average over replications at each customer index
    out = [ybar[:2 * t + 1].mean() for t in range(window)]  # short symmetric windows at the start
    csum = np.concatenate(([0.0], np.cumsum(ybar)))
    out += [(csum[t + window + 1] - csum[t - window]) / (2 * window + 1) for t in range(window, len(ybar) - window)]
    return np.array(out)


def warmup_point(smooth, tol=0.05):
    """Code PROPOSES a warm-up: first index where the curve enters a +/-5% band around its second-half level."""
    level = smooth[len(smooth) // 2:].mean()
    return int(np.nonzero(np.abs(smooth - level) <= tol * level)[0][0]), float(level)  # still look at the curve


def t975(df):
    z = NormalDist().inv_cdf(0.975)  # Cornish-Fisher expansion of the t quantile; within 0.005 of tables for df >= 9
    return z + (z ** 3 + z) / (4 * df) + (5 * z ** 5 + 16 * z ** 3 + 3 * z) / (96 * df ** 2)


def ci(means):
    n = len(means)  # one mean per independent replication -> the t-interval is valid
    return float(np.mean(means)), t975(n - 1) * float(np.std(means, ddof=1)) / math.sqrt(n)


def main():
    runs = np.array([waits(5_000, seed) for seed in range(1, 21)])
    smooth = welch(runs, window=50)
    d, level = warmup_point(smooth)
    print("1. Welch: 20 replications x 5,000 customers, window 50. Moving average at customer:")
    print("   " + "  ".join(f"{i}: {smooth[i]:.2f}" for i in (0, 50, 100, 150, 200, 500, 2000, 4000)))
    print(f"   code proposes warm-up = {d} customers (enters 5% band around level {level:.2f})")
    short = [waits(1_000, seed) for seed in range(101, 141)]  # 40 short runs: the warm-up is a big share of each
    for cut in (0, d):
        m, h = ci([r[cut:].mean() for r in short])
        print(f"2. 40 runs x 1,000 customers, delete first {cut:3d}: {m:.2f} +/- {h:.2f} min (true {TRUE_WQ:.1f})")
    print("3. replications of 5,000 customers, warm-up deleted: 95% CI")
    means = [waits(5_000, seed)[d:].mean() for seed in range(201, 281)]
    for n in (10, 20, 40, 80):
        m, h = ci(means[:n])
        print(f"   n={n:2d}: {m:.2f} +/- {h:.2f} min  (half-width x sqrt(n) = {h * math.sqrt(n):.2f})")


if __name__ == "__main__":
    main()
