"""Skyfield 1.55 + JPL DE421 equivalent of kepler.py (pending-ci: downloads de421.bsp, about 17 MB).

python kepler_skyfield.py
"""
import math

from skyfield.api import load

import kepler


def compare(jd_tdb):
    ts, eph = load.timescale(), load("de421.bsp")
    t = ts.tdb_jd(jd_tdb)
    astrometric = eph["earth"].at(t).observe(eph["mars barycenter"])  # includes light-time
    ra, dec, dist = astrometric.radec()  # ICRS ~ J2000 equator
    ra2, dec2, d2 = kepler.geocentric_radec("Mars", jd_tdb)
    a, b = math.radians(dec.degrees), math.radians(dec2)
    cos_sep = math.sin(a) * math.sin(b) + math.cos(a) * math.cos(b) * math.cos(math.radians(ra._degrees - ra2))
    return math.degrees(math.acos(min(1.0, cos_sep))), dist.au - d2


if __name__ == "__main__":
    sep, dd = compare(2461342.5)
    print(f"Mars: kepler.py vs DE421 separation {sep * 3600:.0f} arcsec, distance difference {dd:+.5f} au")
