"""Fake device for lab 20: an 8-qubit ladder with seeded per-gate error rates, plus a seeded calibration drift.

  0 - 1 - 2 - 3        CX errors: uniform 0.5-2 % per edge (seed 5); 1q errors 0.02-0.1 %; readout 1-4 %.
  |   |   |   |        DRIFT = today's calibration: edge (1, 2) degrades to 15 %.
  4 - 5 - 6 - 7        Illustrative values in the range of published device data, not a real device.
"""
import itertools

import numpy as np

EDGES = [(0, 1), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7), (0, 4), (1, 5), (2, 6), (3, 7)]
DRIFT = {(1, 2): 0.15}


def make_device(seed=5, drift=None):
    rng = np.random.default_rng(seed)
    cx = {e: round(float(rng.uniform(0.005, 0.02)), 4) for e in EDGES}
    cx.update(drift or {})
    return {"n": 8, "cx": cx, "sq": [round(float(e), 5) for e in rng.uniform(2e-4, 1e-3, 8)],
            "ro": [round(float(e), 4) for e in rng.uniform(0.01, 0.04, 8)]}


def cx_error(dev, a, b):
    return dev["cx"].get((a, b), dev["cx"].get((b, a)))


_CACHE = {}


def all_pairs(dev, weighted):
    """Floyd-Warshall: hop counts, or -log(1 - error) so the 'shortest' path is the most reliable one."""
    key = (tuple(sorted(dev["cx"].items())), weighted)
    if key not in _CACHE:
        _CACHE[key] = _floyd(dev, weighted)
    return _CACHE[key]


def _floyd(dev, weighted):
    n, inf = dev["n"], float("inf")
    dist = [[0 if i == j else inf for j in range(n)] for i in range(n)]
    nxt = [[j for j in range(n)] for _ in range(n)]
    for (a, b), e in dev["cx"].items():
        w = -np.log(1 - e) if weighted else 1.0
        dist[a][b] = dist[b][a] = w
    for k, i, j in itertools.product(range(n), repeat=3):
        if dist[i][k] + dist[k][j] < dist[i][j]:
            dist[i][j], nxt[i][j] = dist[i][k] + dist[k][j], nxt[i][k]
    return dist, nxt


def path(nxt, a, b):
    out = [a]
    while out[-1] != b:
        out.append(nxt[out[-1]][b])
    return out
