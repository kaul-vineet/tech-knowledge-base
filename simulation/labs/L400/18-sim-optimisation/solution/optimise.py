"""buildTask solution (lesson 18): pick() re-runs the finalists on fresh common random numbers with OCBA,
from a reserve inside the same budget. Otherwise identical to the lab file.

L400 simulation-based optimisation: choose a bike shop's (s, S) policy under uncertain demand.

Reuses the L200 lesson 11 inventory model. 81 designs: s = 10..50 (step 5), Q = S - s = 20..100 (step 10).
Three optimisers get the SAME budget of simulation runs and the SAME common random numbers:
grid search, a GP-lite surrogate with expected improvement, and a (mu + lambda) evolution strategy.
python solution/optimise.py
"""
import json
import math
import sys
from pathlib import Path
from statistics import NormalDist

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.append(str(HERE.parents[1] / "L200" / "11-supply-chain-inventory"))
import inventory  # noqa: E402  (L200 lesson 11: simulate(s, S, demand, lead), streams(rep, days))

S_GRID, Q_GRID = np.arange(10, 55, 5), np.arange(20, 110, 10)
DESIGNS = [(int(s), int(q)) for s in S_GRID for q in Q_GRID]
DAYS, BUDGET, REPS_PER_LOOK = 180, 324, 4  # 324 runs = grid search with 4 replications per design
RESERVE = 60  # FIX: runs kept back from the search for the final selection (same total budget)
FINALISTS, FIRST_LOOK, STEP, FRESH = 5, 5, 5, 500  # fresh replications start at stream index 500
TRUTH = {tuple(json.loads(k)): v for k, v in json.loads((HERE / "truth.json").read_text(encoding="utf-8")).items()}
N = NormalDist()


class Budget:
    """Counts every simulation run; an optimiser that asks for more than its share gets an error, not a result."""

    def __init__(self, total, crn_offset):
        self.total, self.used, self.offset = total, 0, crn_offset

    def run(self, design, rep):
        if self.used >= self.total:
            raise RuntimeError("simulation budget exhausted")
        self.used += 1
        s, q = design
        demand, lead = inventory.streams(self.offset + rep, DAYS)  # CRN: replication r = the same days for all designs
        return inventory.simulate(s, s + q, demand, lead)["cost_per_day"]


def look(budget, design, data, reps=REPS_PER_LOOK):
    """Add `reps` replications of `design` (continuing its stream index) to data[design]."""
    reps = min(reps, budget.total - budget.used)
    if reps > 0:
        have = data.setdefault(design, [])
        have += [budget.run(design, len(have) + r) for r in range(reps)]


def grid_search(budget, rng):
    data, reps = {}, (budget.total - budget.used) // len(DESIGNS)  # equal allocation over all 81 designs
    for d in DESIGNS:
        look(budget, d, data, reps)
    return data


def gp_posterior(X, y, Xs, length=1.5, noise=0.05):
    """GP-lite: RBF kernel on grid-index coordinates, outputs standardised (GPML Algorithm 2.1, Cholesky form)."""
    mu, sd = y.mean(), y.std() + 1e-9
    k = lambda A, B: np.exp(-0.5 * ((A[:, None, :] - B[None, :, :]) ** 2).sum(-1) / length ** 2)
    L = np.linalg.cholesky(k(X, X) + noise * np.eye(len(X)))
    alpha = np.linalg.solve(L.T, np.linalg.solve(L, (y - mu) / sd))
    Ks, v = k(X, Xs), np.linalg.solve(L, k(X, Xs))
    return mu + sd * Ks.T @ alpha, sd * np.sqrt(np.maximum(1e-12, 1 - (v ** 2).sum(0)))


def surrogate_search(budget, rng, n_init=12):
    data, coords = {}, {d: (list(S_GRID).index(d[0]), list(Q_GRID).index(d[1])) for d in DESIGNS}
    for i in rng.choice(len(DESIGNS), n_init, replace=False):
        look(budget, DESIGNS[i], data)
    while budget.used + REPS_PER_LOOK <= budget.total:
        seen = list(data)
        X, y = np.array([coords[d] for d in seen], float), np.array([np.mean(data[d]) for d in seen])
        m, s = gp_posterior(X, y, np.array([coords[d] for d in DESIGNS], float))
        z = (y.min() - m) / s
        ei = (y.min() - m) * np.array([N.cdf(v) for v in z]) + s * np.array([N.pdf(v) for v in z])  # EGO's EI
        look(budget, DESIGNS[int(np.argmax(ei))], data)  # a revisit adds replications: noise matters
    return data


