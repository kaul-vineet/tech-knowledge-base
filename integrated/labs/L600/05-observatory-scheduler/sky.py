"""The night and the constraints: one robotic 0.4 m telescope at Gurgaon, the night of 2026-11-19 (waxing gibbous Moon).

Everything reuses astronomy L300 #12: ephem.py for Sun, Moon and alt/az; Kasten & Young airmass from its solution.
Units are in the names: *_deg degrees, *_h hours, *_min minutes. Sky functions accept only UtcInstant.
"""
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import numpy as np

import _kb
from timeutil import UTC, UtcInstant

ephem, airmass = _kb.ephem, _kb.astro_plan.airmass
SITE = {"name": "Gurgaon, India", "lat_deg": 28.46, "lon_deg": 77.03, "tz": timezone(timedelta(hours=5, minutes=30))}
NIGHT_LOCAL = datetime(2026, 11, 19, 17, 0)  # wall clock at the site (naive on purpose: it is NOT a UTC time)
STEP_MIN, HOURS = 10, 14
MAX_AIRMASS, MIN_MOON_SEP_DEG, SUN_LIMIT_DEG = 2.0, 30.0, -18.0


@dataclass(frozen=True)
class Request:
    name: str
    ra_deg: float
    dec_deg: float
    priority: int  # 1 (filler) .. 5 (must-have); the value weight
    exp_min: int  # one uninterrupted block, a multiple of STEP_MIN


S = _kb.astro_plan.TARGETS  # J2000 RA/Dec (deg) from SIMBAD, as used in astronomy L300 #12
REQUESTS = [Request("Vega", *S["Vega"], 3, 60), Request("Altair", *S["Altair"], 2, 60),
            Request("Deneb", *S["Deneb"], 4, 120), Request("Fomalhaut", *S["Fomalhaut"], 5, 60),
            Request("Capella", *S["Capella"], 3, 120), Request("Aldebaran", *S["Aldebaran"], 4, 90),
            Request("Betelgeuse", *S["Betelgeuse"], 5, 180), Request("Sirius", *S["Sirius"], 4, 150),
            Request("Polaris", 37.9546, 89.2641, 2, 60), Request("Canopus", 95.9880, -52.6957, 3, 60),
            Request("Arcturus", 213.9153, 19.1824, 1, 30)]  # last three: astronomy L100 #2 (SIMBAD, rounded)


def _jd(t):
    if not isinstance(t, UtcInstant):
        raise TypeError(f"sky maths needs a UtcInstant, got {type(t).__name__}")
    return t.jd()


def alt_deg(req, t):
    return float(ephem.altaz(req.ra_deg, req.dec_deg, SITE["lat_deg"], SITE["lon_deg"], _jd(t))[0])


def sun_alt_deg(t):
    jd = _jd(t)
    return float(ephem.altaz(*ephem.sun_radec(jd), SITE["lat_deg"], SITE["lon_deg"], jd)[0])


def moon_sep_deg(req, t):
    _, _, mra, mdec = ephem.moon_altaz(SITE["lat_deg"], SITE["lon_deg"], _jd(t))
    return float(ephem.separation(req.ra_deg, req.dec_deg, mra, mdec))


@dataclass(frozen=True)
class Slot:
    index: int
    utc: UtcInstant
    local: datetime  # aware, site time zone; for people, never for sky maths


def night_slots():
    """Slot boundaries from 17:00 local for 14 h, trimmed to astronomical darkness (Sun <= -18 deg)."""
    start = UtcInstant.from_aware(NIGHT_LOCAL.replace(tzinfo=SITE["tz"]))  # naive wall clock + its zone, converted
    pts = [start.plus(STEP_MIN * k) for k in range(HOURS * 60 // STEP_MIN + 1)]
    dark = [t for t in pts if sun_alt_deg(t) <= SUN_LIMIT_DEG]
    return [Slot(i, t, t.local(SITE["tz"])) for i, t in enumerate(dark)]


def sky_instant(slot, fault=None):
    """The instant handed to sky maths. FAULT 'local-as-utc': the local wall clock relabelled as UTC."""
    if (fault or os.environ.get("SCHED_FAULT")) == "local-as-utc":
        return UtcInstant(slot.local.replace(tzinfo=None).replace(tzinfo=UTC))  # the bug: 18:50 IST read as 18:50 UTC
    return slot.utc


def feasibility(reqs, slots, fault=None):
    """ok[i, s]: request i may start at slot s (every boundary of the block dark, airmass <= 2, Moon >= 30 deg)."""
    n_b = len(slots)
    x = np.array([[float(airmass(alt_deg(r, sky_instant(sl, fault)))) for sl in slots] for r in reqs])
    sep = np.array([[moon_sep_deg(r, sky_instant(sl, fault)) for sl in slots] for r in reqs])
    good = (x <= MAX_AIRMASS) & (sep >= MIN_MOON_SEP_DEG)
    ok = np.zeros((len(reqs), n_b), dtype=bool)
    for i, r in enumerate(reqs):
        n = r.exp_min // STEP_MIN
        for s in range(n_b - n):
            ok[i, s] = good[i, s:s + n + 1].all()  # start, every 10-min boundary inside, end
    return ok, x
