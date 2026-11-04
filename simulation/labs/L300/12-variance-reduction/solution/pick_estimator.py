"""buildTask solution (lesson 12): a pilot run PROPOSES the estimator; antithetic is refused unless pairs anti-correlate.

python solution/pick_estimator.py
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import variance_reduction as vr  # noqa: E402


def pick_estimator(f, dims, control_mean=None, pilot=2_000, seed=99, log=print):
    """f(u) -> (y, c). Measure per-evaluation variance of each method on a small pilot; never trust a default."""
    u = np.random.default_rng(seed).random((pilot, dims))
    y, c = f(u)
    ratios = {"plain": 1.0}
    a, b = f(u[: pilot // 2])[0], f(1.0 - u[: pilot // 2])[0]
    rho = float(np.corrcoef(a, b)[0, 1]) if np.std(a) > 0 and np.std(b) > 0 else 1.0
    if rho < 0:  # Owen 8.2: rho >= 0 means antithetic sampling cannot help and can double the variance
        ratios["antithetic"] = float(np.var(y, ddof=1) / (2 * np.var((a + b) / 2, ddof=1)))
    if control_mean is not None:
        beta = np.cov(y, c)[0, 1] / np.var(c, ddof=1)
        ratios["control variate"] = float(np.var(y, ddof=1) / np.var(y - beta * (c - control_mean), ddof=1))
    method = max(ratios, key=ratios.get)
    decision = {"event": "estimator_choice", "pilot": pilot, "rho": round(rho, 3),
                "ratios": {k: round(v, 2) for k, v in ratios.items()}, "method": method}
    log(json.dumps(decision))  # structured log line: the decision and the evidence for it
    return decision


def even(u):
    """Symmetric under u -> 1-u: the antithetic partner gives the SAME value (rho = +1)."""
    y = (u.sum(axis=1) - u.shape[1] / 2) ** 2
    return y, y


def monotone(u):
    """Increasing in every input: antithetic pairs anti-correlate (Owen's 'safe harbor')."""
    y = np.exp(u.sum(axis=1) / 2)
    return y, y


if __name__ == "__main__":
    pick_estimator(vr.overtime, vr.N_TASKS, control_mean=vr.N_TASKS * vr.MEAN_H)
    pick_estimator(even, 4)
    pick_estimator(monotone, 4)
