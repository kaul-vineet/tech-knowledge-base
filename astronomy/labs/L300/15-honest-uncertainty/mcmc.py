"""Metropolis MCMC for the lesson 15 transit, with the noise level as a FREE parameter (sigma = s x flux_err).

Sampling the noise scale s is the Bayesian version of 'let the residuals tell you sigma' (Hogg, Bovy & Lang 2010).
Proposal covariance from the least-squares fit (scaled 2.38^2/d); convergence via the integrated autocorrelation
time (Sokal window, C = 5, as in the emcee docs). emcee's affine-invariant sampler: fit_emcee.py (pending-ci).
python mcmc.py
"""
import json

import numpy as np

import transit_fit as tf


def log_prob(q, y, t=None):
    t0, depth, t14, t12, ln_s = q
    if not (abs(t0) < 1 and 0 < depth < 0.05 and 0.5 < t14 < 5 and 0.01 < t12 < t14 / 2 and -1 < ln_s < 3):
        return -np.inf  # flat priors inside physical bounds
    sigma = np.exp(ln_s) * tf.SIGMA_REPORTED
    r = y - tf.model(q[:4], tf.T if t is None else t)
    return -0.5 * np.sum((r / sigma) ** 2) - y.size * np.log(sigma)


def autocorr_time(x, c=5.0):
    """Integrated autocorrelation time of one chain (FFT autocovariance, window M >= c * tau)."""
    x = x - x.mean()
    n = 1 << (2 * x.size - 1).bit_length()
    f = np.fft.rfft(x, n)
    acf = np.fft.irfft(f * np.conj(f))[: x.size]
    acf /= acf[0]
    taus = 2.0 * np.cumsum(acf) - 1.0
    window = np.arange(taus.size) < c * taus
    return float(taus[np.argmin(window)] if not window.all() else taus[-1])


def run(y, steps=20_000, burn=5_000, seed=3, t=None, p=None):
    """Metropolis on (t0, depth, T14, T12, ln s); t / p let other labs (the capstone) reuse it on folded data."""
    t = tf.T if t is None else t
    p = tf.fit_lm(y, t=t) if p is None else np.asarray(p, float)
    J = tf.jacobian(p, t=t)
    cov4 = np.linalg.inv(J.T @ J) * np.sum((y - tf.model(p, t)) ** 2) / (y.size - 4)
    prop = np.zeros((5, 5))
    prop[:4, :4], prop[4, 4] = cov4, 0.05 ** 2
    L = np.linalg.cholesky(prop * 2.38 ** 2 / 5)
    rng = np.random.default_rng(seed)
    q = np.append(p, np.log(2.0))
    lp, chain, accepted = log_prob(q, y, t), np.empty((steps, 5)), 0
    for i in range(steps):
        trial = q + L @ rng.normal(size=5)
        lt = log_prob(trial, y, t)
        if np.log(rng.uniform()) < lt - lp:  # Metropolis rule
            q, lp, accepted = trial, lt, accepted + 1
        chain[i] = q
    post = chain[burn:]
    tau = max(autocorr_time(post[:, k]) for k in range(5))
    return post, accepted / steps, tau


if __name__ == "__main__":
    y = tf.make_data()
    post, acc, tau = run(y)
    lo, med, hi = np.percentile(post, [15.87, 50, 84.13], axis=0)
    for k, name in enumerate(tf.NAMES + ["noise_scale_s"]):
        f = np.exp if k == 4 else (lambda v: v)
        print(json.dumps({"param": name, "median": round(float(f(med[k])), 5),
                          "minus": round(float(f(med[k]) - f(lo[k])), 5), "plus": round(float(f(hi[k]) - f(med[k])), 5)}))
    print(f"acceptance {acc:.3f}; autocorrelation time {tau:.0f} steps; effective samples {len(post) / tau:.0f}")