def evolution(budget, rng, mu=4, lam=8):
    data = {}
    parents = [DESIGNS[i] for i in rng.choice(len(DESIGNS), mu, replace=False)]
    for p in parents:
        look(budget, p, data)
    while budget.used + REPS_PER_LOOK <= budget.total:
        for _ in range(lam):
            s, q = rng.choice(parents)
            child = (int(np.clip(s + 5 * rng.integers(-2, 3), 10, 50)), int(np.clip(q + 10 * rng.integers(-2, 3), 20, 100)))
            look(budget, child, data)
        parents = sorted(data, key=lambda d: np.mean(data[d]))[:mu]  # (mu + lambda): parents compete too
    return data


def ocba(means, sds, total):
    """OCBA (Chen et al. 2000), minimising: N_i ~ (sd_i / d_i)^2 for non-best i, d_i = mean_i - mean_best;
    N_best = sd_best * sqrt(sum N_i^2 / sd_i^2). Returns the ideal number of runs per design for `total` runs."""
    means, sds = np.asarray(means, float), np.maximum(np.asarray(sds, float), 1e-9)
    b = int(np.argmin(means))
    ratio = (sds / np.maximum(means - means[b], 1e-9)) ** 2
    ratio[b] = 0.0
    ratio[b] = sds[b] * math.sqrt(float(np.sum(ratio ** 2 / sds ** 2)))
    return ratio / ratio.sum() * total


def pick(budget, data):
    """Choose the winner and the cost we report for it."""
    finalists = sorted(data, key=lambda d: np.mean(data[d]))[:FINALISTS]
    fresh = {d: [] for d in finalists}  # FIX: new replications, never used to rank the search, CRN across finalists

    def more(d, n):
        for _ in range(min(n, budget.total - budget.used)):
            fresh[d].append(budget.run(d, FRESH + len(fresh[d])))

    for d in finalists:
        more(d, FIRST_LOOK)
    while budget.used < budget.total:  # OCBA: give the next STEP runs to the finalist furthest below its share
        n = np.array([len(fresh[d]) for d in finalists])
        target = ocba([np.mean(fresh[d]) for d in finalists], [np.std(fresh[d], ddof=1) for d in finalists],
                      n.sum() + STEP)
        more(finalists[int(np.argmax(target - n))], STEP)
    best = min(finalists, key=lambda d: np.mean(fresh[d]))
    return best, float(np.mean(fresh[best]))  # an estimate from data the choice did not see


def optimise(method, macro_rep, budget_total=BUDGET):
    rng = np.random.default_rng([18, macro_rep])  # optimiser's own randomness, separate from the model's streams
    budget = Budget(budget_total, crn_offset=1000 * macro_rep)
    budget.total = budget_total - RESERVE
    data = method(budget, rng)
    budget.total = budget_total
    best, reported = pick(budget, data)
    return {"method": method.__name__, "macro_rep": macro_rep, "design": best, "reported": reported,
            "true": TRUTH[best]["mean"], "gap": TRUTH[best]["mean"] - min(v["mean"] for v in TRUTH.values()),
            "runs": budget.used, "designs_seen": len(data)}


def main(macro_reps=5):
    best = min(TRUTH, key=lambda d: TRUTH[d]["mean"])
    print(f"81 (s, Q) designs; true best {best} at {TRUTH[best]['mean']:.3f}/day (truth.json: 100 reps per design)")
    print(f"budget {BUDGET} runs per optimiser ({RESERVE} reserved for selection), {macro_reps} macro-replications")
    print(f"{'method':17s} {'mean gap':>9s} {'worst gap':>9s} {'reported - true':>16s} {'runs':>5s}")
    for method in (grid_search, surrogate_search, evolution):
        rows = [optimise(method, m) for m in range(macro_reps)]
        gaps, bias = [r["gap"] for r in rows], [r["reported"] - r["true"] for r in rows]
        print(f"{method.__name__:17s} {np.mean(gaps):9.3f} {max(gaps):9.3f} {np.mean(bias):+16.3f} "
              f"{max(r['runs'] for r in rows):5d}   picks {[r['design'] for r in rows]}")


if __name__ == "__main__":
    main()
