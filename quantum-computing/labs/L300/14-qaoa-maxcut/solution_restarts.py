"""Build-task solution for lab 14: escape local minima with a grid / interpolated start plus seeded restarts.

Run: python solution_restarts.py
p = 1: start from the best point of the 41x21 grid. p = 2: interpolate the p = 1 answer into a ramp
[gamma/2, gamma, beta, beta/2] (a common QAOA warm start), then add a few random restarts and keep the best.
"""
import json

import numpy as np

import qaoa_lab as lab


def starts(p, seed, restarts):
    g, b, _ = lab.landscape()
    if p == 1:
        yield np.array([g, b])
    else:
        g1, b1 = lab.optimize([g, b])
        yield np.array([g1 / 2, g1, b1, b1 / 2])                    # interpolated warm start
    rng = np.random.default_rng(seed)
    for _ in range(restarts):
        yield rng.uniform(0, np.pi, 2 * p)


def solve(p, seed=0, restarts=3):
    results = [(lab.cost(x), x) for x in (lab.optimize(x0) for x0 in starts(p, seed, restarts))]
    return min(results, key=lambda r: r[0])[1]


if __name__ == "__main__":
    for p in (1, 2):
        x = solve(p)
        print(json.dumps({"p": p, "method": "warm start + 3 restarts", "ratio": lab.ratio(x), "params": np.round(x, 3).tolist()}))
