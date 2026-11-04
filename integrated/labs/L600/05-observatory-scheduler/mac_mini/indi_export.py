"""Experiment 3: the INDI telescope + CCD simulators execute tonight's plan, driven by INDI's own command-line tools.

The optimised plan (scheduler.build, the same night as run_project.py) becomes a bash script of indi_setprop /
indi_eval commands. Property names are INDI standard properties (docs.indilib.org/drivers/standard-properties):
  CONNECTION.CONNECT, GEOGRAPHIC_COORD.LAT;LONG;ELEV (LONG 0..360 +E), ON_COORD_SET.TRACK,
  EQUATORIAL_EOD_COORD.RA;DEC (JNow, RA in HOURS, sent atomically), CCD_EXPOSURE.CCD_EXPOSURE_VALUE (seconds),
  TELESCOPE_PARK.PARK. indi_eval -w waits until an expression is true (property _STATE: Idle 0, Ok 1, Busy 2, Alert 3);
  each move/exposure first waits (tolerantly) for Busy, then for Ok, so a stale Ok from the previous step is not read
  as "done".
New seam: the scheduler's coordinates are J2000 but EQUATORIAL_EOD_COORD is epoch-of-date, so this exporter precesses
(IAU 1976, Meeus ch. 21) - sending J2000 as JNow points ~0.36 deg off in 2026 (the gap noted in KNOWN-GAPS).

python indi_export.py --here                     dry run: print the script (no INDI needed)
python indi_export.py --out night.sh             write the script; then on the Mac:  bash night.sh
python indi_export.py --execute                  run the commands now (needs indiserver with both simulators)
Timing: --compressed (default) = one --sub-exp exposure per block, back to back (any day, minutes);
        --realtime = wait for each block's UTC start, then fill the block with --sub-exp exposures (the real night).
"""
import argparse
import math
import shlex
import shutil
import subprocess
import sys

import _lab

TELESCOPE, CCD = "Telescope Simulator", "CCD Simulator"  # default device names of indi_simulator_telescope / _ccd
ELEV_M = 217  # Gurgaon site height used by astronomy L300 #12's astroplan equivalent
STANDARD = {"CONNECTION", "GEOGRAPHIC_COORD", "ON_COORD_SET", "EQUATORIAL_EOD_COORD", "CCD_EXPOSURE", "TELESCOPE_PARK"}


def precess(ra_deg, dec_deg, jd, jd0=2451545.0):
    """Rigorous precession J2000 -> epoch jd (IAU 1976 zeta, z, theta; Meeus, Astronomical Algorithms, eq. 21.2-21.4).
    Proper motion, nutation and aberration are ignored (< 0.01 deg here); returns (ra_deg, dec_deg)."""
    T = (jd0 - 2451545.0) / 36525.0
    t = (jd - jd0) / 36525.0
    zeta = ((2306.2181 + 1.39656 * T - 0.000139 * T * T) * t + (0.30188 - 0.000344 * T) * t * t + 0.017998 * t ** 3) / 3600
    z = ((2306.2181 + 1.39656 * T - 0.000139 * T * T) * t + (1.09468 + 0.000066 * T) * t * t + 0.018203 * t ** 3) / 3600
    theta = ((2004.3109 - 0.85330 * T - 0.000217 * T * T) * t - (0.42665 + 0.000217 * T) * t * t - 0.041833 * t ** 3) / 3600
    a0, d0 = math.radians(ra_deg), math.radians(dec_deg)
    zr, thr, zer = math.radians(z), math.radians(theta), math.radians(zeta)
    A = math.cos(d0) * math.sin(a0 + zer)
    B = math.cos(thr) * math.cos(d0) * math.cos(a0 + zer) - math.sin(thr) * math.sin(d0)
    C = math.sin(thr) * math.cos(d0) * math.cos(a0 + zer) + math.cos(thr) * math.sin(d0)
    ra = math.degrees(math.atan2(A, B)) + z
    dec = math.degrees(math.asin(max(-1.0, min(1.0, C))))
    return ra % 360.0, dec


def separation_deg(ra1, dec1, ra2, dec2):
    a1, d1, a2, d2 = map(math.radians, (ra1, dec1, ra2, dec2))
    c = math.sin(d1) * math.sin(d2) + math.cos(d1) * math.cos(d2) * math.cos(a1 - a2)
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def setprop(device, prop, elements, values):
    return ["indi_setprop", f"{device}.{prop}.{';'.join(elements)}={';'.join(str(v) for v in values)}"]


def wait_state(device, prop, state, timeout_s):
    return ["indi_eval", "-t", str(int(timeout_s)), "-w", f'"{device}.{prop}._STATE"=={state}']


BUSY, OK = 2, 1  # indi_eval _STATE values: Idle 0, Ok 1, Busy 2, Alert 3
TOLERANT = "busy?"  # comment prefix: this wait may time out (a fast simulator can finish before we look)


