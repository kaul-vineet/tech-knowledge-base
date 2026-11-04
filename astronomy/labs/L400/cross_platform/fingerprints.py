"""Seeded results of every L400 lab and the capstone, at the precision the READMEs print (timings excluded).

CI runs test_fingerprints.py on Linux, macOS (Apple silicon) and Windows: all three must reproduce golden.json.
python fingerprints.py           # print the fingerprints of this machine
python fingerprints.py --write   # overwrite golden.json (only after an intended change to a lab)
"""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GOLDEN = HERE / "golden.json"


def load(lab, rel, name):
    sys.path.insert(0, str(HERE.parent / lab))
    try:
        spec = importlib.util.spec_from_file_location(name, HERE.parent / lab / rel)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


def compute():
    s17 = load("17-survey-pipeline", "solution/survey.py", "s17")
    raws, bias, flat, truth = s17.sim.night()
    rows, _, _ = s17.run("C", raws, bias, flat)
    a18 = load("18-alert-broker", "solution/alerts.py", "a18")
    ex = a18.sim.nights()
    alerts18 = {o: a18.summary(o, a18.run(o, ex), ex) for o in "ABC"}
    c19 = load("19-big-catalogues", "solution/catalog.py", "c19")
    rows19 = c19.main(n=200_000)
    m20 = load("20-model-comparison", "solution/compare.py", "m20")
    v, err = m20.g.observed()
    r21 = load("21-open-data-practice", "solution/release.py", "r21")
    cap = load("22-capstone", "run_capstone.py", "cap")
    results, _ = cap.analyse_all()
    return {
        "17 catalogue sha / completeness / purity": [s17.checksum(rows), *s17.score(rows, truth)],
        "18 alerts per night / real fraction A B C": [[alerts18[o]["alerts_per_night"], alerts18[o]["real_fraction"]]
                                                       for o in "ABC"],
        "19 wrong cones / found (200k)": [[r["wrong_cones"], r["sources_found"]] for r in rows19],
        "20 chi2 per model / pick": [[r["chi2"] for r in m20.table(m20.g.R, v, err)], m20.select(m20.g.R, v, err)[0]],
        "21 release licence": r21.release_licence(r21.inputs.INPUTS),
        "22 periods / verdicts": {s: [r["period_d"], r["verdict"]] for s, r in results.items()},
        "22 fitted depths ppm": {s: r["fit"]["depth_ppm"] for s, r in results.items() if "fit" in r},
    }


if __name__ == "__main__":
    result = compute()
    if "--write" in sys.argv:
        GOLDEN.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=1))
