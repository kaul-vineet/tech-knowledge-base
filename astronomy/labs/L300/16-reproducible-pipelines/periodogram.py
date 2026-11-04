"""Classical Lomb-Scargle periodogram in numpy (normalised power 0..1), for unevenly sampled light curves.
astropy.timeseries.LombScargle(t, y).power(f) gives the same 'standard' normalisation (pending-ci check)."""
import numpy as np


def lomb_scargle(t, y, freq):
    y = y - y.mean()
    w = 2 * np.pi * freq[:, None]
    tau = np.arctan2(np.sum(np.sin(2 * w * t), axis=1), np.sum(np.cos(2 * w * t), axis=1)) / (2 * w[:, 0])
    arg = w * (t - tau[:, None])
    c, s = np.cos(arg), np.sin(arg)
    p = (c @ y) ** 2 / np.sum(c * c, axis=1) + (s @ y) ** 2 / np.sum(s * s, axis=1)
    return p / np.sum(y * y)  # astropy "standard" normalisation: 1 = perfect sinusoid fit
