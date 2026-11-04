"""L100 Coordinates and the sky: RA/Dec -> Alt/Az for an observer. Is a star above the horizon now?

python sky.py                                   # Gurgaon, 2026-10-29 15:30 UTC (21:00 IST)
python sky.py --lat 51.4778 --lon -0.0015 --utc 2026-10-29T21:00   # any place and time (east longitude +)
Simplifications: J2000 catalogue positions (no precession, nutation, aberration), no refraction.
"""
import argparse
import math
from datetime import datetime, timezone

GURGAON = (28.46, 77.03)  # latitude N, longitude E (degrees)
# Approximate J2000 (ICRS) RA/Dec in degrees, rounded, as listed by SIMBAD; check them in Stellarium.
STARS = {
    "Polaris": (37.9546, 89.2641), "Vega": (279.2347, 38.7837), "Altair": (297.6958, 8.8683),
    "Deneb": (310.3580, 45.2803), "Fomalhaut": (344.4127, -29.6222), "Capella": (79.1723, 45.9980),
    "Betelgeuse": (88.7929, 7.4071), "Sirius": (101.2872, -16.7161), "Canopus": (95.9880, -52.6957),
    "Arcturus": (213.9153, 19.1824),
}


def julian_date(dt):
    """JD from an aware UTC datetime (JD 2440587.5 = 1970-01-01 00:00 UTC, the Unix epoch)."""
    return 2440587.5 + dt.timestamp() / 86400.0


def gmst_hours(jd_ut):
    # Greenwich mean sidereal time, USNO approximate formula (accuracy ~0.1 s; UTC used for UT1)
    return (18.697375 + 24.065709824279 * (jd_ut - 2451545.0)) % 24.0


def altaz(ra_deg, dec_deg, lat_deg, lon_deg, dt):
    """Return (altitude, azimuth) in degrees; azimuth from North through East."""
    lst_deg = (gmst_hours(julian_date(dt)) * 15.0 + lon_deg) % 360.0  # local sidereal time as an angle
    ha = math.radians((lst_deg - ra_deg) % 360.0)  # hour angle: how far west of the meridian the star is
    dec, lat = math.radians(dec_deg), math.radians(lat_deg)
    sin_alt = math.sin(dec) * math.sin(lat) + math.cos(dec) * math.cos(lat) * math.cos(ha)
    alt = math.asin(sin_alt)
    az = math.atan2(-math.cos(dec) * math.sin(ha),  # east-west component
                    math.sin(dec) * math.cos(lat) - math.cos(dec) * math.sin(lat) * math.cos(ha))
    return math.degrees(alt), math.degrees(az) % 360.0


def sky_table(lat, lon, dt):
    rows = []
    for name, (ra, dec) in STARS.items():
        alt, az = altaz(ra, dec, lat, lon, dt)
        rows.append((name, alt, az, alt > 0.0))  # above the (mathematical) horizon?
    return sorted(rows, key=lambda r: -r[1])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--lat", type=float, default=GURGAON[0])
    p.add_argument("--lon", type=float, default=GURGAON[1])
    p.add_argument("--utc", default="2026-10-29T15:30")
    a = p.parse_args()
    dt = datetime.fromisoformat(a.utc).replace(tzinfo=timezone.utc)
    lst = (gmst_hours(julian_date(dt)) + a.lon / 15.0) % 24.0
    print(f"observer lat {a.lat:+.2f} lon {a.lon:+.2f} | {dt:%Y-%m-%d %H:%M} UTC | JD {julian_date(dt):.5f} | LST {lst:.4f} h")
    print("star        alt(deg)  az(deg)  up?")
    for name, alt, az, up in sky_table(a.lat, a.lon, dt):
        print(f"{name:<11} {alt:8.2f} {az:8.2f}  {'UP' if up else 'below'}")


if __name__ == "__main__":
    main()
