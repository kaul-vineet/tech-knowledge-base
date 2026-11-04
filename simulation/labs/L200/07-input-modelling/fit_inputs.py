"""L200 input modelling: fit candidate distributions to measured service times, check the fit, see why it matters.

Data: service_times.csv (200 bike-repair service times, minutes). Candidates: exponential, normal, lognormal.
python fit_inputs.py
"""
import csv
from pathlib import Path
from statistics import NormalDist

import numpy as np

DATA = Path(__file__).with_name("service_times.csv")
Z = NormalDist()  # standard normal: cdf / inv_cdf from the stdlib, no SciPy needed
phi, phi_inv = np.vectorize(Z.cdf), np.vectorize(Z.inv_cdf)


def load(path=DATA):
    with path.open(encoding="utf-8", newline="") as f:  # explicit encoding: same result on Windows
        return np.array([float(row["minutes"]) for row in csv.DictReader(f)])


def fit_exponential(x):
    rate = 1 / x.mean()  # MLE (and method of moments): rate = 1 / sample mean
    return {"name": "exponential", "params": {"rate": rate},
            "cdf": lambda v: 1 - np.exp(-rate * v), "ppf": lambda p: -np.log(1 - p) / rate,
            "sample": lambda rng, n: rng.exponential(1 / rate, n)}


def fit_normal(x):
    mu, sd = x.mean(), x.std()  # method of moments = MLE for the normal (ddof=0)
    return {"name": "normal", "params": {"mu": mu, "sigma": sd},
            "cdf": lambda v: phi((v - mu) / sd), "ppf": lambda p: mu + sd * phi_inv(p),
            "sample": lambda rng, n: np.maximum(rng.normal(mu, sd, n), 0.0)}  # a time can't be negative: clip


def fit_lognormal(x):
    mu, s = np.log(x).mean(), np.log(x).std()  # MLE: mean and sd of log(data)
    return {"name": "lognormal", "params": {"mu": mu, "sigma": s},
            "cdf": lambda v: phi((np.log(v) - mu) / s), "ppf": lambda p: np.exp(mu + s * phi_inv(p)),
            "sample": lambda rng, n: rng.lognormal(mu, s, n)}


FITTERS = [fit_exponential, fit_normal, fit_lognormal]


def ks_statistic(x, cdf):
    """Kolmogorov-Smirnov D: largest gap between the empirical CDF (steps of 1/n) and the fitted CDF."""
    x = np.sort(x)
    n, F, i = len(x), cdf(x), np.arange(1, len(x) + 1)
    return float(max((F - (i - 1) / n).max(), (i / n - F).max()))  # check BOTH sides of every step


def qq_points(x, ppf, probs=(0.10, 0.50, 0.90, 0.99)):
    """Q-Q data: fitted quantile vs data quantile at the same probability (on a straight line if the fit is good)."""
    return [(p, float(ppf(np.array(p))), float(np.quantile(x, p))) for p in probs]


def queue_waits(sample, lam, n=200_000, seed=7):
    """Single-server queue fed by the fitted service distribution (Lindley rule), Poisson arrivals."""
    rng = np.random.default_rng(seed)
    service, gaps = sample(rng, n).tolist(), rng.exponential(1 / lam, n).tolist()
    w, out = 0.0, []
    for s, a in zip(service, gaps):
        out.append(w)
        w = max(0.0, w + s - a)
    return np.array(out[5_000:])  # drop warm-up (lesson 10)


def main():
    x = load()
    print(f"data: n={len(x)} mean={x.mean():.2f} sd={x.std():.2f} cv={x.std() / x.mean():.2f} max={x.max():.2f} min")
    fits = [f(x) for f in FITTERS]
    print(f"{'candidate':12} {'parameters':28} KS D   (5% critical ~{1.36 / np.sqrt(len(x)):.3f} if params were known)")
    for fit in fits:
        params = " ".join(f"{k}={v:.3f}" for k, v in fit["params"].items())
        print(f"{fit['name']:12} {params:28} {ks_statistic(x, fit['cdf']):.3f}")
    best = min(fits, key=lambda f: ks_statistic(x, f["cdf"]))  # D ranks candidates; it is not a valid p-value here
    qq = "  ".join(f"{p:.2f}: {q:.2f} vs {d:.2f}" for p, q, d in qq_points(x, best["ppf"]))
    print(f"smallest D: {best['name']} | Q-Q (p: fitted vs data):", qq)
    lam = 0.85 / x.mean()  # same 85% utilisation for every candidate: only the SHAPE differs
    print(f"queue at 85% load (lam={lam:.3f}/min): mean wait / p95 wait / P(service > 10 min)")
    resampled = {"name": "data (resampled)", "sample": lambda rng, n: rng.choice(x, n),  # reference: the data itself
                 "cdf": lambda v: (x[:, None] <= v).mean(axis=0)}
    for fit in fits + [resampled]:
        w = queue_waits(fit["sample"], lam)
        tail = 1 - float(fit["cdf"](np.array([10.0]))[0])
        print(f"  {fit['name']:16} {w.mean():6.2f} min / {np.quantile(w, 0.95):6.2f} min / {tail:.3f}")


if __name__ == "__main__":
    main()
