"""L300 observation planning: one night at Gurgaon, eight bright stars, a greedy scheduler under constraints.

Constraints (astroplan names in brackets): astronomical darkness, Sun below -18 deg [AtNightConstraint];
airmass <= 2.0 [AirmassConstraint]; >= 30 deg from the Moon [MoonSeparationConstraint]. Each target gets one 60-min block.
python solution/plan.py           (night of 2026-11-24, full Moon near Aldebaran)
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # ephem.py lives in the lab folder
import ephem  # noqa: E402

SITE = {"name": "Gurgaon, India", "lat": 28.46, "lon": 77.03, "tz": timezone(timedelta(hours=5, minutes=30))}
NIGHT = datetime(2026, 11, 24, 17, 0, tzinfo=SITE["tz"])  # local evening; the grid runs 14 h from here
STEP_MIN, BLOCK_MIN = 10, 60
MAX_AIRMASS, MIN_MOON_SEP, SUN_LIMIT = 2.0, 30.0, -18.0
# J2000 RA/Dec in degrees, SIMBAD (van Leeuwen 2007 Hipparcos reduction)
TARGETS = {"Vega": (279.23474, 38.78369), "Altair": (297.69583, 8.86832), "Deneb": (310.35798, 45.28034),
           "Fomalhaut": (344.41269, -29.62224), "Capella": (79.17233, 45.99799), "Aldebaran": (68.98016, 16.50930),
           "Betelgeuse": (88.79294, 7.40706), "Sirius": (101.28715, -16.71612)}


def airmass(alt_deg):
    """Airmass that cannot be gamed: infinite at or below the horizon (sec z turns NEGATIVE there and a
    'lowest airmass wins' rule then prefers stars under the ground). Above it, Kasten & Young (1989, Applied
    Optics 28, 4735, eq. 3 with the revised constants): X = 1/(sin h + 0.50572 (h + 6.07995)^-1.6364), h in
    degrees. It fits their ISO-standard-atmosphere table to < 0.5 % and stays finite (~38) at the horizon.
    The paper's argument is the APPARENT (refracted) elevation; this lab passes true elevation (KNOWN-GAPS).
    The fit dips to 0.9997 at the zenith (table: 1.0000), so it is clamped at 1 - airmass is >= 1 by definition."""
    h = np.asarray(alt_deg, dtype=float)
    hp = np.where(h > 0, h, 1.0)  # placeholder keeps the power defined; masked out below
    x = 1.0 / (np.sin(np.radians(hp)) + 0.50572 * (hp + 6.07995) ** -1.6364)
    return np.where(h > 0, np.maximum(x, 1.0), np.inf)


def grid(site=SITE, start=NIGHT, hours=14):
    """Time grid (UTC JDs) with Sun altitude and topocentric Moon RA/Dec at each step."""
    times = [start + timedelta(minutes=STEP_MIN * k) for k in range(hours * 60 // STEP_MIN + 1)]
    jd = np.array([ephem.julian_date(t) for t in times])
    sun_alt, _ = ephem.altaz(*ephem.sun_radec(jd), site["lat"], site["lon"], jd)
    _, _, mra, mdec = ephem.moon_altaz(site["lat"], site["lon"], jd)
    return times, jd, sun_alt, mra, mdec


def observable(name, k, g, site=SITE):
    """Every constraint at grid step k; returns (ok, alt, airmass, moon separation)."""
    times, jd, sun_alt, mra, mdec = g
    ra, dec = TARGETS[name]
    alt, _ = ephem.altaz(ra, dec, site["lat"], site["lon"], jd[k])
    x, sep = airmass(alt), ephem.separation(ra, dec, mra[k], mdec[k])
    ok = sun_alt[k] <= SUN_LIMIT and x <= MAX_AIRMASS and sep >= MIN_MOON_SEP  # the night's three rules
    return bool(ok), float(alt), float(x), float(sep)


def schedule(site=SITE, start=NIGHT):
    """Sequential greedy scheduler: at each free step, start the valid block with the lowest mean airmass."""
    g = grid(site, start)
    n_block, k, plan, todo = BLOCK_MIN // STEP_MIN, 0, [], set(TARGETS)
    while k + n_block < len(g[0]) and todo:
        best = None
        for name in sorted(todo):
            checks = [observable(name, k + j, g, site) for j in (0, n_block // 2, n_block)]  # start, middle, end
            if all(c[0] for c in checks):
                mean_x = sum(c[2] for c in checks) / 3
                if best is None or mean_x < best[0]:
                    best = (mean_x, name, checks)
        if best is None:
            k += 1
            continue
        _, name, checks = best
        plan.append({"target": name, "start": g[0][k].strftime("%H:%M"), "alt_deg": round(checks[0][1], 1),
                     "airmass": round(checks[0][2], 2), "moon_sep_deg": round(checks[0][3], 1)})
        todo.discard(name)
        k += n_block
    return plan, sorted(todo)


def dark_window(site=SITE, start=NIGHT):
    """First and last grid step with the Sun below the astronomical-twilight limit."""
    times, _, sun_alt, _, _ = grid(site, start)
    dark = np.flatnonzero(sun_alt <= SUN_LIMIT)
    return times[dark[0]].strftime("%H:%M"), times[dark[-1]].strftime("%H:%M")


if __name__ == "__main__":
    first, last = dark_window()
    print(f"{SITE['name']} {NIGHT:%Y-%m-%d}: astronomical darkness {first}-{last} local (10-min grid)")
    plan, unscheduled = schedule()
    for row in plan:
        print(json.dumps(row))
    print("unscheduled:", unscheduled)
    if "--check" in sys.argv:  # recompute altitude independently: did we schedule anything below 30 deg?
        print("blocks below 30 deg altitude:", [r["target"] for r in plan if r["alt_deg"] < 30])
