"""Seeded results of every L300 lab, at the precision the lab READMEs print (timings excluded: machine-dependent).

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
for lab in ("12-variance-reduction", "13-calibration", "14-global-sensitivity", "15-cosimulation-fmi",
            "16-performance-scale"):
    sys.path.insert(0, str(HERE.parent / lab))

import calibrate  # noqa: E402
import cosim  # noqa: E402
import numpy as np  # noqa: E402
import perf  # noqa: E402
import sensitivity  # noqa: E402
import variance_reduction as vr  # noqa: E402


def solution(lab, name):
    """The buildTask solution copy (fixed); the lab file itself ships the unfixed version."""
    spec = importlib.util.spec_from_file_location(f"{name}_solution", HERE.parent / lab / "solution" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compute():
    base = vr.plain(20_000)
    vr_fixed, cal_fixed = solution("12-variance-reduction", "variance_reduction"), solution("13-calibration", "calibrate")
    vrows = [vr.antithetic(20_000), vr.control_variate(20_000), vr.antithetic_loop(20_000), vr_fixed.antithetic_loop(20_000)]
    y = calibrate.observed()
    models = calibrate.candidates(calibrate.T_HOURS[calibrate.CAL], y[calibrate.CAL])
    same, hold = calibrate.scores(models, y, calibrate.CAL), calibrate.scores(models, y, ~calibrate.CAL)
    rows = sensitivity.table()
    data = [perf.draws(c) for c in np.random.SeedSequence(perf.SEED).spawn(40)]
    means = perf.mean_wait_vectorised(np.array([s for s, _ in data]), np.array([g for _, g in data]))
    return {
        "12 estimates plain/anti/cv/broken/fixed": [f"{r['mean']:.4f}" for r in [base] + vrows],
        "12 variance ratios anti/cv/broken/fixed": [f"{base['var_per_eval'] / r['var_per_eval']:.2f}" for r in vrows],
        "13 RMSE same-data / holdout per model": [[f"{same[k]:.3f}", f"{hold[k]:.3f}"] for k in same],
        "13 picks same / holdout": [calibrate.select(y)[0], cal_fixed.select(y)[0]],
        "14 S1 / ST per input": [[r["S1"], r["ST"]] for r in rows],
        "14 Morris mu* / sigma per input": [[r["morris_mu_star"], r["morris_sigma"]] for r in rows],
        "15 metrics h=60 / h=900": [cosim.metrics(cosim.run(60)), cosim.metrics(cosim.run(900))],
        "16 mean wait +/- half-width (40 spawned streams)": [f"{x:.3f}" for x in perf.ci(means)],
    }


if __name__ == "__main__":
    result = compute()
    if "--write" in sys.argv:
        GOLDEN.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=1))