def plan_commands(rows, reqs, jd_of, sub_exp_s=10, realtime=False, block_min=None, precess_coords=True):
    """rows: scheduler rows (target, start_utc, end_utc). jd_of(iso) -> Julian date. Returns [(comment, argv)]."""
    by_name = {r.name: r for r in reqs}
    from sky import SITE
    cmds = [("connect", setprop(TELESCOPE, "CONNECTION", ["CONNECT"], ["On"])),
            ("connect", setprop(CCD, "CONNECTION", ["CONNECT"], ["On"])),
            ("site", setprop(TELESCOPE, "GEOGRAPHIC_COORD", ["LAT", "LONG", "ELEV"],
                             [SITE["lat_deg"], round(SITE["lon_deg"] % 360.0, 4), ELEV_M]))]
    for row in rows:
        req = by_name[row["target"]]
        ra, dec = precess(req.ra_deg, req.dec_deg, jd_of(row["start_utc"])) if precess_coords else (req.ra_deg, req.dec_deg)
        if realtime:
            cmds.append((f"wait for {row['start_utc']}", ["wait_until_utc", row["start_utc"]]))
        cmds.append((f"{row['target']} (J2000 {req.ra_deg:.4f} {req.dec_deg:+.4f} -> JNow)",
                     setprop(TELESCOPE, "ON_COORD_SET", ["TRACK"], ["On"])))
        cmds.append(("goto", setprop(TELESCOPE, "EQUATORIAL_EOD_COORD", ["RA", "DEC"], [f"{ra / 15.0:.6f}", f"{dec:.5f}"])))
        cmds.append((f"{TOLERANT} slew started", wait_state(TELESCOPE, "EQUATORIAL_EOD_COORD", BUSY, 10)))
        cmds.append(("slew done", wait_state(TELESCOPE, "EQUATORIAL_EOD_COORD", OK, 180)))
        n = max(1, (block_min or _block_min(row)) * 60 // sub_exp_s) if realtime else 1
        for _ in range(n):
            cmds.append(("expose", setprop(CCD, "CCD_EXPOSURE", ["CCD_EXPOSURE_VALUE"], [sub_exp_s])))
            cmds.append((f"{TOLERANT} exposure started", wait_state(CCD, "CCD_EXPOSURE", BUSY, 10)))
            cmds.append(("exposure done", wait_state(CCD, "CCD_EXPOSURE", OK, sub_exp_s + 60)))
    cmds.append(("park", setprop(TELESCOPE, "TELESCOPE_PARK", ["PARK"], ["On"])))
    return cmds


def _block_min(row):
    from datetime import datetime
    f = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
    return int((f(row["end_utc"]) - f(row["start_utc"])).total_seconds() // 60)


def script(cmds):
    lines = ["#!/usr/bin/env bash", "# Generated by mac_mini/indi_export.py from the optimised plan (UTC). Start first:",
             "#   indiserver -v indi_simulator_telescope indi_simulator_ccd", "set -eu",
             'wait_until_utc() { local t; t=$(python3 -c "import sys,datetime as d;'
             'print(int(d.datetime.fromisoformat(sys.argv[1].replace(\'Z\',\'+00:00\')).timestamp()))" "$1"); '
             'while [ "$(date -u +%s)" -lt "$t" ]; do sleep 20; done; }']
    for comment, argv in cmds:
        lines.append(f"# {comment}")
        lines.append(" ".join(shlex.quote(a) for a in argv) + (" || true" if comment.startswith(TOLERANT) else ""))
    lines.append('echo "plan executed"')
    return "\n".join(lines) + "\n"


def wait_until(iso):
    import time
    from datetime import datetime
    target = datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()
    while time.time() < target:
        time.sleep(min(20.0, target - time.time()))


def jd_from_iso(iso):
    import _kb
    from datetime import datetime
    return float(_kb.ephem.julian_date(datetime.fromisoformat(iso.replace("Z", "+00:00"))))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--here", action="store_true", help="dry run: print the script")
    ap.add_argument("--out", help="write the script to this file")
    ap.add_argument("--execute", action="store_true", help="run the commands now (INDI tools must be installed)")
    ap.add_argument("--realtime", action="store_true")
    ap.add_argument("--sub-exp", type=int, default=10)
    ap.add_argument("--no-precess", action="store_true", help="send J2000 as if it were JNow (to see the seam fail)")
    a = ap.parse_args(argv)
    r = _lab.build()
    cmds = plan_commands(r["local_rows"], r["reqs"], jd_from_iso, a.sub_exp, a.realtime, precess_coords=not a.no_precess)
    text = script(cmds)
    if a.out:
        from pathlib import Path
        p = Path(a.out)
        p.unlink(missing_ok=True)
        p.write_text(text, encoding="utf-8")
        print(f"wrote {p} ({len(cmds)} commands)")
    if a.execute:
        missing = [t for t in ("indi_setprop", "indi_eval") if shutil.which(t) is None]
        if missing:
            print(f"SKIP: {', '.join(missing)} not found - install INDI (see mac_mini/README.md); nothing was sent")
            return 2
        for comment, argv in cmds:
            if argv[0] == "wait_until_utc":
                wait_until(argv[1])
                continue
            print(f"# {comment}\n{' '.join(shlex.quote(x) for x in argv)}", flush=True)
            subprocess.run(argv, check=not comment.startswith(TOLERANT))
        print("plan executed")
        return 0
    if a.here or not a.out:
        print(text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
