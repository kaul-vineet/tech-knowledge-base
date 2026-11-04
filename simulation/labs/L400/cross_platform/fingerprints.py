"""Seeded results of every L400 lab (fixed versions) and the capstone, at the precision the READMEs print.

Timings are excluded (machine-dependent). CI runs test_fingerprints.py on Linux, macOS (Apple silicon) and Windows.
python fingerprints.py           # print this machine's fingerprints
python fingerprints.py --write   # overwrite golden.json (only after an intended change to a lab)
"""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GOLDEN = HERE / "golden.json"
L400 = HERE.parent


def load(lab, rel, name):
    path = L400 / lab / rel
    sys.path.append(str(path.parent if path.parent.name != "solution" else path.parent.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compute():
    tw = load("17-digital-twin", "solution/twin.py", "fp_twin")
    twin, errors = tw.run()
    opt = load("18-sim-optimisation", "solution/optimise.py", "fp_opt")
    r18 = opt.optimise(opt.grid_search, 0)
    sg = load("19-surrogates", "surrogate.py", "fp_sur")
    X, y, Xh, yh = sg.design()
    models = sg.fit_all(X, y)
    sw = load("20-parallel-scale", "solution/sweep.py", "fp_sweep")
    tasks = sw.seeded([(0, 0), (11, 9)])
    gov = load("21-governance-vv", "solution/governance.py", "fp_gov")
    rows, envelope = gov.validate()
    sys.path.append(str(L400 / "22-capstone"))
    import pipeline  # noqa: E402  (capstone)
    inp = pipeline.model_inputs(pipeline.history())
    return {
        "17 events": [[e["t_min"], e["event"]] for e in twin.events],
        "17 last-day RMSE / refit a": [f"{tw.rmse(errors, 2880):.3f}", f"{twin.a:.4f}"],
        "18 grid+OCBA macro 0 design / gap": [list(r18["design"]), f"{r18['gap']:.3f}"],
        "19 holdout RMSE poly / gp / rff": [f"{(lambda e: (e ** 2).mean() ** 0.5)(m(Xh)[0] - yh):.3f}" for m in models.values()],
        "20 Wq of tasks (0,0) and (11,9)": [f"{sw.run_task(t)[4]:.6f}" for t in tasks],
        "21 envelope / max error": [envelope, f"{max(r['rel_error'] for r in rows if r['rho'] <= envelope):.3f}"],
        "22 rates / ks / cv": [inp["rates"], inp["ks_d"], inp["cv"]],
        "22 plan": pipeline.plan(inp["rates"], inp, 4.5),
    }


if __name__ == "__main__":
    result = compute()
    if "--write" in sys.argv:
        GOLDEN.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(result))
