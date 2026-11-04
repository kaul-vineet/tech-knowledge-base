"""Experiment 2a: cross-check the plan's altitudes and airmasses with astropy (and astroplan, if installed).

For every block of the optimised plan, sampled every 10 minutes from start to end: our altitude (sky.alt_deg:
ephem.py, J2000 RA/Dec, GMST) against a reference altitude, both converted to airmass with the SAME Kasten & Young
formula (sky.airmass), so the difference isolates the astronomy, not the airmass model. Reference routes:
  astropy   AltAz frame, pressure 0 (no refraction, like ours), site height 217 m (astropy, BSD-3-Clause)
  astroplan Observer.altaz (astroplan, BSD-3-Clause) - only if installed
  lst       --here: validator.alt_deg_lst (apparent sidereal time route already in the lab) - runs anywhere
Reported: max |delta altitude|, max |delta airmass|, and blocks whose reference airmass exceeds the 2.0 limit (FF1).

python astropy_check.py --here       reference = validator's LST route (no astropy needed)
python astropy_check.py              astropy (+ astroplan); prints SKIP and exits 0 when astropy is missing
"""
import argparse
import json
import sys
from datetime import datetime

import _lab
import sky
import validator
from timeutil import UtcInstant

ELEV_M = 217
STEP_MIN = 10


def samples(row):
    start = UtcInstant(datetime.fromisoformat(row["start_utc"].replace("Z", "+00:00")))
    end = UtcInstant(datetime.fromisoformat(row["end_utc"].replace("Z", "+00:00")))
    t, out = start, []
    while t <= end:
        out.append(t)
        t = t.plus(STEP_MIN)
    return out


def compare(rows, reqs, ref_alt, label):
    """ref_alt(req, [UtcInstant]) -> [alt_deg]. Same airmass formula on both sides."""
    by = {r.name: r for r in reqs}
    worst_dalt, worst_dx, blocks = 0.0, 0.0, []
    for row in rows:
        req, ts = by[row["target"]], samples(row)
        ours = [sky.alt_deg(req, t) for t in ts]
        ref = ref_alt(req, ts)
        x_ours = [float(sky.airmass(a)) for a in ours]
        x_ref = [float(sky.airmass(a)) for a in ref]
        dalt = max(abs(a - b) for a, b in zip(ours, ref))
        dx = max(abs(a - b) for a, b in zip(x_ours, x_ref))
        worst_dalt, worst_dx = max(worst_dalt, dalt), max(worst_dx, dx)
        blocks.append({"target": row["target"], "max_airmass_ours": round(max(x_ours), 4),
                       "max_airmass_ref": round(max(x_ref), 4), "max_dalt_deg": round(dalt, 4),
                       "ref_violates_ff1": max(x_ref) > sky.MAX_AIRMASS + 1e-9})
    return {"reference": label, "max_dalt_deg": round(worst_dalt, 4), "max_dairmass": round(worst_dx, 4),
            "ff1_violations_by_reference": [b["target"] for b in blocks if b["ref_violates_ff1"]], "blocks": blocks}


def lst_route(req, ts):
    return [validator.alt_deg_lst(req, t) for t in ts]


def astropy_route():
    try:
        import astropy.units as u
        from astropy.coordinates import AltAz, EarthLocation, SkyCoord
        from astropy.time import Time
    except ImportError:
        return None
    loc = EarthLocation(lat=sky.SITE["lat_deg"] * u.deg, lon=sky.SITE["lon_deg"] * u.deg, height=ELEV_M * u.m)

    def ref(req, ts):
        t = Time([x.dt for x in ts], scale="utc")
        c = SkyCoord(ra=req.ra_deg * u.deg, dec=req.dec_deg * u.deg, frame="icrs")
        return [float(a) for a in c.transform_to(AltAz(obstime=t, location=loc, pressure=0 * u.hPa)).alt.deg]
    return ref


def astroplan_route():
    try:
        import astropy.units as u
        from astroplan import FixedTarget, Observer
        from astropy.coordinates import EarthLocation, SkyCoord
        from astropy.time import Time
    except ImportError:
        return None
    obs = Observer(location=EarthLocation(lat=sky.SITE["lat_deg"] * u.deg, lon=sky.SITE["lon_deg"] * u.deg,
                                          height=ELEV_M * u.m))

    def ref(req, ts):
        target = FixedTarget(SkyCoord(ra=req.ra_deg * u.deg, dec=req.dec_deg * u.deg), name=req.name)
        return [float(a) for a in obs.altaz(Time([x.dt for x in ts], scale="utc"), target).alt.deg]
    return ref


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--here", action="store_true", help="reference = validator's LST route (no astropy needed)")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    routes = [("lst (validator.alt_deg_lst)", lst_route)] if a.here else \
        [(n, f) for n, f in (("astropy AltAz", astropy_route()), ("astroplan Observer.altaz", astroplan_route())) if f]
    if not routes:
        print("SKIP: astropy is not installed here (python3 -m pip install astropy astroplan on the Mac); "
              "run with --here for the format")
        return 0
    r = _lab.build()
    rows = [compare(r["local_rows"], r["reqs"], f, n) for n, f in routes]
    for row in rows:
        print(json.dumps({k: v for k, v in row.items() if k != "blocks"}))
        for b in row["blocks"]:
            print("   ", json.dumps(b))
    _lab.write_jsonl(_lab.runs_dir(a.out) / "05-astropy-check.jsonl", rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
