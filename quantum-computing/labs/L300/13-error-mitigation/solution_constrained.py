"""Build-task solution for lab 13: readout mitigation that always returns a real probability distribution.

Run: python solution_constrained.py
Constrained least squares: minimise ||M p - p_noisy||^2 subject to p >= 0 and sum(p) = 1, solved by projected
gradient descent onto the probability simplex (start from the plain inverse, projected). Same idea as
mthree's nearest_probability_distribution(); clipping + renormalising is a cruder shortcut (tryIt 2).
"""
import numpy as np

import mitigation_lab as lab


def project_to_simplex(v):
    """Euclidean projection onto {p >= 0, sum p = 1} (sort-based algorithm)."""
    u = np.sort(v)[::-1]
    css = np.cumsum(u) - 1
    k = np.nonzero(u - css / np.arange(1, len(v) + 1) > 0)[0][-1]
    return np.maximum(v - css[k] / (k + 1), 0)


def mitigate(p_noisy, m_est, iters=500):
    p = project_to_simplex(np.linalg.solve(m_est, p_noisy))
    step = 1 / np.linalg.norm(m_est, 2) ** 2                  # 1 / Lipschitz constant of the gradient
    for _ in range(iters):
        nxt = project_to_simplex(p - step * m_est.T @ (m_est @ p - p_noisy))
        if np.abs(nxt - p).max() < 1e-12:                      # converged
            return nxt
        p = nxt
    return p


def mean_tvd(fn, cal_shots, shots, seeds=200):
    ideal, out = lab.true_bell(), []
    for seed in range(seeds):
        rng = np.random.default_rng(seed)
        m_est = lab.calibrate(cal_shots, rng)
        out.append(lab.tvd(fn(lab.measure(ideal, shots, rng), m_est), ideal))
    return round(float(np.mean(out)), 4)


if __name__ == "__main__":
    rng = np.random.default_rng(11)
    for cal_shots, shots in ((4000, 4000), (100, 200)):
        m_est = lab.calibrate(cal_shots, rng)
        p = mitigate(lab.measure(lab.true_bell(), shots, rng), m_est)
        print(f"cal {cal_shots}/run {shots}: {np.round(p, 4).tolist()} min {p.min():.4f} sampling ok: {rng.choice(4, p=p) >= 0}")
    for cal_shots, shots in ((100, 200), (4000, 4000)):
        print(f"mean TVD over 200 seeds, cal {cal_shots}/run {shots}: raw-inverse {mean_tvd(lab.mitigate, cal_shots, shots)}"
              f" constrained {mean_tvd(mitigate, cal_shots, shots)}")
