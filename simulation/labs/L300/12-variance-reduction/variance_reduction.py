"""L300 variance reduction: expected overtime of a warehouse picking shift, with fewer runs for the same precision.

A shift has 12 picking tasks, each ~ exponential(mean 0.6 h); overtime = max(0, total - 7 h).
The exact answer is known (Erlang formula), so every estimator can be checked against it.
python variance_reduction.py
"""
import math

import numpy as np

N_TASKS, MEAN_H, SHIFT_H, SEED = 12, 0.6, 7.0, 2026


def overtime(u, shift=SHIFT_H):
    """Model: uniforms (n, 12) -> overtime hours. Inverse transform t = -mean*ln(1-u) is monotone in every u."""
    t = -MEAN_H * np.log1p(-u)
    return np.maximum(t.sum(axis=1) - shift, 0.0), t.sum(axis=1)


def exact_overtime(k=N_TASKS, mean=MEAN_H, s=SHIFT_H):
    """E[(T - s)+] for T ~ Erlang(k, rate 1/mean) = k*mean*P(Erlang(k+1) > s) - s*P(Erlang(k) > s)."""
    tail = lambda m: sum(math.exp(-s / mean) * (s / mean) ** j / math.factorial(j) for j in range(m))
    return k * mean * tail(k + 1) - s * tail(k)


def summary(y, evals):
    """Mean, standard error and per-evaluation variance (the cost-fair number to compare methods by)."""
    se = float(np.std(y, ddof=1) / math.sqrt(len(y)))
    return {"mean": float(np.mean(y)), "se": se, "var_per_eval": se ** 2 * evals}


def plain(n, seed=SEED):
    y, _ = overtime(np.random.default_rng(seed).random((n, N_TASKS)))
    return summary(y, n)


def antithetic(n, seed=SEED):
    """One stream per PAIR: f(u) and f(1-u) share the same u, so their errors cancel (Owen 8.2)."""
    u = np.random.default_rng(seed).random((n // 2, N_TASKS))
    a, b = overtime(u)[0], overtime(1.0 - u)[0]
    out = summary((a + b) / 2, n)  # analyse PAIR averages: the two halves of a pair are not independent
    return out | {"rho": float(np.corrcoef(a, b)[0, 1])}


def antithetic_loop(n, seed=SEED):
    """Loop version, as when a simulator is called once per run: evaluate f(u) and its mirror f(1-u) per pair."""
    a, b = np.empty(n // 2), np.empty(n // 2)
    for i in range(n // 2):
        a[i] = overtime(np.random.default_rng([2 * i, seed]).random((1, N_TASKS)))[0][0]  # a fresh stream per call
        b[i] = overtime(1.0 - np.random.default_rng([2 * i + 1, seed]).random((1, N_TASKS)))[0][0]
    return summary((a + b) / 2, n) | {"rho": float(np.corrcoef(a, b)[0, 1])}


def control_variate(n, seed=SEED):
    """Y - beta*(C - E[C]) with C = total task time, whose mean 12*0.6 = 7.2 h is known exactly."""
    y, c = overtime(np.random.default_rng(seed).random((n, N_TASKS)))
    beta = np.cov(y, c)[0, 1] / np.var(c, ddof=1)  # optimal beta = Cov(Y, C) / Var(C)
    return summary(y - beta * (c - N_TASKS * MEAN_H), n) | {"beta": float(beta)}


def crn_difference(n, seed=SEED, crn=True):
    """Recap (L200 #11): overtime saved by a 30-minute longer shift, same vs independent random numbers."""
    rng = np.random.default_rng(seed)
    u7 = rng.random((n, N_TASKS))
    u75 = u7 if crn else rng.random((n, N_TASKS))
    return summary(overtime(u7)[0] - overtime(u75, shift=7.5)[0], n)


def main(n=20_000):
    print(f"exact expected overtime: {exact_overtime():.4f} h per shift (Erlang formula)")
    base = plain(n)
    print(f"{n:,} model evaluations per method:")
    print("  method              estimate   std.err   variance ratio vs plain")
    rows = [("plain Monte Carlo", base), ("antithetic", antithetic(n)), ("control variate", control_variate(n)),
            ("antithetic (loop)", antithetic_loop(n))]
    for name, r in rows:
        extra = f"  rho={r['rho']:+.2f}" if "rho" in r else f"  beta={r['beta']:.3f}" if "beta" in r else ""
        print(f"  {name:18s}  {r['mean']:.4f}    {r['se']:.5f}   {base['var_per_eval'] / r['var_per_eval']:5.2f}x{extra}")
    ind, com = crn_difference(n, crn=False), crn_difference(n)
    print(f"CRN recap, overtime saved by a 7.5 h shift: independent {ind['mean']:.4f} +/- {1.96 * ind['se']:.4f}, "
          f"common {com['mean']:.4f} +/- {1.96 * com['se']:.4f} h")


if __name__ == "__main__":
    main()
