"""Astropy 8.0.2 equivalent of sky.py (pending-ci: astropy is not installed in the offline sandbox).

Astropy applies precession, nutation, aberration and Earth-orientation data (it may download IERS tables),
so its altitudes differ from the simple J2000 calculation by a few tenths of a degree.
python sky_astropy.py
"""
from datetime import datetime, timezone

import astropy.units as u
from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from astropy.time import Time

import sky


def compare(dt):
    loc = EarthLocation(lat=sky.GURGAON[0] * u.deg, lon=sky.GURGAON[1] * u.deg, height=0 * u.m)
    frame = AltAz(obstime=Time(dt), location=loc, pressure=0 * u.hPa)  # pressure 0 = no refraction, like sky.py
    out = []
    for name, (ra, dec) in sky.STARS.items():
        aa = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame="icrs").transform_to(frame)
        alt, az = sky.altaz(ra, dec, *sky.GURGAON, dt)
        daz = (aa.az.deg - az + 180) % 360 - 180
        out.append((name, aa.alt.deg - alt, daz if abs(alt) < 85 else 0.0))  # azimuth is unstable near the zenith/pole
    return out


if __name__ == "__main__":
    for name, dalt, daz in compare(datetime(2026, 10, 29, 15, 30, tzinfo=timezone.utc)):
        print(f"{name:<11} astropy - sky.py: alt {dalt:+.3f} deg, az {daz:+.3f} deg")
