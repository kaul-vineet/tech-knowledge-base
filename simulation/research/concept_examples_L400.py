"""Recomputes the numbers used in the L400 concept notes (content/concepts/L400/*.md) from the labs' fixed versions.

python research/concept_examples_L400.py   (observed output: concept_examples_L400_observed.txt; a few minutes)
Lesson 20 storage timings and the capstone numbers come from storage_options.py and run_capstone.py (their READMEs).
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np

LABS = Path(__file__).resolve().parents[1] / "labs" / "L400"


def load(lab, rel, name):
    sys.path.append(str(LABS / lab))
    spec = importlib.util.spec_from_file_location(name, LABS / lab / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    tw = load("17-digital-twin", "solution/twin.py", "tw")
    for name, kw in (("A", {"twin": tw.Twin(recalibrate=False), "assimilate": False}), ("B", {"twin": tw.Twin(recalibrate=False)}), ("C", {})):
        twin, err = tw.run(**kw)
        print(f"17 option {name}: before {tw.rmse(err, 0, 2500):.3f} | last day {tw.rmse(err, 2880):.3f}; events {[(e['t_min'], e['event']) for e in twin.events][:3]}")
    shipped17 = load("17-digital-twin", "twin.py", "tw_shipped")
    twin, err = shipped17.run()
    print(f"17 shipped: false alarms {sum(e['event'] == 'drift_alarm' and e['t_min'] < 2500 for e in twin.events)}, before-drift RMSE {shipped17.rmse(err, 0, 2500):.3f}")

    opt_fixed = load("18-sim-optimisation", "solution/optimise.py", "opt_fixed")
    opt_shipped = load("18-sim-optimisation", "optimise.py", "opt_shipped")
    for name, m in (("shipped", opt_shipped), ("fixed", opt_fixed)):
        rows = [m.optimise(m.grid_search, k) for k in range(12)]
        print(f"18 {name} grid, 12 macro-reps: bias {np.mean([r['reported'] - r['true'] for r in rows]):+.3f}, "
              f"mean gap {np.mean([r['gap'] for r in rows]):.3f}, worst {max(r['gap'] for r in rows):.3f}")
    print(f"18 truth best {min(opt_fixed.TRUTH, key=lambda d: opt_fixed.TRUTH[d]['mean'])}, se {opt_fixed.TRUTH[(25, 70)]['se']}")

    sg = load("19-surrogates", "surrogate.py", "sg")
    X, y, Xh, yh = sg.design()
    models = sg.fit_all(X, y)
    exact_h = np.array([sg.mmc_queue.erlang_c(3, l, m)["Wq"] for l, m in Xh])
    print("19 holdout RMSE", {k: round(float(np.sqrt(np.mean((m(Xh)[0] - yh) ** 2))), 3) for k, m in models.items()},
          "noise floor", round(float(np.sqrt(np.mean((yh - exact_h) ** 2))), 3))
    print("19 rho 0.95:", {k: round(float(m(np.array([[2.7, 0.95]]))[0][0]), 3) for k, m in models.items()},
          "exact", round(sg.mmc_queue.erlang_c(3, 2.7, 0.95)["Wq"], 3))

    gov = load("21-governance-vv", "solution/governance.py", "gov")
    rows, env = gov.validate()
    print(f"21 envelope {env}; max error inside {max(r['rel_error'] for r in rows if r['rho'] <= env):.3f}; "
          f"elasticities {gov.sensitivity()}; peak {gov.peak_utilisation()}")
