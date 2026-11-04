"""Recompute every number in L600 #07's Mac mini material (mac_mini/README.md, parts/07.json macMini, qbank 07-mac).

python integrated/research/checks_07_mac.py      -> prints OK, exit 0 (re-runs three seeded load tests, ~2 s each)
"""
import contextlib
import io
import sys

import mac_checks_common as common

LAB = common.ROOT / "labs" / "L600" / "07-quantum-job-service"
sys.path.insert(0, str(LAB / "mac_mini"))
import _mac  # noqa: E402
import overnight_load  # noqa: E402
import qubit_sweep  # noqa: E402

FAILS = []


def check(label, ok):
    if not ok:
        FAILS.append(label)


bank = common.load_mac_bank("07")
common.check_bank("07", bank, FAILS)
mm = common.check_mac_mini("07", FAILS)
q = {x["id"]: x for x in bank}
readme = (LAB / "mac_mini" / "README.md").read_text(encoding="utf-8")
text = str(mm)

prof = _mac.mac_profile()
budget16 = prof.recommend(prof.ram_from_gib(16))["budget_gb"]
check("budget 16 GB = 10.06", budget16 == 10.06)
# Q1/Q2: walls at 10.06 GB
w = qubit_sweep.walls(budget16)
check("q01 29", w["statevector_c128"] == 29 and 16 * 2 ** 29 <= 10.06e9 < 16 * 2 ** 30
      and common.answer_text(q["07-mac-01"]) == "29 qubits")
check("q02 14", w["density_matrix_c128"] == 14 and 16 * 4 ** 14 <= 10.06e9 < 16 * 4 ** 15
      and common.answer_text(q["07-mac-02"]) == "14")
by = {g: qubit_sweep.walls(prof.recommend(prof.ram_from_gib(g))["budget_gb"]) for g in (16, 24, 32, 64)}
check("walls by RAM", [by[g]["statevector_c128"] for g in by] == [29, 30, 30, 31]
      and [by[g]["density_matrix_c128"] for g in by] == [14, 15, 15, 15])
check("macMini walls text", "29-31 qubits, density matrix 14-15" in text)
# Q5 + README + macMini: seeded load tests
with contextlib.redirect_stdout(io.StringIO()):
    s7, s8, s8x2 = overnight_load.one((1, 7, 240)), overnight_load.one((1, 8, 240)), overnight_load.one((2, 8, 240))
check("seed 7 p95 18.38 pass", s7["p95_queue_s"] == 18.38 and s7["fitness_pass"])
check("seed 8 p95 170.49 fail", s8["p95_queue_s"] == 170.49 and not s8["fitness_pass"])
check("seed 8 x2 p95 19.2 pass", s8x2["p95_queue_s"] == 19.2 and s8x2["fitness_pass"])
check("contracts hold", s7["contract_violations"] == s8["contract_violations"] == s8x2["contract_violations"] == 0)
check("readme numbers", '"p95_queue_s": 170.49' in readme and '"p95_queue_s": 18.38' in readme)
check("q05 numbers", "18.4 s" in q["07-mac-05"]["question"] and "170.5 s" in q["07-mac-05"]["question"])
# Q6: snippet executed
check("q06 snippet", common.run_snippet(q["07-mac-06"]["code"]) == common.answer_text(q["07-mac-06"]))

if FAILS:
    print("FAIL:", FAILS)
    sys.exit(1)
print("OK")
