"""Astropy 8.0.2 SkyCoord.match_to_catalog_sky and SciPy 1.18.1 cKDTree equivalents (pending-ci).

python crossmatch_astropy.py
"""
import astropy.units as u
import numpy as np
from astropy.coordinates import SkyCoord
from scipy.spatial import cKDTree

import crossmatch as cm


def compare(radius_arcsec=1.0):
    a, b, _ = cm.make_catalogues()
    ours, _, _ = cm.match(a, b, radius_arcsec)
    ca, cb = SkyCoord(a[0] * u.deg, a[1] * u.deg), SkyCoord(b[0] * u.deg, b[1] * u.deg)
    idx, d2d, _ = cb.match_to_catalog_sky(ca)  # nearest A for every B (astropy also uses a k-d tree)
    astro = np.where(d2d.arcsec <= radius_arcsec, idx, -1)
    chord, j = cKDTree(cm.unit_vectors(*a)).query(cm.unit_vectors(*b))
    kd = np.where(chord <= 2 * np.sin(radius_arcsec * cm.ARCSEC / 2), j, -1)
    return ours, astro, kd


if __name__ == "__main__":
    ours, astro, kd = compare()
    print(f"same pairs as astropy: {np.array_equal(ours, astro)}; same as scipy cKDTree: {np.array_equal(ours, kd)}")
