"""Recompute every number in L600 #05's Mac mini material (mac_mini/README.md, parts/05.json macMini, qbank 05-mac).

python integrated/research/checks_05_mac.py      -> prints OK, exit 0 (builds the night once, ~20 s on a network drive)
"""
import math
import sys

import mac_checks_common as common

LAB = common.ROOT / "labs" / "L600" / "05-observatory-scheduler"
sys.path.insert(0, str(LAB / "mac_mini"))
import _lab  # noqa: E402
import astropy_check  # noqa: E402
import indi_export  # noqa: E402
import sky  # noqa: E402
import weather  # noqa: E402

FAILS = []


def check(label, ok):
    if not ok:
        FAILS.append(label)


bank = common.load_mac_bank("05")
common.check_bank("05", bank, FAILS)
mm = common.check_mac_mini("05", FAILS)
readme = (LAB / "mac_mini" / "README.md").read_text(encoding="utf-8")
q = {x["id"]: x for x in bank}
r = _lab.build()

# Precession of the night's targets (README, macMini, Q1-Q3)
jd = indi_export.jd_from_iso(r["local_rows"][0]["start_utc"])
shifts = {t.name: indi_export.separation_deg(t.ra_deg, t.dec_deg, *indi_export.precess(t.ra_deg, t.dec_deg, jd))
          for t in sky.REQUESTS}
lo, hi = min(shifts.values()), max(shifts.values())
check("shift range text", f"{lo:.2f}" == "0.09" and f"{hi:.2f}" == "0.37" and "0.09–0.37" in readme)
vega_ra, vega_dec = indi_export.precess(*[(t.ra_deg, t.dec_deg) for t in sky.REQUESTS if t.name == "Vega"][0], jd)
check("q01", common.answer_text(q["05-mac-01"]) == f"{vega_ra / 15:.6f}" and f"{vega_ra:.5f}" in q["05-mac-01"]["question"])
check("q02 range", "0.09-0.37" in common.answer_text(q["05-mac-02"]))
check("q03", common.run_snippet(q["05-mac-03"]["code"]) == common.answer_text(q["05-mac-03"]))
check("q03 numbers", f"{vega_ra:.5f}" in q["05-mac-03"]["code"] and f"{vega_dec:.3f}" in q["05-mac-03"]["code"])
# 39 commands for the 5-block plan (README + macMini)
cmds = indi_export.plan_commands(r["local_rows"], r["reqs"], indi_export.jd_from_iso)
check("39 commands", len(cmds) == 39 and "(39 commands)" in readme and len(r["local_rows"]) == 5)
# Vega's worst airmass 1.93 and the LST route difference 0.0019 deg
check("vega 1.93", r["local_rows"][0]["target"] == "Vega" and round(r["local_rows"][0]["max_airmass"], 2) == 1.93)
lst = astropy_check.compare(r["local_rows"], r["reqs"], astropy_check.lst_route, "lst")
check("lst 0.0019", f"{lst['max_dalt_deg']:.4f}" == "0.0019" and "0.0019" in readme)
# Q5: block z over 100,000 nights, and the same gap over 1,000
p18 = weather.p_complete(18)
check("p18", round(p18, 4) == 0.4163)
z = (0.4100 - 0.4163) / math.sqrt(0.4163 * (1 - 0.4163) / 100_000)
z1k = (0.4100 - 0.4163) / math.sqrt(0.4163 * (1 - 0.4163) / 1_000)
check("q05", common.answer_text(q["05-mac-05"]).startswith(f"{z:.2f}") and f"z = {z1k:.2f}" in q["05-mac-05"]["explanation"])
check("q05 block", any(b == 18 for _, b, _ in r["local"]))
# Q6: CI shrink factor
check("q06", common.answer_text(q["05-mac-06"]) == f"{math.sqrt(100_000 / 2_000):.2f}" and "~7×" in readme)
# Fake-model trial numbers quoted in README / macMini
import io, contextlib, json, shutil, tempfile  # noqa: E401,E402
from pathlib import Path  # noqa: E402
import agent_trials  # noqa: E402
tmp = Path(tempfile.mkdtemp(prefix="checks05-", dir=LAB / "mac_mini"))
try:
    with contextlib.redirect_stdout(io.StringIO()):
        agent_trials.main(["--here", "--out", str(tmp)])
    row = json.loads((tmp / "05-agent-trials.jsonl").read_text(encoding="utf-8").splitlines()[0])
finally:
    shutil.rmtree(tmp, ignore_errors=True)
check("fake kinds", row["violation_kinds"] == {"zone": 1, "airmass": 3} and row["adopted"] == "optimiser")
check("fake text", "{zone: 1, airmass: 3}" in mm["experiments"][0]["steps"][0]["expected"])

if FAILS:
    print("FAIL:", FAILS)
    sys.exit(1)
print("OK")
