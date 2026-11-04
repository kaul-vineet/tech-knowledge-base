"""MaxCut solvers for lab 18. Every budgeted solver gets (n, edges, budget, seed) and returns
{"cut": best cut found, "used": samples (candidate cut evaluations or shots) spent, "first_best": samples to reach it}.
One "sample" = one candidate bitstring evaluated - a classical flip evaluation or one quantum shot.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from qopt import maxcut as mc  # noqa: E402


def neighbours(n, edges):
    nb = [[] for _ in range(n)]
    for i, j in edges:
        nb[i].append(j)
        nb[j].append(i)
    return nb


def gain(x, v, nb):
    """Change in cut size if vertex v flips side."""
    same = sum(x[u] == x[v] for u in nb[v])
    return 2 * same - len(nb[v])


def exact(n, edges, budget=None, seed=None):
    best, _ = mc.brute_force(n, edges)                  # 2**n evaluations: the reference, not budgeted
    return {"cut": best, "used": 2 ** n, "first_best": 2 ** n}


def greedy(n, edges, budget, seed):
    """Random start, best-improving single flips until a local optimum, then restart."""
    rng, nb = np.random.default_rng(seed), neighbours(n, edges)
    best = {"cut": -1, "used": 0, "first_best": 0}
    used = 0
    while used + n <= budget:
        x = rng.integers(0, 2, n)
        cut = mc.cut_of(int(sum(int(b) << i for i, b in enumerate(x))), edges)
        while used + n <= budget:
            gains = [gain(x, v, nb) for v in range(n)]
            used += n
            v = int(np.argmax(gains))
            if gains[v] <= 0:
                break
            x[v] ^= 1
            cut += gains[v]
        if cut > best["cut"]:
            best = {"cut": int(cut), "first_best": used}
    return {**best, "used": used}


def annealing(n, edges, budget, seed, t0=2.0, t1=0.05):
    """Simulated annealing (Kirkpatrick et al. 1983): Metropolis single flips on a geometric cooling schedule."""
    rng, nb = np.random.default_rng(seed), neighbours(n, edges)
    x = rng.integers(0, 2, n)
    cut = mc.cut_of(int(sum(int(b) << i for i, b in enumerate(x))), edges)
    best, first = cut, 0
    for k in range(budget):
        t = t0 * (t1 / t0) ** (k / max(budget - 1, 1))
        v = int(rng.integers(n))
        g = gain(x, v, nb)
        if g >= 0 or rng.random() < np.exp(g / t):
            x[v] ^= 1
            cut += g
            if cut > best:
                best, first = cut, k + 1
    return {"cut": int(best), "used": budget, "first_best": first}


def qaoa(n, edges, budget, seed, grid=5):
    """QAOA p=1 on the simulator, charged like hardware: half the shots pick angles on a grid, half sample."""
    rng, cuts = np.random.default_rng(seed), mc.cut_values(n, edges)
    per_point = budget // 2 // (grid * grid)
    scores = {}
    for g in np.linspace(0.2, 1.0, grid):
        for b in np.linspace(0.1, 0.7, grid):
            scores[(g, b)] = cuts[mc.sample(n, cuts, [g, b], per_point, rng)].mean()   # shot-based estimate
    angles = max(scores, key=scores.get)
    shots = budget - per_point * grid * grid
    found = cuts[mc.sample(n, cuts, list(angles), shots, rng)]
    first = per_point * grid * grid + int(np.argmax(found == found.max())) + 1
    return {"cut": int(found.max()), "used": budget, "first_best": first}


BUDGETED = {"greedy": greedy, "annealing": annealing, "qaoa": qaoa}
