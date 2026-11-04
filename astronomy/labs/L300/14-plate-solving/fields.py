"""Seeded SYNTHETIC star fields for lesson 14: a catalogue (RA, Dec, mag) and the detections a camera would report.

The camera's true pointing, rotation and pixel scale are known, so a solution can be checked exactly.
Pixel <-> sky uses the FITS TAN (gnomonic) projection (Calabretta & Greisen 2002, WCS Paper II).
FIELDS: "orion" near Dec -5 (easy) and "cassiopeia" near Dec +62 (where RA degrees shrink by cos(Dec) = 0.47).
"""
import numpy as np

D2R = np.pi / 180.0
NPIX, SCALE_ARCSEC = 1024, 2.0
CRPIX = (NPIX + 1) / 2.0
FIELDS = {"orion": {"center": (83.82, -5.39), "rot_deg": 12.0, "seed": 14},
          "cassiopeia": {"center": (10.40, 62.10), "rot_deg": -33.0, "seed": 41}}
HINT_ERROR_DEG = (0.15, -0.10)  # the mount's pointing error: the solver only gets center + this offset


def tan_project(ra, dec, ra0, dec0):
    """Gnomonic (TAN) projection -> standard coordinates (xi, eta) in degrees.

    DERIVED here, not quoted (Calabretta & Greisen 2002, sec. 5.1.3, could not be read in full): project the star's
    unit vector from the sphere's centre onto the plane tangent at (ra0, dec0). In a frame whose z-axis points at the
    tangent point the vector is (cos d sin(a-a0), cos d0 sin d - sin d0 cos d cos(a-a0), cos c), where
    cos c = sin d0 sin d + cos d0 cos d cos(a-a0) is the spherical law of cosines (c = angular distance). Dividing
    x and y by z puts the point on the plane z = 1, at radius tan c = cot(theta) with native latitude theta = 90 - c:
    the TAN rule R_theta = (180/pi) cot(theta), i.e. C&G's zenithal AZP formula (their eq. 16) with mu = 0.
    Checked by a round trip with tan_deproject (test_tan_round_trip) and against astropy.wcs in CI.
    """
    a, d, a0, d0 = ra * D2R, dec * D2R, ra0 * D2R, dec0 * D2R
    cosc = np.sin(d0) * np.sin(d) + np.cos(d0) * np.cos(d) * np.cos(a - a0)
    xi = np.cos(d) * np.sin(a - a0) / cosc
    eta = (np.cos(d0) * np.sin(d) - np.sin(d0) * np.cos(d) * np.cos(a - a0)) / cosc
    return xi / D2R, eta / D2R


def tan_deproject(xi, eta, ra0, dec0):
    x, y, d0 = xi * D2R, eta * D2R, dec0 * D2R
    den = np.cos(d0) - y * np.sin(d0)
    ra = ra0 + np.arctan2(x, den) / D2R
    dec = np.arctan2(np.sin(d0) + y * np.cos(d0), np.hypot(x, den)) / D2R
    return ra % 360.0, dec


def catalogue(name, radius=0.9, density=220.0):
    """Uniform stars on the sphere around the field center; magnitudes from a steep (realistic-ish) law."""
    f = FIELDS[name]
    rng = np.random.default_rng(f["seed"])
    ra0, dec0 = f["center"]
    n = rng.poisson(density * np.pi * radius ** 2)
    r = radius * np.sqrt(rng.uniform(0, 1, n))
    th = rng.uniform(0, 2 * np.pi, n)
    ra, dec = tan_deproject(r * np.cos(th), r * np.sin(th), ra0, dec0)
    mag = 12.0 - 2.5 * np.log10(rng.uniform(0.0, 1.0, n) ** -0.6)  # many faint, few bright
    return {"ra": ra, "dec": dec, "mag": mag}


def true_cd(name):
    th = FIELDS[name]["rot_deg"] * D2R
    s = SCALE_ARCSEC / 3600.0
    return s * np.array([[-np.cos(th), np.sin(th)], [np.sin(th), np.cos(th)]])  # RA increases to the left


def detections(name, limit=11.5):
    """What source extraction reports: pixel x, y (FITS 1-based), instrumental mag; 10% missed, 5 spurious."""
    f, cat = FIELDS[name], catalogue(name)
    rng = np.random.default_rng(f["seed"] + 1000)
    xi, eta = tan_project(cat["ra"], cat["dec"], *f["center"])
    pix = np.linalg.solve(true_cd(name), np.vstack([xi, eta]))
    x, y = pix[0] + CRPIX, pix[1] + CRPIX
    keep = (x > 1) & (x < NPIX) & (y > 1) & (y < NPIX) & (cat["mag"] < limit) & (rng.uniform(0, 1, x.size) > 0.10)
    x, y = x[keep] + rng.normal(0, 0.15, keep.sum()), y[keep] + rng.normal(0, 0.15, keep.sum())
    m = cat["mag"][keep] + rng.normal(0, 0.05, keep.sum())
    x, y = np.append(x, rng.uniform(1, NPIX, 5)), np.append(y, rng.uniform(1, NPIX, 5))
    m = np.append(m, rng.uniform(9, 11.5, 5))
    return {"x": x, "y": y, "mag": m}
