"""Library equivalent (pending-ci): fit the WCS of the matched stars with astropy.wcs.utils.fit_wcs_from_points.

pip install -r ../requirements.txt   (astropy 8.0.2)        python platesolve_astropy.py
Real images: astrometry.net's solve-field does the blind search + verification (see the lesson's learningTools).
"""
import importlib.util
from pathlib import Path

import astropy.units as u
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.wcs.utils import fit_wcs_from_points, proj_plane_pixel_scales

import fields

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("platesolve_fixed", HERE / "solution" / "platesolve.py")
ps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ps)


def astropy_wcs(name):
    """Match with our solver, then let astropy fit a TAN WCS to the same pairs (FITS 1-based pixels)."""
    det, cat = fields.detections(name), fields.catalogue(name)
    sol = ps.solve(det, cat, fields.FIELDS[name]["center"])
    xy = np.column_stack([det["x"], det["y"]])
    M = np.column_stack([xy[:, 0] - fields.CRPIX, xy[:, 1] - fields.CRPIX])
    ra, dec = fields.tan_deproject(*(M @ sol["cd"].T).T, *sol["crval"])
    world = SkyCoord(ra * u.deg, dec * u.deg)
    wcs = fit_wcs_from_points((xy[:, 0] - 1, xy[:, 1] - 1), world, proj_point=SkyCoord(*sol["crval"], unit="deg"),
                              projection="TAN")  # astropy pixels are 0-based
    return float(proj_plane_pixel_scales(wcs).mean() * 3600), sol


if __name__ == "__main__":
    for field in fields.FIELDS:
        scale, sol = astropy_wcs(field)
        print(f"{field}: astropy scale {scale:.4f} arcsec/px (ours {np.sqrt(abs(np.linalg.det(sol['cd']))) * 3600:.4f})")
