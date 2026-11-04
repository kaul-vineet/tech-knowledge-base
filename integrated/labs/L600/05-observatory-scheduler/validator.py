"""The deterministic judge. Any plan - greedy, optimised, or proposed by an agent - must pass it to be executed.

Independent of the scheduler on purpose: it re-derives altitude from the local APPARENT sidereal time of astronomy
L100 #3 (GAST, checked against Wallace & Capitaine 2006) instead of ephem.py's GMST, samples every 5 minutes instead
of every 10, and rechecks the Sun and Moon itself. Input rows: {"target", "start": UtcInstant}.
"""
import math

import sky
from timeutil import UtcInstant, lst_hours

SAMPLE_MIN = 5


def alt_from_hour_angle(ha_deg, dec_deg, lat_deg):
    """sin h = sin(phi) sin(dec) + cos(phi) cos(dec) cos(H); every argument in DEGREES."""
    ha, phi, dec = math.radians(ha_deg), math.radians(lat_deg), math.radians(dec_deg)
    return math.degrees(math.asin(math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.cos(ha)))


def alt_deg_lst(req, t):
    """Route 2: hour angle from local apparent sidereal time (HOURS, x 15 -> degrees) minus RA (degrees)."""
    return alt_from_hour_angle(lst_hours(t, sky.SITE["lon_deg"]) * 15.0 - req.ra_deg, req.dec_deg, sky.SITE["lat_deg"])


def validate(rows, reqs=None, slots=None):
    """Return a list of violations (empty = the plan may run). Never repairs a plan; it only judges."""
    reqs = {r.name: r for r in (reqs or sky.REQUESTS)}
    slots = slots or sky.night_slots()
    first, last = slots[0].utc, slots[-1].utc
    out, seen, spans = [], set(), []
    for row in rows:
        name, start = row["target"], row["start"]
        if not isinstance(start, UtcInstant):
            out.append(f"{name}: start is {type(start).__name__}, not a UtcInstant")
            continue
        if name not in reqs:
            out.append(f"{name}: not a requested target")
            continue
        if name in seen:
            out.append(f"{name}: scheduled twice")
        seen.add(name)
        req, end = reqs[name], start.plus(reqs[name].exp_min)
        offset_min = (start.dt - first.dt).total_seconds() / 60.0
        if offset_min % sky.STEP_MIN:
            out.append(f"{name}: start {start.iso()} is off the {sky.STEP_MIN}-min slot grid")
        if start < first or end > last:
            out.append(f"{name}: {start.iso()}-{end.iso()} outside darkness {first.iso()}-{last.iso()}")
        spans.append((start.dt, end.dt, name))
        for k in range(req.exp_min // SAMPLE_MIN + 1):
            t = start.plus(k * SAMPLE_MIN)
            alt = alt_deg_lst(req, t)
            x = float(sky.airmass(alt))
            if alt <= 0 or x > sky.MAX_AIRMASS + 1e-9:
                out.append(f"{name}: altitude {alt:.1f} deg, airmass {x:.2f} at {t.iso()} (limit {sky.MAX_AIRMASS})")
                break
            if sky.sun_alt_deg(t) > sky.SUN_LIMIT_DEG:
                out.append(f"{name}: Sun above {sky.SUN_LIMIT_DEG} deg at {t.iso()}")
                break
            sep = sky.moon_sep_deg(req, t)
            if sep < sky.MIN_MOON_SEP_DEG:
                out.append(f"{name}: {sep:.1f} deg from the Moon at {t.iso()} (min {sky.MIN_MOON_SEP_DEG})")
                break
    spans.sort()
    for (s1, e1, n1), (s2, _, n2) in zip(spans, spans[1:]):
        if s2 < e1:
            out.append(f"{n1} and {n2} overlap")
    return out


def rows_from_blocks(blocks, reqs, slots):
    return [{"target": reqs[i].name, "start": slots[s].utc} for s, _, i in blocks]
