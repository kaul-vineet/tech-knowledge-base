"""L100 Time systems: UTC, TAI, TT, Julian Date and sidereal time (checked against official formulas).

python timescales.py                        # Gurgaon (77.03 E), 2026-10-29 15:30 UTC
python timescales.py --utc 2027-01-01T00:00 --lon -0.0015
"""
import argparse
import math
from datetime import date, datetime, timezone

# TAI-UTC in seconds from each MJD on (IERS Leap_Second.dat, Bulletin C 72, July 2026). The file expires:
LEAP_TABLE_EXPIRES = date(2027, 6, 28)
LEAPS = [(41317, 10), (41499, 11), (41683, 12), (42048, 13), (42413, 14), (42778, 15), (43144, 16),
         (43509, 17), (43874, 18), (44239, 19), (44786, 20), (45151, 21), (45516, 22), (46247, 23),
         (47161, 24), (47892, 25), (48257, 26), (48804, 27), (49169, 28), (49534, 29), (50083, 30),
         (50630, 31), (51179, 32), (53736, 33), (54832, 34), (56109, 35), (57204, 36), (57754, 37)]
TT_MINUS_TAI = 32.184  # seconds, exact by definition


def jd_utc(dt):
    return 2440587.5 + dt.timestamp() / 86400.0  # Julian Date: days since -4712 Jan 1 noon; Unix epoch = 2440587.5


def tai_minus_utc(mjd):
    if mjd < LEAPS[0][0]:
        raise ValueError("before 1972: UTC had fractional steps; not handled")
    return [s for start, s in LEAPS if mjd >= start][-1]  # leap seconds: a step table, not a formula


def scales(dt):
    jd = jd_utc(dt)
    dat = tai_minus_utc(jd - 2400000.5)
    return {"JD(UTC)": jd, "MJD(UTC)": jd - 2400000.5, "TAI-UTC s": dat,
            "TT-UTC s": dat + TT_MINUS_TAI, "JD(TT)": jd + (dat + TT_MINUS_TAI) / 86400.0}


def gmst_hours(jd_ut):
    return (18.697375 + 24.065709824279 * (jd_ut - 2451545.0)) % 24.0  # USNO approximate GMST (UT1 ~ UTC)


def gmst_usno_full_hours(dt):
    """USNO's longer GMST formula (from USNO Circular 179, sec. 2.6.2): split at 0h UT1, with the TT-century terms."""
    jd = jd_utc(dt)
    jd0 = math.floor(jd - 0.5) + 0.5
    h = (jd - jd0) * 24.0
    t = (scales(dt)["JD(TT)"] - 2451545.0) / 36525.0
    return (6.697375 + 0.065707485828 * (jd0 - 2451545.0) + 1.0027379 * h + 0.0854103 * t + 0.0000258 * t * t) % 24.0


def era_hours(jd_ut1):
    """Earth rotation angle, IERS Conventions (2010) eq. 5.14, in hours (24 h = one turn)."""
    return 24.0 * ((0.7790572732640 + 1.00273781191135448 * (jd_ut1 - 2451545.0)) % 1.0)


def gast_hours(jd_ut1, jd_tt):
    """Apparent sidereal time = GMST + equation of the equinoxes (USNO approximate nutation terms)."""
    d = jd_tt - 2451545.0
    omega, sun_l, eps = 125.04 - 0.052954 * d, 280.47 + 0.98565 * d, 23.4393 - 0.0000004 * d
    dpsi = -0.000319 * math.sin(math.radians(omega)) - 0.000024 * math.sin(math.radians(2.0 * sun_l))  # hours
    return (gmst_hours(jd_ut1) + dpsi * math.cos(math.radians(eps))) % 24.0


# Worked example, Wallace & Capitaine 2006 (A&A 459, 981), appendix: UTC 2006-01-15 21:24:37.5, UT1-UTC = +0.3341 s
WC06_JD_UT1 = 2400000.5 + 53750.892104561342593
WC06_JD_TT = 2400000.5 + 53750.892855138888889
WC06_ERA_H = 76.265431053522 / 15.0             # 5h05m03.703452845s
WC06_GST_H = 5.0 + 5.0 / 60.0 + 22.213252581 / 3600.0  # 5h05m22.213252581s (apparent, IAU 2006/2000A)


def hms(hours):
    s = round(hours * 3600.0, 2)
    return f"{int(s // 3600):02d}h{int(s % 3600 // 60):02d}m{s % 60:05.2f}s"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--utc", default="2026-10-29T15:30")
    p.add_argument("--lon", type=float, default=77.03)
    a = p.parse_args()
    dt = datetime.fromisoformat(a.utc).replace(tzinfo=timezone.utc)
    for k, v in scales(dt).items():
        print(f"{k:<10} {v:.6f}" if isinstance(v, float) else f"{k:<10} {v}")
    g = gmst_hours(jd_utc(dt))
    print(f"GMST {hms(g)} | LST at {a.lon:+.2f} deg: {hms((g + a.lon / 15.0) % 24.0)}")
    # official check 1: J2000.0 is 2000-01-01 12:00 TT -> UTC = 12:00 - (32 + 32.184) s
    j2000 = datetime(2000, 1, 1, 12, tzinfo=timezone.utc).timestamp() - tai_minus_utc(51544.5) - TT_MINUS_TAI
    print("J2000.0 in UTC:", datetime.fromtimestamp(j2000, timezone.utc).isoformat(timespec="milliseconds"))
    # official check 2: the IAU 2006 worked example published by Wallace & Capitaine (2006)
    era, gast = era_hours(WC06_JD_UT1), gast_hours(WC06_JD_UT1, WC06_JD_TT)
    print(f"Worked example 2006-01-15 21:24:37.5 UTC: ERA {hms(era)} (published {hms(WC06_ERA_H)}) | "
          f"GAST {hms(gast)} (published {hms(WC06_GST_H)}, diff {(gast - WC06_GST_H) * 3600.0:+.3f} s)")
    # official check 3: the short formula vs USNO's full GMST formula (USNO: short form loses 0.1 s per century)
    diff = (g - gmst_usno_full_hours(dt)) * 3600.0
    print(f"GMST short vs USNO full formula: {hms(gmst_usno_full_hours(dt))} (diff {diff:+.3f} s)")
    # official check 4: at J2000.0 (UT1) GMST starts where the IERS 2010 Earth rotation angle starts
    print(f"J2000.0 GMST {hms(gmst_hours(2451545.0))} | IERS ERA {hms(era_hours(2451545.0))} "
          f"(diff {(gmst_hours(2451545.0) - era_hours(2451545.0)) * 3600.0:+.4f} s)")
    if date.today() > LEAP_TABLE_EXPIRES:
        print("WARNING: leap-second table expired; fetch the new IERS Leap_Second.dat")


if __name__ == "__main__":
    main()
