"""Recompute every number in L600 #01's Mac mini material (mac_mini/README.md, parts/01.json macMini, qbank 01-mac).

python integrated/research/checks_01_mac.py      -> prints OK, exit 0
Timings are not recomputed (they are machine-specific); the arithmetic that turns them into budgets is.
"""
import math
import sys

import mac_checks_common as common

LAB = common.ROOT / "labs" / "L600" / "01-pq-replicated-messaging"
sys.path.insert(0, str(LAB / "mac_mini"))
import bench_crypto  # noqa: E402
import replica  # noqa: E402

FAILS = []


def check(label, ok):
    if not ok:
        FAILS.append(label)


bank = common.load_mac_bank("01")
common.check_bank("01", bank, FAILS)
mm = common.check_mac_mini("01", FAILS)
q = {x["id"]: x for x in bank}
readme = (LAB / "mac_mini" / "README.md").read_text(encoding="utf-8")
text = str(mm)

# Q1/Q2 + README budget line: the budget maths of bench_crypto.budgets() on the sandbox's quoted timings
rows = [{"op": "project welcome (hybrid KEM + HKDF + AES-GCM wrap)", "us_per_call": 165.61},
        {"op": "project seal (envelope + AES-256-GCM + fingerprint)", "us_per_call": 24.28}]
b = bench_crypto.budgets(rows)
check("q01 603", b["max_members_in_rotate_budget"] == math.floor(100_000 / 165.61) == 603
      and common.answer_text(q["01-mac-01"]) == "603")
check("q01 1,656 ms distractor", b["rotate_ms_for_members"][10000] == 1656.1)
check("q02 41,186/s", b["seals_per_s_one_core"] == 41186)
days = 2 ** 32 / 41186 / 86400
check("q02 1.2 days", round(days, 1) == 1.2 == b["days_to_2^32_at_that_rate"]
      and common.answer_text(q["01-mac-02"]) == "About 1.2 days")
check("readme budget line", '"max_members_in_rotate_budget": 603' in readme and '"days_to_2^32_at_that_rate": 1.2' in readme)
check("macMini 603 / 1.2 days", "603 members and 1.2 days" in text)
# Q5: snippet executed
check("q05 snippet", common.run_snippet(q["01-mac-05"]["code"]) == common.answer_text(q["01-mac-05"]))
# Q5 matches the solution's layout
import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location("sol01", LAB / "solution" / "nonce_derived.py")
sol = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sol)
dn = sol.DerivedNonce()
dn.next(3)
check("q05 = solution", dn.next(3).hex() == common.answer_text(q["01-mac-05"]))
# Q4: the shipped counter's first nonce, as reported by the failure lab across processes
import nonce_derived  # noqa: E402
check("q04 first nonce", nonce_derived.DerivedNonce().next(7).hex() == "000000000000000000000001"
      and "000000000000000000000001" in readme and "000000000000000000000001" in text)
# README / macMini quote the same here-run observations
for s in ('"reused_nonces": 62', '"ciphertexts_on_wire": 301', '"kills": 4'):
    check(f"readme {s}", s in readme)
check("macMini 62 / 301", "62 reused nonces" in text and "301 ciphertexts on the wire" in text)
# Q8: a torn last line is dropped by read_log (the replay rule the question explains)
d = LAB / "mac_mini" / "runs" / "checks-torn"
d.mkdir(parents=True, exist_ok=True)
(d / "log.jsonl").write_text('{"i": 1, "t": 1, "ikey": "a", "env": {}}\n{"i": 2, "t"', encoding="utf-8")
check("q08 torn line", [e["ikey"] for e in replica.read_log(d)] == ["a"])
(d / "log.jsonl").unlink()
d.rmdir()

if FAILS:
    print("FAIL:", FAILS)
    sys.exit(1)
print("OK")
