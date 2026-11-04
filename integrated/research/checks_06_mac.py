"""Recompute every number in L600 #06's Mac mini material (mac_mini/README.md, parts/06.json macMini, qbank 06-mac).

python integrated/research/checks_06_mac.py      -> prints OK, exit 0
"""
import contextlib
import io
import sys

import mac_checks_common as common

LAB = common.ROOT / "labs" / "L600" / "06-signed-science-data"
sys.path.insert(0, str(LAB / "mac_mini"))
import _mac  # noqa: E402,F401  (puts the lab folder on sys.path)
import canonical as C  # noqa: E402
import jcs_crosscheck  # noqa: E402
import merkle  # noqa: E402
import scale_bench as sb  # noqa: E402

FAILS = []


def check(label, ok):
    if not ok:
        FAILS.append(label)


bank = common.load_mac_bank("06")
common.check_bank("06", bank, FAILS)
mm = common.check_mac_mini("06", FAILS)
q = {x["id"]: x for x in bank}
readme = (LAB / "mac_mini" / "README.md").read_text(encoding="utf-8")
text = str(mm)

# Q1 + macMini: proof length ceil(log2 n) for 1e5, 1e6, 1e7 rows
hashes = [(n - 1).bit_length() for n in (10 ** 5, 10 ** 6, 10 ** 7)]
check("proof hashes 17/20/24", hashes == [17, 20, 24] and "proof_hashes_max 17, 20, 24" in text)
check("q01 24", common.answer_text(q["06-mac-01"]) == "24" and 2 ** 23 < 10 ** 7 <= 2 ** 24)
leaves = [f"r{i}".encode() for i in range(1000)]
lv = sb.build_levels([merkle.leaf_hash(x) for x in leaves])
check("proof length = bit_length", max(len(sb.proof(lv, m)) for m in range(1000)) == (1000 - 1).bit_length())
# Q2: traffic ratio of the fault run
ratio = 4_839_263 / 174_951
check("q02 ~28x", round(ratio) == 28 and common.answer_text(q["06-mac-02"]) == "About 28 times")
check("readme bytes", "4839263" in readme and "174951" in readme and "28" in readme)
# Q5: snippet executed; the stack is the binary representation of n
check("q05 snippet", common.run_snippet(q["06-mac-05"]["code"]) == common.answer_text(q["06-mac-05"]))
stack = sb.stream_push([], [merkle.leaf_hash(b"x%d" % i) for i in range(11)])
check("q05 = stream_push heights", [k for k, _ in stack] == [3, 1, 0])
check("streaming root = mth", sb.stream_root([merkle.leaf_hash(x) for x in leaves]) == merkle.mth(leaves))
# JCS: 8 vectors, 6 of them change under the failure lab's platform_dumps (no Node needed for this count)
vecs = jcs_crosscheck.vectors()
diff = sum(C.platform_dumps(v["value"]) != C.dumps(v["value"]) for v in vecs)
check("jcs 8 vectors / 6 differ", len(vecs) == 8 and diff == 6 and '"platform_dumps_vectors_that_differ": 6' in readme)
check("rfc8785 sample", C.dumps(next(v for v in vecs if v["id"] == "rfc8785-sample")["value"])
      == jcs_crosscheck.RFC8785_SAMPLE_OUT.encode())
# README: the 10,000-row sandbox root is reproducible
with contextlib.redirect_stdout(io.StringIO()):
    r = sb.bench(10000)
check("10k root 8923a7bff6a28e32", r["root"] == "8923a7bff6a28e32" and r["proof_hashes_max"] == 14 and "8923a7bff6a28e32" in readme)

if FAILS:
    print("FAIL:", FAILS)
    sys.exit(1)
print("OK")
