"""Low-precision ephemeris helpers for lesson 12 (numpy + stdlib; good to about 1-2 arcmin, plenty for planning).

Sun and sidereal time: USNO "Approximate Solar Coordinates" and "Approximate Sidereal Time" (aa.usno.navy.mil/faq).
Moon: P. Schlyter, "How to compute planetary positions" (stjarnhimlen.se), elements + the 12 largest perturbations.
Star coordinates are J2000 (SIMBAD); precession to the date (~0.36 deg by 2026) is ignored - astroplan does it (pending-ci).
"""
from datetime import datetime, timezone

import numpy as np

D2R = np.pi / 180.0


def julian_date(t):
    """JD of an aware datetime (converted to UTC). JD 2451545.0 = 2000-01-01 12:00 UT."""
    t = t.astimezone(timezone.utc)
    j2000 = datetime(2000, 1, 1, 12, tzinfo=timezone.utc)
    return 2451545.0 + (t - j2000).total_seconds() / 86400.0


def gmst_deg(jd):
    """USNO: GMST = 6.697375 + 0.065709824279 D0 + 1.0027379 H + 0.0000258 T^2 hours (D0 at 0h UT)."""
    jd0 = np.floor(jd - 0.5) + 0.5
    h, d0 = (jd - jd0) * 24.0, jd0 - 2451545.0
    t = (jd - 2451545.0) / 36525.0
    return (15.0 * (6.697375 + 0.065709824279 * d0 + 1.0027379 * h + 0.0000258 * t * t)) % 360.0


def sun_radec(jd):
    """USNO approximate solar coordinates (about 1 arcmin within two centuries of 2000). Degrees."""
    d = jd - 2451545.0
    g, q = (357.529 + 0.98560028 * d) * D2R, 280.459 + 0.98564736 * d
    lon = (q + 1.915 * np.sin(g) + 0.020 * np.sin(2 * g)) * D2R
    eps = (23.439 - 0.00000036 * d) * D2R
    ra = np.arctan2(np.cos(eps) * np.sin(lon), np.cos(lon))  # same quadrant as L
    return np.degrees(ra) % 360.0, np.degrees(np.arcsin(np.sin(eps) * np.sin(lon)))


def moon_radec(jd):
    """Schlyter's Moon: Kepler orbit + major perturbations. Returns RA, Dec (deg) and distance (Earth radii)."""
    d = jd - 2451543.5  # Schlyter's day 0.0 = 2000 Jan 0.0 UT
    n, i, w = 125.1228 - 0.0529538083 * d, 5.1454, 318.0634 + 0.1643573223 * d
    a, e, m = 60.2666, 0.054900, (115.3654 + 13.0649929509 * d) % 360.0
    E = m + np.degrees(e * np.sin(m * D2R) * (1 + e * np.cos(m * D2R)))
    for _ in range(5):  # Kepler's equation, Newton steps in degrees
        E = E - (E - np.degrees(e * np.sin(E * D2R)) - m) / (1 - e * np.cos(E * D2R))
    xv, yv = a * (np.cos(E * D2R) - e), a * np.sqrt(1 - e * e) * np.sin(E * D2R)
    v, r = np.degrees(np.arctan2(yv, xv)), np.hypot(xv, yv)
    vw, N, I = (v + w) * D2R, n * D2R, i * D2R
    xh = r * (np.cos(N) * np.cos(vw) - np.sin(N) * np.sin(vw) * np.cos(I))
    yh = r * (np.sin(N) * np.cos(vw) + np.cos(N) * np.sin(vw) * np.cos(I))
    zh = r * np.sin(vw) * np.sin(I)
    lon, lat = np.degrees(np.arctan2(yh, xh)), np.degrees(np.arctan2(zh, np.hypot(xh, yh)))
    ms, ws = 356.0470 + 0.9856002585 * d, 282.9404 + 4.70935e-5 * d
    ls, lm = ms + ws, m + w + n
    D, F = (lm - ls) * D2R, (lm - n) * D2R
    Ms, Mm = ms * D2R, m * D2R
    lon += (-1.274 * np.sin(Mm - 2 * D) + 0.658 * np.sin(2 * D) - 0.186 * np.sin(Ms) - 0.059 * np.sin(2 * Mm - 2 * D)
            - 0.057 * np.sin(Mm - 2 * D + Ms) + 0.053 * np.sin(Mm + 2 * D) + 0.046 * np.sin(2 * D - Ms)
            + 0.041 * np.sin(Mm - Ms) - 0.035 * np.sin(D) - 0.031 * np.sin(Mm + Ms) - 0.015 * np.sin(2 * F - 2 * D)
            + 0.011 * np.sin(Mm - 4 * D))
    lat += (-0.173 * np.sin(F - 2 * D) - 0.055 * np.sin(Mm - F - 2 * D) - 0.046 * np.sin(Mm + F - 2 * D)
            + 0.033 * np.sin(F + 2 * D) + 0.017 * np.sin(2 * Mm + F))
    r += -0.58 * np.cos(Mm - 2 * D) - 0.46 * np.cos(2 * D)
    eps = (23.4393 - 3.563e-7 * d) * D2R
    lo, la = lon * D2R, lat * D2R
    x, y, z = np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)
    ye, ze = y * np.cos(eps) - z * np.sin(eps), y * np.sin(eps) + z * np.cos(eps)
    return np.degrees(np.arctan2(ye, x)) % 360.0, np.degrees(np.arctan2(ze, np.hypot(x, ye))), r


def altaz(ra, dec, lat, lon, jd):
    """Equatorial -> horizontal for an observer (east longitude positive). Degrees; az 0 = north, 90 = east."""
    ha = (gmst_deg(jd) + lon - ra) * D2R
    la, de = lat * D2R, dec * D2R
    alt = np.arcsin(np.sin(de) * np.sin(la) + np.cos(de) * np.cos(la) * np.cos(ha))
    az = np.arctan2(-np.sin(ha) * np.cos(de), np.sin(de) * np.cos(la) - np.cos(de) * np.sin(la) * np.cos(ha))
    return np.degrees(alt), np.degrees(az) % 360.0


def moon_altaz(lat, lon, jd):
    """Topocentric Moon altitude (Schlyter: alt_topo = alt_geo - mpar cos alt_geo) plus RA/Dec for separations."""
    ra, dec, r = moon_radec(jd)
    alt, az = altaz(ra, dec, lat, lon, jd)
    return alt - np.degrees(np.arcsin(1.0 / r)) * np.cos(alt * D2R), az, ra, dec


def separation(ra1, dec1, ra2, dec2):
    """Great-circle angle (haversine form, stable for small angles). Degrees."""
    p1, p2, dl = dec1 * D2R, dec2 * D2R, (ra2 - ra1) * D2R
    h = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return np.degrees(2 * np.arcsin(np.sqrt(np.clip(h, 0, 1))))
