"""Astropy 8.0.2 io.fits + wcs equivalent of fitslite.py (pending-ci). python fits_astropy.py"""
import tempfile
from pathlib import Path

import numpy as np
from astropy.io import fits
from astropy.wcs import WCS

import fitslite as fl
from field import synthetic_field


def compare():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "star_field.fits"
        fl.write_fits(path, synthetic_field(), fl.WCS)
        with fits.open(path) as hdul:  # astropy must accept our hand-written file
            hdul.verify("exception")
            data, header = hdul[0].data.copy(), hdul[0].header
        w = WCS(header)
        yy, xx = np.mgrid[1:65:7, 1:65:7].astype(float)
        ra_a, dec_a = w.all_pix2world(xx, yy, 1)  # origin=1: FITS 1-based pixels, like fitslite
        ra_o, dec_o = fl.pixel_to_sky(fl.WCS, xx, yy)
        err = np.hypot((ra_a - ra_o) * np.cos(np.radians(dec_o)), dec_a - dec_o).max() * 3600
        return bool(np.array_equal(data, synthetic_field())), float(err)


if __name__ == "__main__":
    same, err = compare()
    print(f"astropy reads identical data: {same}; max WCS difference {err:.2e} arcsec")
