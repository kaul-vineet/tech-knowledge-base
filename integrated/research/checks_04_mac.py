"""Recompute every number in L600 #04's Mac mini material (mac_mini/README.md, parts/04.json macMini, qbank 04-mac).

python integrated/research/checks_04_mac.py      -> prints OK, exit 0 (runs a 20-board x 12 h site, ~15 s)
"""
import contextlib
import io
import math
import sys

import mac_checks_common as common

LAB = common.ROOT / "labs" / "L600" / "04-microbit-sensor-fleet"
sys.path.insert(0, str(LAB / "mac_mini"))
import make_sim_programs as msp  # noqa: E402
import soak  # noqa: E402

FAILS = []


def check(label, ok):
    if not ok:
        FAILS.append(label)


bank = common.load_mac_bank("04")
common.check_bank("04", bank, FAILS)
mm = common.check_mac_mini("04", FAILS)
q = {x["id"]: x for x in bank}
readme = (LAB / "mac_mini" / "README.md").read_text(encoding="utf-8")
text = str(mm)

# Q1: 16-bit seq at one sample a minute
check("q01 45.5 days", round(0xFFFF / 1440, 1) == 45.5 and common.answer_text(q["04-mac-01"]) == "About 45.5 days")
check("readme/macMini 45.5", "45.5 days" in readme and "45.5 days" in text)
# Q2/Q3: the 1-byte device id, proved by the firmware's own frames()
limit = soak.dev_id_limit()
sites = math.ceil(500 / limit)
check("q03 255", limit == 255)
check("q02 2 x 250", (sites, math.ceil(500 / sites)) == (2, 250) and common.answer_text(q["04-mac-02"]) == "2 sites of 250 boards")
# Q5: snippet executed
check("q05 snippet", common.run_snippet(q["04-mac-05"]["code"]) == common.answer_text(q["04-mac-05"]))
# Q8 + README: oversize frame 3 + 11 x 9 = 102, truncated to 32 on air (stub)
progs = msp.programs()
with contextlib.redirect_stdout(io.StringIO()):
    over = msp.run_on_stub(progs, "node_sim_oversize.py")
    normal = msp.run_on_stub(progs, "node_sim.py")
check("q08 102", 3 + min(27, 11) * 9 == 102 == over["maxframe"] and common.answer_text(q["04-mac-08"]) == "102 bytes")
check("q06 32 on air", over["max_bytes_on_air"] == 32)
check("normal run 30/30", (normal["sampled"], normal["acked"], normal["left"], normal["maxframe"]) == (30, 30, 0, 30))
check("full frame distractor 246", 3 + 27 * 9 == 246)
# macMini + README: the 20-board x 12 h site (seeded, deterministic)
r = soak.site((20, 12, 4))
check("site 14,400 sampled", r["sampled"] == 14400 and r["lost"] == 0 and r["pass"])
check("life 2,419.7 h", r["life_h_min"] == 2419.7 and "2,419.7" in text and "2419.7" in readme)
check("drain 2", r["drain_min"] == 2 and '"drain_min": 2' in readme)

if FAILS:
    print("FAIL:", FAILS)
    sys.exit(1)
print("OK")
