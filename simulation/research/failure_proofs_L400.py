"""Fail-before / pass-after evidence for every L400 failureLab: each fix's acceptance check is applied to the shipped
lab file (unfixed, must FAIL) and to the buildTask solution in solution/ (must PASS).
python research/failure_proofs_L400.py      (several minutes: lessons 18 and 20 run real optimisations / pools)
"""
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

LABS = Path(__file__).resolve().parents[1] / "labs" / "L400"
for lab in ("17-digital-twin", "18-sim-optimisation", "19-surrogates", "20-parallel-scale", "21-governance-vv"):
    sys.path.append(str(LABS / lab))


def load(lab, rel, name):
    spec = importlib.util.spec_from_file_location(name, LABS / lab / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check17(m):  # fix acceptance: no drift alarm before the real change at t = 2500 min
    twin, _ = m.run()
    return not [e for e in twin.events if e["event"] == "drift_alarm" and e["t_min"] < 2500]


def check18(m):  # fix acceptance: worst optimality gap of the grid within the indifference zone over 5 macro-reps
    return max(m.optimise(m.grid_search, k)["gap"] for k in range(5)) <= 0.10


def check19(m):  # fix acceptance: a what-if at rho 0.95 is not answered by the surrogate
    X, y, _, _ = m.design()
    return m.what_if(m.fit_gp(X, y), 2.7, 0.95)["source"] != "surrogate"


def check20(m):  # fix acceptance: crash + resume stores exactly the clean results
    import sweep
    m.run_task, m.REPS = sweep.run_task, 3
    with tempfile.TemporaryDirectory() as tmp:
        clean, resumed = Path(tmp) / "c.db", Path(tmp) / "r.db"
        m.run_sweep(clean, workers=1)
        try:
            m.run_sweep(resumed, workers=1, crash_after=10)
        except m.Crash:
            m.run_sweep(resumed, workers=1)
        return m.checksum(clean) == m.checksum(resumed)


def check21(m):  # fix acceptance: the overclaiming draft card gets findings
    card = json.loads((LABS / "21-governance-vv" / "cards" / "draft_overclaiming.json").read_text(encoding="utf-8"))
    ev = {"verification": {"tests_run": 7, "failures": 0}, "envelope_rho_max": 0.85, "max_rel_error_in_envelope": 0.055,
          "most_influential": "mu", "code_sha256": m.sha256(m.MODEL_FILE), "data_sha256": m.sha256(m.DATA_FILE)}
    return len(m.check_card(card, ev)) >= 4


CASES = [("17-digital-twin", "twin", check17), ("18-sim-optimisation", "optimise", check18),
         ("19-surrogates", "surrogate", check19), ("20-parallel-scale", "sweep", check20),
         ("21-governance-vv", "governance", check21)]

if __name__ == "__main__":  # lesson 20 starts spawn pools
    for lab, name, check in CASES:
        shipped = load(lab, f"{name}.py", f"{name}_shipped")
        fixed = load(lab, f"solution/{name}.py", f"{name}_fixed")
        print(f"{lab}: shipped {'PASS' if check(shipped) else 'FAIL'} | solution {'PASS' if check(fixed) else 'FAIL'}")
