"""Recompute every number in L600 #08's Mac mini material (mac_mini/README.md, parts/08.json macMini, qbank 08-mac).

python integrated/research/checks_08_mac.py      -> prints OK, exit 0 (runs the fake-model corpus on both hosts)
"""
import contextlib
import io
import json
import math
import shutil
import sys
import tempfile
from pathlib import Path

import mac_checks_common as common

LAB = common.ROOT / "labs" / "L600" / "08-secure-agent-tools"
sys.path.insert(0, str(LAB / "mac_mini"))
import _lab  # noqa: E402,F401
import corpus  # noqa: E402
import injection_eval  # noqa: E402
from model_endpoint import RemoteModelRefused, check_model_url  # noqa: E402

FAILS = []


def check(label, ok):
    if not ok:
        FAILS.append(label)


bank = common.load_mac_bank("08")
common.check_bank("08", bank, FAILS)
mm = common.check_mac_mini("08", FAILS)
readme = (LAB / "mac_mini" / "README.md").read_text(encoding="utf-8")
q = {x["id"]: x for x in bank}

tmp = Path(tempfile.mkdtemp(prefix="checks08-", dir=LAB / "mac_mini"))
try:
    with contextlib.redirect_stdout(io.StringIO()):
        injection_eval.main(["--here", "--naive", "--out", str(tmp)])
    s = json.loads((tmp / "08-injection-eval.jsonl").read_text(encoding="utf-8").splitlines()[0])
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# Fake baseline quoted in README, macMini, Q1, Q3
check("items 40", s["items"] == len(corpus.build()) == 40)
check("fake numbers", (s["obeyed"], s["executed"], s["unscoped"], s["effects"], s["naive_executed"], s["naive_effects"])
      == (24, 0, 0, 0, 24, 16))
lo, hi = injection_eval.wilson(24, 40)
check("wilson", (round(lo, 3), round(hi, 3)) == (0.446, 0.737))
check("readme fake", "obeyed 24/40 (0.60, Wilson 0.446-0.737)" in readme and "executed 24 and recorded 16" in readme)
check("macMini fake", "obeyed 24/40 (0.60, Wilson 0.446-0.737)" in mm["experiments"][0]["steps"][0]["expected"])
check("q01", common.answer_text(q["08-mac-01"]) == f"{lo:.3f} to {hi:.3f}")
wald = (0.6 - 1.96 * math.sqrt(0.24 / 40), 0.6 + 1.96 * math.sqrt(0.24 / 40))
check("q01 wald distractor", f"{wald[0]:.3f} to {wald[1]:.3f}" in q["08-mac-01"]["options"])
check("q01 explanation", "0.591" in q["08-mac-01"]["explanation"]
      and f"{(lo + hi) / 2:.3f}" == "0.591" and f"{(hi - lo) / 2:.3f}" == "0.145")
by = s["obeyed_by_tool"]
check("q03", by == {"delete_file": 6, "read_file": 8, "save_memory": 1, "send_email": 9}
      and by["delete_file"] + by["save_memory"] + by["send_email"] == s["naive_effects"])
# Q2: half-width at 1,000 items, and the 40-item width quoted in README
check("q02", common.answer_text(q["08-mac-02"]) == f"+/-{1.96 * math.sqrt(0.24 / 1000):.2f}")
check("readme widths", "±~0.15" in readme and "about ±0.03" in readme and round((hi - lo) / 2, 2) == 0.15)
check("overnight items", 200 * 5 == 1000 and "1,000 corpus items" in readme)
# Q4: executed snippet
check("q04", common.run_snippet(q["08-mac-04"]["code"]) == common.answer_text(q["08-mac-04"]))
# The loopback guard behaves as Q5 and Experiment 2 describe
for url, ok in (("http://localhost:11434/v1", True), ("http://mac-mini.local:11434/v1", False),
                ("http://192.168.1.20:11434/v1", False)):
    try:
        check_model_url(url)
        got = True
    except RemoteModelRefused:
        got = False
    check(f"guard {url}", got == ok)

if FAILS:
    print("FAIL:", FAILS)
    sys.exit(1)
print("OK")
