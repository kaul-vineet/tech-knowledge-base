"""L400 model comparison: does this rotation curve need a dark-matter halo - and how do we decide?

Four mass models are fitted by weighted least squares (Levenberg-Marquardt): disk only (1 parameter), disk +
cored halo (3), disk + NFW halo (3), disk + cored halo + a cubic 'wiggle' term (6). Then one is SELECTED.
Options: A lowest chi^2 | B BIC = chi^2 + k ln n (Schwarz 1978) | C hold out the outer radii (R > 20 kpc).
python compare.py
"""
import json

import numpy as np

import galaxy as g

MODELS = {  # name: (V^2 function of radius and parameters, starting values, lower bounds)
    "disk only": (lambda r, p: g.v_disk2(r, p[0]), [1.0], [0.05]),
    "disk + cored halo": (lambda r, p: g.v_disk2(r, p[0]) + g.v_iso2(r, p[1] * 1e7, p[2]), [0.8, 2.0, 3.0],
                          [0.05, 0.01, 0.2]),
    "disk + NFW halo": (lambda r, p: g.v_disk2(r, p[0]) + g.v_nfw2(r, p[1], p[2]), [0.8, 150.0, 8.0],
                        [0.05, 20.0, 1.0]),
    "disk + halo + wiggles": (lambda r, p: g.v_disk2(r, p[0]) + g.v_iso2(r, p[1] * 1e7, p[2])
                              + 1e3 * (p[3] * (r / 30) + p[4] * (r / 30) ** 2 + p[5] * (r / 30) ** 3),
                              [0.8, 2.0, 3.0, 0.0, 0.0, 0.0], [0.05, 0.01, 0.2, -1e9, -1e9, -1e9]),
}


def fit(name, r, v, err, iters=80):
    f, p0, lo = MODELS[name]
    p, lam = np.array(p0, float), 1e-2
    model = lambda q: np.sqrt(np.clip(f(r, q), 1e-9, None))  # noqa: E731
    chi2 = np.sum(((v - model(p)) / err) ** 2)
    for _ in range(iters):
        J = np.column_stack([(model(p + 1e-6 * max(1, abs(p[k])) * np.eye(len(p))[k]) - model(p))
                             / (1e-6 * max(1, abs(p[k]))) for k in range(len(p))]) / err[:, None]
        res = (v - model(p)) / err
        A = J.T @ J
        trial = np.maximum(p + np.linalg.solve(A + lam * np.diag(np.diag(A)), J.T @ res), lo)
        new = np.sum(((v - model(trial)) / err) ** 2)
        p, chi2, lam = (trial, new, lam / 3) if new < chi2 else (p, chi2, lam * 4)
    return p, float(chi2), model


def runs_z(resid):
    """Wald-Wolfowitz runs test on residual signs (NIST e-Handbook 1.3.5.13): |Z| > 1.96 -> structure left."""
    s = resid > 0
    n1, n2 = int(s.sum()), int((~s).sum())
    runs = 1 + int(np.sum(s[1:] != s[:-1]))
    mean = 2 * n1 * n2 / (n1 + n2) + 1
    var = 2 * n1 * n2 * (2 * n1 * n2 - n1 - n2) / ((n1 + n2) ** 2 * (n1 + n2 - 1))
    return (runs - mean) / np.sqrt(var)


def table(r, v, err):
    rows = []
    for name in MODELS:
        p, chi2, model = fit(name, r, v, err)
        k, n = len(p), len(r)
        rows.append({"model": name, "k": k, "chi2": round(chi2, 2), "bic": round(float(chi2 + k * np.log(n)), 2),
                     "aic": round(chi2 + 2 * k, 2), "runs_z": round(float(runs_z(v - model(p))), 2),
                     "params": [round(float(x), 3) for x in p]})
    return rows


def holdout_choice(r, v, err, cut=20.0):
    """Option C: fit on R <= cut, pick the model with the lowest chi^2 on the outer, unseen radii."""
    inner, scores = r <= cut, {}
    for name in MODELS:
        p, _, _ = fit(name, r[inner], v[inner], err[inner])
        f = MODELS[name][0]
        scores[name] = float(np.sum(((v[~inner] - np.sqrt(np.clip(f(r[~inner], p), 1e-9, None))) / err[~inner]) ** 2))
    return min(scores, key=scores.get)


def option_rates(seeds=range(100, 150)):
    """How often each selection rule picks each model over 50 seeded data sets (truth: disk + cored halo)."""
    rates = {"A chi2": {}, "B BIC": {}, "C holdout R>20": {}}
    for s in seeds:
        v, err = g.observed(seed=s)
        rows = table(g.R, v, err)
        for opt, pick in (("A chi2", min(rows, key=lambda x: x["chi2"])["model"]),
                          ("B BIC", min(rows, key=lambda x: x["bic"])["model"]),
                          ("C holdout R>20", holdout_choice(g.R, v, err))):
            rates[opt][pick] = rates[opt].get(pick, 0) + 1
    return rates


def select(r, v, err):
    """Pick the model to publish."""
    rows = table(r, v, err)
    return min(rows, key=lambda row: row["chi2"])["model"], rows


if __name__ == "__main__":
    v, err = g.observed()
    best, rows = select(g.R, v, err)
    for row in rows:
        print(json.dumps(row))
    print("select() picks:", best)
    for opt, picks in option_rates().items():
        print(json.dumps({"option": opt, "picks_over_50_datasets": dict(sorted(picks.items()))}))
