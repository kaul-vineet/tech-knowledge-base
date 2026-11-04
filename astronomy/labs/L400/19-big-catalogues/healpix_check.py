"""Library equivalent (pending-ci; healpy has no Windows wheels): HEALPix candidates + the same exact test.

healpy.query_disc(nside, vec, radius_rad, inclusive=True) returns every pixel touching the cone; sources in
those pixels are the candidates. The result must equal brute force, like the zones index.
pip install -r ../requirements.txt   (healpy 1.20.1, macOS/Linux)        python healpix_check.py
"""
import healpy as hp
import numpy as np

import catalog

NSIDE = 256  # 786 432 equal-area pixels of ~0.23 deg


def build(cat):
    pix = hp.ang2pix(NSIDE, cat["ra"], cat["dec"], lonlat=True)
    order = np.argsort(pix, kind="stable")
    return pix[order], order, catalog.unit(cat["ra"], cat["dec"])


def query(index, cat, ra, dec, radius):
    pix_sorted, order, xyz = index
    pixels = hp.query_disc(NSIDE, catalog.unit(ra, dec), np.radians(radius), inclusive=True)
    lo, hi = np.searchsorted(pix_sorted, pixels), np.searchsorted(pix_sorted, pixels, side="right")
    idx = order[np.concatenate([np.arange(a, b) for a, b in zip(lo, hi)])] if len(pixels) else np.array([], int)
    return np.sort(cat["id"][idx[xyz[idx] @ catalog.unit(ra, dec) >= np.cos(np.radians(radius))]])


def wrong_cones(n=200_000):
    cat, cones = catalog.make_catalogue(n), catalog.test_cones()
    brute, index = catalog.Brute(cat), build(cat)
    return sum(not np.array_equal(query(index, cat, *c), brute.query(*c)) for c in cones)


if __name__ == "__main__":
    print("HEALPix cones that differ from brute force:", wrong_cones())
