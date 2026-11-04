"""buildTask solution (lesson 7): add a SHIFTED exponential candidate - a minimum set-up time plus an exponential tail.

python solution/shifted_exponential.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fit_inputs as fi  # noqa: E402


def fit_shifted_exponential(x):
    loc = x.min()  # MLE of the shift: no service is shorter than the shortest one seen
    rate = 1 / (x.mean() - loc)  # MLE of the rate of the part above the shift
    return {"name": "shifted exponential", "params": {"loc": loc, "rate": rate},
            "cdf": lambda v: np.where(v >= loc, 1 - np.exp(-rate * (v - loc)), 0.0),
            "ppf": lambda p: loc - np.log(1 - p) / rate,
            "sample": lambda rng, n: loc + rng.exponential(1 / rate, n)}


FITTERS = fi.FITTERS + [fit_shifted_exponential]

if __name__ == "__main__":
    x = fi.load()
    for f in FITTERS:
        fit = f(x)
        print(f"{fit['name']:20} KS D={fi.ks_statistic(x, fit['cdf']):.3f}")
