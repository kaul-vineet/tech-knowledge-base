"""L200 Light curves and periods: Lomb-Scargle periodogram in numpy; a pulsating variable vs a transiting planet.

Synthetic and seeded (not real stars): 30 nights from one ground site, 8 h per night every 10 min, ~30% of
nights clouded out. Variable: sawtooth, P = 0.5671 d, 0.6 mag. Transit: P = 3.2127 d, 1% deep, 2.4 h long.
python periods.py               # add --export to write variable.csv / transit.csv (for TOPCAT)
"""
import sys

import numpy as np

P_VAR, P_TRANSIT = 0.5671, 3.2127


def sample_times(seed=10, nights=30):
    rng = np.random.default_rng(seed)
    clear = np.flatnonzero(rng.random(nights) > 0.3)
    t = (clear[:, None] + 0.25 + np.arange(48)[None, :] / 144).ravel()  # 48 points x 10 min each clear night
    return t + rng.normal(0, 0.001, t.size)  # small jitter in the time stamps


def variable_star(t, seed=11):
    phase = (t / P_VAR) % 1.0
    shape = np.where(phase < 0.15, 1 - phase / 0.15, (phase - 0.15) / 0.85)  # fast rise, slow decline
    return 12.0 + 0.6 * shape + np.random.default_rng(seed).normal(0, 0.02, t.size)


def transit_star(t, seed=12):
    phase = ((t / P_TRANSIT) + 0.5) % 1.0 - 0.5
    flux = np.where(np.abs(phase * P_TRANSIT) < 0.05, 0.99, 1.0)  # box-shaped dip, 0.1 d = 2.4 h
    return 11.0 - 2.5 * np.log10(flux) + np.random.default_rng(seed).normal(0, 0.003, t.size)


def lomb_scargle(t, y, freqs):
    """Classical Lomb-Scargle (Scargle 1982), 'standard' normalisation: power in [0, 1]."""
    y = y - y.mean()
    w = 2 * np.pi * freqs[:, None]
    tau = np.arctan2(np.sin(2 * w * t).sum(1), np.cos(2 * w * t).sum(1))[:, None] / (2 * w)  # time offset
    c, s = np.cos(w * (t - tau)), np.sin(w * (t - tau))  # makes the sine and cosine terms orthogonal
    power = (c @ y) ** 2 / (c * c).sum(1) + (s @ y) ** 2 / (s * s).sum(1)
    return power / (y @ y)


def frequency_grid(t, f_min=0.1, f_max=5.0, oversample=10):
    return np.arange(f_min, f_max, 1 / (oversample * (t.max() - t.min())))


def skewness(y):
    d = y - y.mean()
    return float((d**3).mean() / (d**2).mean() ** 1.5)  # transits: rare, one-sided dips -> large positive skew in mag


def bootstrap_fap(t, y, freqs, n=200, seed=0):
    raise NotImplementedError("build task: false-alarm probability by shuffling the magnitudes")


def analyse(t, y):
    f = frequency_grid(t)
    p = lomb_scargle(t, y, f)
    top = np.argsort(p)[::-1]
    best = 1 / f[top[0]]
    second = next(1 / f[i] for i in top if abs(1 / f[i] - best) / best > 0.05)  # next peak that is not the same one
    return {"best_period_days": best, "power": float(p[top[0]]), "second_period_days": second, "skew": skewness(y)}


def main():
    t = sample_times()
    print(f"{t.size} points over {t.max() - t.min():.1f} d ({np.unique(np.floor(t)).size} clear nights)")
    for name, y, true_p in (("variable", variable_star(t), P_VAR), ("transit", transit_star(t), P_TRANSIT)):
        r = analyse(t, y)
        print(f"{name:<8} true P {true_p:.4f} d | LS best {r['best_period_days']:.4f} d (power {r['power']:.3f}) | "
              f"next peak {r['second_period_days']:.4f} d | skew {r['skew']:+.2f}")
        if "--export" in sys.argv:
            np.savetxt(f"{name}.csv", np.column_stack([t, y]), delimiter=",", header="t_days,mag", comments="", fmt="%.6f")
    print(f"1-day alias of the variable: 1 / (1/{P_VAR} - 1) = {1 / (1 / P_VAR - 1):.4f} d")


if __name__ == "__main__":
    main()
