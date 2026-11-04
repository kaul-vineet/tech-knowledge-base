"""tryIt 1: is Python's own json.dumps(sort_keys=True, separators=(',', ':')) 'canonical enough' for mirror m2?
Predict first: do the mirrors converge? Then: would they still converge if a later release carried a tiny flux
(2.5e-05), a 1e-07 error, a 1e21 count or a float written as 5.0 by the producer?"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import canonical as C  # noqa: E402
import checks  # noqa: E402
import world as W  # noqa: E402


def python_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


orig = C.platform_dumps
C.platform_dumps = python_json  # the float-format fault slot now holds Python's json module
try:
    w = W.World("float-format")
finally:
    C.platform_dumps = orig
ok, d = checks.m4_replicated(w)
print("1) m2 = json.dumps: converged", ok, "| rounds", d["rounds"], "| conflicts", d["conflicts"])
values = [5.0, 2.5e-05, 1e-07, 1e21, 270.70193010476163]
py, jcs = [python_json(v).decode() for v in values], [C.dumps(v).decode() for v in values]
print("1) json.dumps:", py)
print("1) JCS       :", jcs, "| differ:", sum(a != b for a, b in zip(py, jcs)), "of", len(values))
