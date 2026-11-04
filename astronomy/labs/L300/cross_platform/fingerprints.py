"""Seeded results of every L300 lab, at the precision the lab READMEs print (timings excluded).

CI runs test_fingerprints.py on Linux, macOS (Apple silicon) and Windows: all three must reproduce golden.json.
python fingerprints.py           # print the fingerprints of this machine
python fingerprints.py --write   # overwrite golden.json (only after an intended change to a lab)
"""
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
GOLDEN = HERE / "golden.json"
LABS = ("12-observation-planning", "13-ccd-calibration", "14-plate-solving", "15-honest-uncertainty",
        "16-reproducible-pipelines")


def load(lab, rel, name):
    """Import a lab file under a unique name with its own folder first on sys.path (labs reuse module names)."""
    sys.path.insert(0, str(HERE.parent / lab))
    try:
        spec = importlib.util.spec_from_file_location(name, HERE.parent / lab / rel)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


def compute():
    p12, f12 = load(LABS[0], "plan.py", "p12"), load(LABS[0], "solution/plan.py", "f12")
    c13, f13 = load(LABS[1], "calibrate.py", "c13"), load(LABS[1], "solution/calibrate.py", "f13")
    s14, f14 = load(LABS[2], "platesolve.py", "s14"), load(LABS[2], "solution/platesolve.py", "f14")
    t15, f15 = load(LABS[3], "transit_fit.py", "t15"), load(LABS[3], "solution/transit_fit.py", "f15")
    p16, f16 = load(LABS[4], "pipeline.py", "p16"), load(LABS[4], "solution/pipeline.py", "f16")
    y = t15.make_data()
    p = t15.fit_lm(y)
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        stale, fresh = p16.demo(Path(a))[2], f16.demo(Path(b))[2]
    return {
        "12 shipped / fixed schedule": [[r["target"], r["start"]] for r in p12.schedule()[0]] + ["|"]
        + [[r["target"], r["start"]] for r in f12.schedule()[0]],
        "12 dark window": list(p12.dark_window()),
        "13 robust rms shipped / fixed": [c13.run(log_path=None)[1]["robust_rms_percent"],
                                          f13.run(log_path=None)[1]["robust_rms_percent"]],
        "14 shipped / fixed": [s14.run("cassiopeia"), f14.run("cassiopeia")],
        "15 fit + formal sigma shipped / fixed": [[round(float(v), 5) for v in p],
                                                  [round(float(v), 5) for v in t15.uncertainty(y, p)],
                                                  [round(float(v), 5) for v in f15.uncertainty(y, p)]],
        "16 v2 period shipped (stale) / fixed": [stale["period_d"], fresh["period_d"]],
    }


if __name__ == "__main__":
    result = compute()
    if "--write" in sys.argv:
        GOLDEN.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=1))
