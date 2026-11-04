"""buildTask solution (lesson 19): what_if() guards the validity envelope and falls back to the simulation.
Otherwise identical to the lab file.

L400 surrogate models: emulate an "expensive" queue simulation, validate on holdout, use it for what-ifs.

Expensive model: the L200 lesson 8 clinic queue (3 desks, 20,000 patients per run). Inputs: arrival rate lam
in [1.5, 2.4]/min and service rate mu in [0.95, 1.10]/min per desk. Output: mean wait Wq (min).
Three surrogates fitted on the same 30-run Latin hypercube: quadratic polynomial, GP-lite, random features.
python solution/surrogate.py
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.append(str(HERE.parents[1] / "L200" / "08-multi-server-queue"))
import mmc_queue  # noqa: E402  (simulate(n_customers, c, lam, mu, seed), erlang_c(c, lam, mu))

LO, HI = np.array([1.5, 0.95]), np.array([2.4, 1.10])  # the training box = the validity envelope
N_TRAIN, N_HOLD, CUSTOMERS = 30, 20, 20_000
SD_MAX, FALLBACK_REPS = 0.10, 4  # refuse when the GP is this unsure; replications for the fallback run


def expensive(lam, mu, seed):
    return mmc_queue.simulate(CUSTOMERS, 3, lam, mu, seed=seed)["Wq"]


def latin_hypercube(n, rng):
    """One point per 1/n stratum in every input (McKay et al. 1979), strata paired at random."""
    u = (np.array([rng.permutation(n) for _ in LO]).T + rng.random((n, len(LO)))) / n
    return LO + u * (HI - LO)


def scale(X):
    return (np.asarray(X, float) - LO) / (HI - LO)


def fit_poly(X, y):
    feats = lambda Z: np.column_stack([np.ones(len(Z)), Z, Z ** 2, Z[:, :1] * Z[:, 1:]])  # quadratic + interaction
    coef, *_ = np.linalg.lstsq(feats(scale(X)), y, rcond=None)
    return lambda Xs: (feats(scale(Xs)) @ coef, None)


def fit_gp(X, y):
    """GP-lite: RBF kernel, length-scales and noise picked by log marginal likelihood (GPML Algorithm 2.1)."""
    Z, mu_y, sd_y = scale(X), y.mean(), y.std()
    t = (y - mu_y) / sd_y
    k = lambda A, B, ell: np.exp(-0.5 * (((A[:, None, :] - B[None, :, :]) / ell) ** 2).sum(-1))
    best = None
    for l1 in (0.2, 0.4, 0.8, 1.6):
        for l2 in (0.2, 0.4, 0.8, 1.6):
            for noise in (1e-4, 1e-3, 1e-2, 1e-1):
                L = np.linalg.cholesky(k(Z, Z, np.array([l1, l2])) + noise * np.eye(len(Z)))
                alpha = np.linalg.solve(L.T, np.linalg.solve(L, t))
                lml = -0.5 * t @ alpha - np.log(np.diag(L)).sum()  # log p(y|X) up to a constant
                if best is None or lml > best[0]:
                    best = (lml, np.array([l1, l2]), noise, L, alpha)
    _, ell, noise, L, alpha = best

    def predict(Xs):
        Ks = k(Z, scale(Xs), ell)
        v = np.linalg.solve(L, Ks)
        var = np.maximum(1e-12, 1 + noise - (v ** 2).sum(0))  # predictive variance incl. simulation noise
        return mu_y + sd_y * Ks.T @ alpha, sd_y * np.sqrt(var)
    predict.params = {"length_scales": ell.tolist(), "noise": noise}
    return predict


def fit_random_features(X, y, n_feat=300, ell=0.4, ridge=1e-3, seed=19):
    """Random Fourier features (Rahimi & Recht 2007): z(x) = sqrt(2/D) cos(Wx + b), then ridge regression."""
    rng = np.random.default_rng(seed)
    W, b = rng.normal(0, 1 / ell, (len(LO), n_feat)), rng.uniform(0, 2 * np.pi, n_feat)
    feats = lambda Xs: np.sqrt(2 / n_feat) * np.cos(scale(Xs) @ W + b)
    F = feats(X)
    coef = np.linalg.solve(F.T @ F + ridge * np.eye(n_feat), F.T @ (y - y.mean()))
    return lambda Xs: (y.mean() + feats(Xs) @ coef, None)


def design(seed=19):
    rng = np.random.default_rng(seed)
    X = latin_hypercube(N_TRAIN, rng)
    Xh = LO + rng.random((N_HOLD, 2)) * (HI - LO)  # holdout: fresh random points, fresh seeds
    y = np.array([expensive(l, m, 1000 + i) for i, (l, m) in enumerate(X)])
    yh = np.array([expensive(l, m, 2000 + i) for i, (l, m) in enumerate(Xh)])
    return X, y, Xh, yh


def fit_all(X, y):
    return {"polynomial": fit_poly(X, y), "gp-lite": fit_gp(X, y), "random features": fit_random_features(X, y)}


def what_if(model, lam, mu):
    """Answer a what-if question with the surrogate - only inside its validity envelope."""
    x = np.array([[lam, mu]])
    value, sd = model(x)
    inside = bool(np.all((x >= LO) & (x <= HI)))  # FIX: the training box is the envelope; never extrapolate
    if inside and (sd is None or sd[0] <= SD_MAX):
        return {"lam": lam, "mu": mu, "Wq": float(value[0]), "source": "surrogate"}
    runs = [expensive(lam, mu, 3000 + r) for r in range(FALLBACK_REPS)]  # FIX: outside, pay for the real model
    return {"lam": lam, "mu": mu, "Wq": float(np.mean(runs)), "source": "simulation (outside envelope)"}


def main():
    X, y, Xh, yh = design()
    models = fit_all(X, y)
    print(f"expensive model: M/M/3 DES, {CUSTOMERS:,} patients/run; {N_TRAIN} LHS training runs, {N_HOLD} holdout runs")
    print(f"{'surrogate':16s} {'holdout RMSE':>12s} {'max error':>9s}   (min of wait)")
    for name, model in models.items():
        err = model(Xh)[0] - yh
        print(f"{name:16s} {np.sqrt(np.mean(err ** 2)):12.3f} {np.max(np.abs(err)):9.3f}")
    exact_h = np.array([mmc_queue.erlang_c(3, l, m)["Wq"] for l, m in Xh])
    print(f"{'(noise floor)':16s} {np.sqrt(np.mean((yh - exact_h) ** 2)):12.3f}   = holdout runs vs Erlang C")
    mean, sd = models["gp-lite"](Xh)
    print(f"gp-lite 95% intervals cover {np.mean(np.abs(mean - yh) <= 1.96 * sd):.0%} of holdout runs; "
          f"params {models['gp-lite'].params}")
    print("WHAT-IF (Erlang C = exact answer for this M/M/3; * = answered by the simulation, not the surrogate):")
    for lam, mu in ((2.0, 1.0), (2.2 * 1.1, 1.0), (2.7, 0.95)):
        exact = mmc_queue.erlang_c(3, lam, mu)["Wq"]
        answers = "  ".join(f"{n} {r['Wq']:6.3f}{' ' if r['source'] == 'surrogate' else '*'}"
                            for n, r in ((n, what_if(m, lam, mu)) for n, m in models.items()))
        gp_sd = models["gp-lite"](np.array([[lam, mu]]))[1][0]
        print(f"  lam={lam:.2f} mu={mu:.2f} (rho {lam / (3 * mu):.2f}): exact {exact:6.3f} | {answers} | gp sd {gp_sd:.3f}")


if __name__ == "__main__":
    main()
