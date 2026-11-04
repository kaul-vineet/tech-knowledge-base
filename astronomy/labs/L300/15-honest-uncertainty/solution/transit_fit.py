"""L300 fitting with honest uncertainty: one transit, a trapezoid model, least squares, bootstrap and coverage.

SYNTHETIC light curve: 8 h at 2-min cadence, depth 1.0 %, duration 2.5 h, ingress 0.3 h, mid-time 0.12 h.
The photometry pipeline reports flux_err = 0.0010 per point, but the real scatter is 0.0020 (scintillation,
unmodelled systematics): a common, realistic mismatch. The question is not the best fit - it is the error bar.
python solution/transit_fit.py
"""
import json

import numpy as np

TRUE = np.array([0.12, 0.010, 2.5, 0.3])  # t0 [h], depth, T14 [h], T12 [h]
NAMES = ["t0_h", "depth", "T14_h", "T12_h"]
SIGMA_REPORTED, SIGMA_TRUE = 0.0010, 0.0020
T = np.arange(-4.0, 4.0, 2 / 60)  # 240 points


def model(p, t=T):
    """Trapezoid transit (Seager & Mallen-Ornelas 2003 shape): flat bottom between 2nd and 3rd contact."""
    t0, depth, t14, t12 = p
    x = np.abs(t - t0)
    half = t14 / 2
    ramp = np.clip((half - x) / max(t12, 1e-6), 0.0, 1.0)  # 0 outside, 1 on the flat bottom
    return 1.0 - depth * ramp


def make_data(seed=15):
    rng = np.random.default_rng(seed)
    return model(TRUE) + rng.normal(0.0, SIGMA_TRUE, T.size)


def jacobian(p, h=1e-6, t=T):
    f0 = model(p, t)
    return np.column_stack([(model(p + h * np.eye(4)[k], t) - f0) / h for k in range(4)])


def fit_lm(y, p0=(0.0, 0.008, 2.3, 0.4), iters=60, t=T):
    """Levenberg-Marquardt: damped Gauss-Newton on chi^2 = sum((y - model)/sigma)^2 (t: any time grid)."""
    p, lam = np.array(p0, float), 1e-3
    cost = np.sum((y - model(p, t)) ** 2)
    for _ in range(iters):
        J, r = jacobian(p, t=t), y - model(p, t)
        A = J.T @ J
        step = np.linalg.solve(A + lam * np.diag(np.diag(A)), J.T @ r)
        trial = p + step
        trial[3] = np.clip(trial[3], 0.01, trial[2] / 2)  # ingress cannot exceed half the duration
        new = np.sum((y - model(trial, t)) ** 2)
        if new < cost:
            p, cost, lam = trial, new, lam / 3
        else:
            lam *= 4
    return p


def uncertainty(y, p):
    """1-sigma errors from the curvature of chi^2: cov = (J^T W J)^-1 with W = 1/sigma^2."""
    J, r = jacobian(p), y - model(p)
    cov = np.linalg.inv(J.T @ J / SIGMA_REPORTED ** 2)
    chi2_red = np.sum((r / SIGMA_REPORTED) ** 2) / (y.size - p.size)
    return np.sqrt(np.diag(cov) * max(chi2_red, 1.0))  # the residuals say sigma is sqrt(chi2_red) x larger


def bootstrap(y, p, n=300, seed=1):
    """Residual bootstrap: refit fake data = best model + resampled residuals (with replacement)."""
    rng, res, best = np.random.default_rng(seed), y - model(p), model(p)
    fits = np.array([fit_lm(best + rng.choice(res, res.size), p0=p, iters=25) for _ in range(n)])
    return fits.std(axis=0, ddof=1)


def coverage(n=200, seed0=1000):
    """Fraction of seeded datasets whose +/-1 sigma interval contains the TRUE value (should be ~68%)."""
    hits = np.zeros(4)
    for k in range(n):
        y = make_data(seed0 + k)
        p = fit_lm(y)
        hits += np.abs(p - TRUE) <= uncertainty(y, p)
    return hits / n


if __name__ == "__main__":
    y = make_data()
    p = fit_lm(y)
    chi2_red = float(np.sum(((y - model(p)) / SIGMA_REPORTED) ** 2) / (T.size - 4))
    err, boot = uncertainty(y, p), bootstrap(y, p)
    for k, name in enumerate(NAMES):
        print(json.dumps({"param": name, "true": float(TRUE[k]), "fit": round(float(p[k]), 5),
                          "sigma_formal": round(float(err[k]), 5), "sigma_bootstrap": round(float(boot[k]), 5)}))
    print(f"reduced chi^2 with the reported flux_err: {chi2_red:.2f}")
    print("1-sigma coverage over 200 seeded datasets:", dict(zip(NAMES, coverage().round(3).tolist())))
