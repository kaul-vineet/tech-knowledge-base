"""Try it (lab 21): two edits to solution.py, scored with the 200 seeded adversarial replies.

Run:  python try_it.py    (asserted by test_try_it.py)
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "sim_stub"))
import solution  # noqa: E402,F401  (first: our solution.py, before other labs' folders join sys.path)
import fuzz  # noqa: E402
import incident  # noqa: E402
from alarms import decide  # noqa: E402
from tryit import variant_source  # noqa: E402

SNAPSHOT = incident.snapshot()


def run_variant(name):
    with tempfile.TemporaryDirectory(dir=HERE) as d:  # private copy: parallel runs cannot collide
        tmp = Path(d) / ("tryit_%s.py" % name.replace("-", "_"))
        tmp.write_text(variant_source(str(HERE), name), encoding="utf-8")
        spec = importlib.util.spec_from_file_location(tmp.stem, tmp)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    code = decide(SNAPSHOT)
    changed = published = claims = 0
    for _, text in fuzz.replies(code):
        out = mod.run(lambda m: text, SNAPSHOT)
        changed += out["alarms"] != code
        published += out["accepted"]
        claims += bool(out["accepted"] and solution.STATE_CHANGE.search(out["note"] + out["explanation"]))
    return "alarm sets changed %d/200, replies published %d, published notes claiming a state change %d" % (
        changed, published, claims)


def try_1():
    # Remove the check that rejects "cleared / resolved / false alarm" claims.
    return run_variant("no-state-check")


def try_2():
    # Accept replies with extra keys (e.g. "actions") as long as the two text keys are there.
    return run_variant("extra-keys-ok")


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())
