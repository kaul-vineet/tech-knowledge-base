"""buildTask solution (lesson 13): report standard errors and correlations; refuse to call a fit 'identified'.

python solution/param_report.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import calibrate as cal  # noqa: E402


def param_report(model, t, y, p0, names, max_rel_se=0.5):
    """Fit, then cov = s^2 (J^T J)^-1 (Gauss-Newton approximation, NIST 4.1.4.2): se and correlation per parameter."""
    p, J = cal.gauss_newton(model, t, y, p0)
    r = model(t, p) - y
    s2 = float(r @ r) / (len(y) - len(p))  # residual variance with n - k degrees of freedom
    cov = s2 * np.linalg.pinv(J.T @ J)
    se = np.sqrt(np.abs(np.diag(cov)))
    corr = cov / np.outer(se, se)
    np.fill_diagonal(corr, 0.0)
    i, j = np.unravel_index(np.abs(corr).argmax(), corr.shape)
    rel = se / np.maximum(np.abs(p), 1e-12)
    return {"params": dict(zip(names, np.round(p, 3).tolist())), "rel_se": dict(zip(names, np.round(rel, 2).tolist())),
            "worst_pair": (names[i], names[j], round(float(corr[i, j]), 3)),
            "identifiable": bool(np.all(rel < max_rel_se))}  # every parameter pinned to within 50%


if __name__ == "__main__":
    y = cal.observed()
    t, yc = cal.T_HOURS[cal.CAL], y[cal.CAL]
    fixed = lambda tt, q: cal.two_exp(tt, np.r_[12.0, q])  # T_inf measured by an outdoor sensor, not fitted
    for label, rep in [
        ("one-exp, 0-8 h", param_report(cal.one_exp, t, yc, [yc[-1], yc[0] - yc[-1], 2.0], ["T_inf", "A", "tau"])),
        ("two-exp, 0-8 h", param_report(cal.two_exp, t, yc, [yc[-1], 5, 1, 5, 6],
                                        ["T_inf", "A", "tau_air", "B", "tau_wall"])),
        ("two-exp, T_inf=12 fixed", param_report(fixed, t, yc, [5, 1, 5, 6], ["A", "tau_air", "B", "tau_wall"]))]:
        print(f"{label:24s} identifiable={rep['identifiable']!s:5s} worst corr {rep['worst_pair']}  "
              f"rel. s.e. {rep['rel_se']}")
