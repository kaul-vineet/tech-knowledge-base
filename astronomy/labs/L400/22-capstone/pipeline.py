"""Capstone pipeline stages: load -> detrend -> BLS-lite search -> vetting -> fit (lesson 15 model + MCMC).

BLS-lite (Kovacs, Zucker & Mazeh 2002 idea): fold at each trial period, bin the phase, slide boxes of several
durations, and score depth / its error. SDE = (best - mean) / std of the periodogram peaks.
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "L300" / "15-honest-uncertainty"))
import mcmc  # noqa: E402  (lesson 15: Metropolis with a free noise scale)
import transit_fit as tf  # noqa: E402  (lesson 15: trapezoid model + Levenberg-Marquardt)

WINDOW_D = 0.75  # running-median detrending window (ADR 0001)
DURATIONS_H = (1.5, 2.5, 3.5, 4.5)
FREQ = np.linspace(1 / 14.0, 1 / 0.6, 6000)  # cycles per day
SNR_MIN, SDE_MIN, ODD_EVEN_SIG, SECONDARY_SIG = 10.0, 7.0, 3.0, 3.0  # ADR 0002


def load(path):
    a = np.loadtxt(path, delimiter=",", skiprows=1, encoding="utf-8")
    return a[:, 0], a[:, 1], a[:, 2]


def detrend(t, f, window=WINDOW_D, mask=None):
    """Divide by a running median (follows drifts, spots and ramps). mask: points to leave OUT of the median -
    the in-transit points of a found candidate, so the trend does not eat part of the transit depth."""
    lo, hi = np.searchsorted(t, t - window / 2), np.searchsorted(t, t + window / 2)
    use = np.ones(t.size, bool) if mask is None else ~mask
    trend = np.array([np.median(f[a:b][use[a:b]]) if use[a:b].any() else np.median(f[a:b]) for a, b in zip(lo, hi)])
    return f / trend


def in_transit(t, c, factor=1.5):
    p = c["period_d"]
    return np.abs((t - c["t0_d"] + p / 2) % p - p / 2) * 24 < factor * c["duration_h"] / 2


def bls(t, f, freq=FREQ, durations=DURATIONS_H):
    """Returns per-frequency best SNR and the best (period, t0, duration_h, depth, snr, sde)."""
    sigma = 1.4826 * np.median(np.abs(f - np.median(f)))
    best_snr, best = np.zeros(freq.size), None
    for k, nu in enumerate(freq):
        period = 1 / nu
        nb = max(int(period * 24 / 0.25), 8)  # 15-minute phase bins
        b = np.minimum((t * nu % 1.0 * nb).astype(int), nb - 1)
        cnt, s = np.bincount(b, minlength=nb), np.bincount(b, weights=f - 1.0, minlength=nb)
        c2, s2 = np.concatenate([cnt, cnt]), np.concatenate([s, s])  # wrap-around boxes
        cc, cs = np.concatenate([[0], np.cumsum(c2)]), np.concatenate([[0], np.cumsum(s2)])
        for d in durations:
            w = max(int(round(d / 0.25)), 1)
            n_in = cc[w:nb + w] - cc[:nb]
            depth = -(cs[w:nb + w] - cs[:nb]) / np.maximum(n_in, 1)
            snr = depth / (sigma / np.sqrt(np.maximum(n_in, 1)))
            j = int(np.argmax(snr))
            if snr[j] > best_snr[k]:
                best_snr[k] = snr[j]
                if best is None or snr[j] > best[4]:
                    best = (period, (j + w / 2) / nb * period, d, float(depth[j]), float(snr[j]))
    sde = (best[4] - best_snr.mean()) / best_snr.std()
    return best_snr, {"period_d": best[0], "t0_d": best[1], "duration_h": best[2], "depth": best[3],
                      "snr": round(best[4], 2), "sde": round(float(sde), 2)}


def box_depth(t, f, period, t0, dur_h, select=None):
    """Mean depth (and its error) of points inside the box; select picks e.g. odd or even epochs."""
    phase = (t - t0 + period / 2) % period - period / 2
    inside = np.abs(phase) * 24 < dur_h / 2
    if select is not None:
        inside &= select(np.round((t - t0) / period).astype(int))
    sigma = 1.4826 * np.median(np.abs(f - np.median(f)))
    n = max(int(inside.sum()), 1)
    return float(1.0 - f[inside].mean()) if inside.any() else 0.0, sigma / np.sqrt(n), int(inside.sum())


def vet(t, f, c):
    """Code decides: detection thresholds, >= 2 transits, odd/even depths, secondary eclipse, duration."""
    p, t0, d = c["period_d"], c["t0_d"], c["duration_h"]
    reasons = []
    if c["snr"] < SNR_MIN or c["sde"] < SDE_MIN:
        reasons.append(f"weak signal (SNR {c['snr']}, SDE {c['sde']})")
    epochs = {int(round((x - t0) / p)) for x in t[np.abs((t - t0 + p / 2) % p - p / 2) * 24 < d / 2]}
    if len(epochs) < 2:
        reasons.append(f"only {len(epochs)} transit(s) observed")
    odd, eo, _ = box_depth(t, f, p, t0, d, lambda e: e % 2 == 1)
    even, ee, _ = box_depth(t, f, p, t0, d, lambda e: e % 2 == 0)
    if abs(odd - even) > ODD_EVEN_SIG * np.hypot(eo, ee):
        reasons.append(f"odd/even depths differ ({odd * 1e6:.0f} vs {even * 1e6:.0f} ppm)")
    sec, es, _ = box_depth(t, f, p, t0 + p / 2, d)
    if sec > SECONDARY_SIG * es:
        reasons.append(f"secondary eclipse at phase 0.5 ({sec * 1e6:.0f} ppm)")
    # DERIVED duration bound (not quoted): a central transit on a circular orbit lasts T14 ~ (P / pi)(R* / a) in the
    # small-angle limit of Seager & Mallen-Ornelas (2003, b = 0, Rp << R*); Kepler's third law for one solar mass gives
    # a = 1 au (P / 1 yr)^(2/3); with R_sun / au = 0.00465: T14 ~ (8766 h / pi)(0.00465)(P / 1 yr)^(1/3) = 13.0 h (P / 1 yr)^(1/3).
    # A central transit is the longest one, so this is an upper bound; +50 % margin for larger stars and eccentric orbits.
    t_max_h = 1.5 * 13.0 * (p / 365.25) ** (1 / 3)
    if d > t_max_h:
        reasons.append(f"duration {d} h too long for P = {p:.2f} d")
    return ("planet_candidate" if not reasons else "rejected"), reasons


def fit(t, f, c, steps=6000):
    """Fold on the BLS ephemeris, then lesson 15: LM fit of the trapezoid and Metropolis with free noise scale."""
    p = c["period_d"]
    phase_h = ((t - c["t0_d"] + p / 2) % p - p / 2) * 24
    near = np.abs(phase_h) < 2.5 * c["duration_h"]
    x, y = phase_h[near], f[near]
    best = tf.fit_lm(y, p0=(0.0, max(c["depth"], 1e-4), c["duration_h"], 0.3), t=x)
    post, acc, tau = mcmc.run(y, steps=steps, burn=steps // 4, t=x, p=best)
    lo, med, hi = np.percentile(post[:, 1], [15.87, 50, 84.13])
    return {"depth_ppm": round(float(med) * 1e6), "depth_err_ppm": round(float(hi - lo) / 2 * 1e6),
            "t14_h": round(float(np.median(post[:, 2])), 2), "acceptance": round(acc, 3), "tau": round(tau, 1)}
