"""photutils 3.1.1 equivalent of photometry.py (pending-ci). python photometry_photutils.py"""
import numpy as np
from photutils.aperture import ApertureStats, CircularAnnulus, CircularAperture, aperture_photometry

import photometry as ph


def compare():
    img = ph.make_image()
    pos = [(x, y) for x, y, _ in ph.STARS]  # photutils uses the same (x, y) = (column, row) pixel centres
    aper, ann = CircularAperture(pos, r=6.0), CircularAnnulus(pos, r_in=10.0, r_out=15.0)
    bkg = ApertureStats(img, ann).median  # median per pixel in the annulus, like photometry.py
    table = aperture_photometry(img, aper, method="subpixel", subpixels=5)
    net = np.asarray(table["aperture_sum"]) - bkg * aper.area_overlap(img, method="subpixel", subpixels=5)
    return [(ph.measure(img, x, y)["net"], n) for (x, y), n in zip(pos, net)]


if __name__ == "__main__":
    for ours, theirs in compare():
        print(f"ours {ours:9.1f} photutils {theirs:9.1f}")
