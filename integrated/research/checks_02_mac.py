"""Recompute every number in L600 #02's Mac mini material (mac_mini/README.md, parts/02.json macMini, qbank 02-mac).

python integrated/research/checks_02_mac.py      -> prints OK, exit 0
"""
import math
import sys

import numpy as np
from cryptography.hazmat.primitives.asymmetric import mldsa, mlkem

import mac_checks_common as common

LAB = common.ROOT / "labs" / "L600" / "02-quantum-safe-migration"
sys.path.insert(0, str(LAB / "mac_mini"))
import _mac  # noqa: E402
import fitness  # noqa: E402
import order_wall  # noqa: E402
import qiskit_crosscheck as qc  # noqa: E402
import shor_sim  # noqa: E402

FAILS = []


def check(label, ok):
    if not ok:
        FAILS.append(label)


bank = common.load_mac_bank("02")
common.check_bank("02", bank, FAILS)
mm = common.check_mac_mini("02", FAILS)
q = {x["id"]: x for x in bank}
readme = (LAB / "mac_mini" / "README.md").read_text(encoding="utf-8")
text = str(mm)
BPA = 121.9   # bytes per amplitude measured here (order_wall.py --here, README real output)

# Q1: 3 qubits per bit of N
check("q01", order_wall.qubits(899) == 30 and common.answer_text(q["02-mac-01"]) == "30")
# Q2: 121.9 B x 2^27
gb = BPA * 2 ** 27 / 1e9
check("q02", round(gb, 1) == 16.4 and common.answer_text(q["02-mac-02"]) == "About 16.4 GB")
check("q02 textbook distractor", round(16 * 2 ** 27 / 1e9, 1) == 2.1)
# Q3 + macMini + README: walls by RAM from mac_profile budgets
prof = _mac.mac_profile()
walls = {g: order_wall.wall(BPA, prof.recommend(prof.ram_from_gib(g))["budget_gb"]) for g in (16, 24, 32, 64)}
check("wall 16 GB -> 143", walls[16]["largest_N"] == 143 and walls[16]["need_GB"] == 2.045)
check("wall 24/32/64 -> 323", all(walls[g]["largest_N"] == 323 for g in (24, 32, 64)))
check("q03 899 needs ~131 GB", round(BPA * 2 ** 30 / 1e9) == 131 and walls[24]["next_need_GB"] == 130.89)
check("macMini N=143 / N=323", "N = 143 on 16 GB, N = 323 on 24 GB" in text)
check("readme 131 GB", "~131 GB" in readme and "16.4 GB" in readme)
# Q4: ML-KEM-1024 share vs the 1,400 B client flight (sizes from the library)
ek1024 = len(mlkem.MLKEM1024PrivateKey.generate().public_key().public_bytes_raw())
ek768 = len(mlkem.MLKEM768PrivateKey.generate().public_key().public_bytes_raw())
check("q04 1600 > 1400", ek1024 + 32 == 1600 > fitness.BUDGET["client_flight_bytes"] == 1400 and ek768 + 32 == 1216)
sig65 = len(mldsa.MLDSA65PrivateKey.generate().sign(b"x"))
sig87 = len(mldsa.MLDSA87PrivateKey.generate().sign(b"x"))
check("macMini sizes", sig65 == 3309 and sig87 == 4627 and "3309 B (ML-DSA-65), 4627 B (ML-DSA-87)" in text)
check("ML-KEM-512 absent", not hasattr(mlkem, "MLKEM512PrivateKey"))
# Q5 + crosscheck thresholds: sampling-only TVD for N = 35 at 20k and 100k shots
p = shor_sim.run_order_finding(35, 2)["probs"]
rng = np.random.default_rng(1)
t20 = [qc.tvd(rng.multinomial(20_000, p / p.sum()), p) for _ in range(200)]
t100 = [qc.tvd(rng.multinomial(100_000, p / p.sum()), p) for _ in range(200)]
check("q05 20k shots ~0.026", 0.02 < np.mean(t20) < 0.03 and max(t20) > 0.025)
check("100k shots below threshold", np.percentile(t100, 99) < 0.016 < qc.TVD_MAX)
check("q05 ~130 outcomes", 120 <= int((p > 1e-4).sum()) <= 140)
check("crosscheck constants", (qc.SHOTS, qc.TVD_MAX) == (100_000, 0.025))
# Q6: snippet executed
check("q06 snippet", common.run_snippet(q["02-mac-06"]["code"]) == common.answer_text(q["02-mac-06"]))
check("q06 = counts_to_probs", list(qc.counts_to_probs({"01": 3, "10": 1}, 2)) == [0, 3, 1, 0])

if FAILS:
    print("FAIL:", FAILS)
    sys.exit(1)
print("OK")
