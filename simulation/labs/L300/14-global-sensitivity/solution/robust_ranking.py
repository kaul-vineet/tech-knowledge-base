"""buildTask solution (lesson 14): bootstrap confidence intervals for ST; only claim an order the data supports.

python solution/robust_ranking.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sensitivity as sa  # noqa: E402


def st_with_ci(n=8192, boot=200, f=sa.energy, seed=sa.SEED):
    """Same A/B/AB_i runs as sensitivity.sobol(); resample the n rows with replacement to get a 95% interval."""
    rng, d = np.random.default_rng(seed), len(sa.NAMES)
    a, b = rng.random((n, d)), rng.random((n, d))
    fa, fb = f(sa.scale(a)), f(sa.scale(b))
    fab = []
    for i in range(d):
        ab = a.copy()
        ab[:, i] = b[:, i]
        fab.append(f(sa.scale(ab)))
    fab = np.array(fab)  # (d, n)

    def st(rows):  # Jansen total-order estimator on a subset of rows
        return 0.5 * np.mean((fa[rows] - fab[:, rows]) ** 2, axis=1) / np.var(np.r_[fa[rows], fb[rows]])

    point = st(np.arange(n))
    reps = np.array([st(rng.integers(0, n, n)) for _ in range(boot)])  # bootstrap: no new model runs needed
    return point, np.percentile(reps, 2.5, axis=0), np.percentile(reps, 97.5, axis=0)


def robust_ranking(point, lo, hi):
    """Order by ST; join neighbours with '~' when their intervals overlap (the order between them is not shown)."""
    order = np.argsort(-point)
    text = sa.NAMES[order[0]]
    for prev, cur in zip(order, order[1:]):
        text += (" ~ " if lo[prev] <= hi[cur] else " > ") + sa.NAMES[cur]
    return text


if __name__ == "__main__":
    for n in (32, 8192):
        point, lo, hi = st_with_ci(n)
        cis = ", ".join(f"{name} {p:.3f} [{a:.3f}, {b:.3f}]" for name, p, a, b in zip(sa.NAMES, point, lo, hi))
        print(f"N={n:5d}: {robust_ranking(point, lo, hi)}\n          ST 95% CI: {cis}")
