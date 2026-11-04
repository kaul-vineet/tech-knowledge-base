"""Astropy 8.0.2 LombScargle equivalent of periods.py (pending-ci). python periods_astropy.py

lightkurve (LightCurve.to_periodogram) wraps the same astropy class for Kepler/TESS data.
"""
import numpy as np
from astropy.timeseries import LombScargle

import periods as pr


def compare():
    t = pr.sample_times()
    y = pr.variable_star(t)
    f = pr.frequency_grid(t)
    theirs = LombScargle(t, y, fit_mean=False, center_data=True, normalization="standard").power(f)
    return float(np.abs(theirs - pr.lomb_scargle(t, y, f)).max())  # classical LS = no floating mean


if __name__ == "__main__":
    print(f"max |astropy - numpy| power difference: {compare():.2e}")
