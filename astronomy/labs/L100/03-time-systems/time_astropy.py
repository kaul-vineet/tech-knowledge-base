"""Astropy 8.0.2 equivalent of timescales.py (pending-ci). python time_astropy.py"""
from datetime import datetime, timezone

from astropy.time import Time

import timescales as ts


def compare(dt):
    t = Time(dt, scale="utc")
    gmst = t.sidereal_time("mean", "greenwich").hour  # IAU 2006 model; needs UT1 (IERS data, may download)
    return {"tt_minus_utc_s": (t.tt.jd - t.utc.jd) * 86400.0,
            "gmst_diff_s": ((gmst - ts.gmst_hours(ts.jd_utc(dt)) + 12) % 24 - 12) * 3600.0,
            "jd_utc": t.utc.jd}


if __name__ == "__main__":
    print(compare(datetime(2026, 10, 29, 15, 30, tzinfo=timezone.utc)))
