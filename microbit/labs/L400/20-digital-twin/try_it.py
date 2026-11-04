"""Try it (lab 20): one edit to twin.py, one to solution.py, scored on the same telemetry.

Run:  python try_it.py    (asserted by test_try_it.py)
"""
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "sim_stub"))
import drift_eval  # noqa: E402
from tryit import variant_source  # noqa: E402


def run_variant(name):
    with tempfile.TemporaryDirectory(dir=HERE) as d:  # private copy: parallel runs cannot collide
        tmp = str(Path(d) / ("tryit_%s.py" % name.replace("-", "_")))
        Path(tmp).write_text(variant_source(str(HERE), name), encoding="utf-8")
        return json.dumps(drift_eval.summary(tmp)["detected_after_windows"], sort_keys=True) + \
            " | false alarms: fixture %d, synthetic %d per 1000" % (
                drift_eval.run(tmp)[0]["false_alarms"], drift_eval.synthetic_false_alarms(tmp))


def try_1():
    # twin.py with a 3-sigma limit instead of 2.
    return run_variant("z-limit-3")


def try_2():
    # CUSUM without the slack K (K = 0).
    return run_variant("no-slack")


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())
