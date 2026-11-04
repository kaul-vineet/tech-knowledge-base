"""Recompute every number in L600 #03's Mac mini material (mac_mini/README.md, parts/03.json macMini, qbank 03-mac).

python integrated/research/checks_03_mac.py      -> prints OK, exit 0 (runs the fake-model comparison once)
"""
import math
import shutil
import sys
import tempfile
from pathlib import Path

import mac_checks_common as common

LAB = common.ROOT / "labs" / "L600" / "03-agent-driven-simulation"
sys.path.insert(0, str(LAB / "mac_mini"))
import _lab  # noqa: E402,F401
import compare_models  # noqa: E402
import mac_profile  # noqa: E402
import pipeline  # noqa: E402
import run_project  # noqa: E402

FAILS = []


def check(label, ok):
    if not ok:
        FAILS.append(label)


bank = common.load_mac_bank("03")
common.check_bank("03", bank, FAILS)
mm = common.check_mac_mini("03", FAILS)
readme = (LAB / "mac_mini" / "README.md").read_text(encoding="utf-8")
q = {x["id"]: x for x in bank}

# Q1: Sobol cost at n = 8192 (d = 4 inputs, SCREEN_CUSTOMERS per run)
d = len(pipeline.SCREEN_NAMES)
runs = 8192 * (d + 2)
check("q01", common.answer_text(q["03-mac-01"]) == f"{runs * pipeline.SCREEN_CUSTOMERS:,}")
check("readme 49,152 runs", f"{runs:,} runs" in readme)
# Q2: z for coverage 0.930 over 2000 experiments
z = (0.930 - 0.95) / math.sqrt(0.95 * 0.05 / 2000)
check("q02", common.answer_text(q["03-mac-02"]).startswith(f"{z:.2f}"))
# Q7 and README: largest sobol n that fits SIM_BUDGET in a fresh session
n_max = run_project.SIM_BUDGET // ((d + 2) * pipeline.SCREEN_CUSTOMERS)
check("q07", common.answer_text(q["03-mac-07"]) == str(n_max))
check("readme n <= 50", f"at most n = {n_max} today" in readme and f"n <= {n_max}" in mm["experiments"][2]["decides"])
check("sobol 64 over budget", 64 * (d + 2) * pipeline.SCREEN_CUSTOMERS > run_project.SIM_BUDGET)
# Q8: executed snippet
check("q08", common.run_snippet(q["03-mac-08"]["code"]) == common.answer_text(q["03-mac-08"]))
# coverage design in README: 4 rhos x 2000 x 10
check("80,000 runs", 4 * 2000 * 10 == 80_000 and "80,000" in readme)
# Model lists quoted in README / macMini come from mac_profile
check("16 GB models", mac_profile.recommend(mac_profile.ram_from_gib(16))["compare_models"] == ["qwen2.5:3b", "qwen2.5:7b", "qwen2.5:14b"])
check("64 GB models", mac_profile.recommend(mac_profile.ram_from_gib(64))["compare_models"] == ["qwen2.5:7b", "qwen2.5:14b", "qwen2.5:32b"])
# Shared README table == generated table
shared = (common.ROOT / "mac-mini" / "README.md").read_text(encoding="utf-8")
check("shared README table", mac_profile.table([16, 24, 32, 64], markdown=True) in shared)
# Fake-model row quoted in README, macMini and Q4/Q5 context
tmp = Path(tempfile.mkdtemp(prefix="checks03-", dir=LAB / "mac_mini"))
try:
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        compare_models.main(["--here", "--out", str(tmp)])
    import json
    row = json.loads((tmp / "03-compare-models.jsonl").read_text(encoding="utf-8").splitlines()[0])
finally:
    shutil.rmtree(tmp, ignore_errors=True)
check("fake row", (row["contract_rejected"], row["budget_rejected"], row["claims_dropped"], row["budget_spent"])
      == (1, 1, 1, 270000))
check("fake traced", row["numbers_found"] == row["published_traced"] == 7)
check("macMini fake text", "contract_rejected 1, budget_rejected 1, claims_dropped 1, budget_spent 270000"
      in mm["experiments"][0]["steps"][1]["expected"])

if FAILS:
    print("FAIL:", FAILS)
    sys.exit(1)
print("OK")
