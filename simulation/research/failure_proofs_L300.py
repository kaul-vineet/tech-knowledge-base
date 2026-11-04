"""Fail-before / pass-after evidence for every L300 failureLab: the FIX's acceptance check is applied to the shipped
lab file (unfixed, must FAIL) and to the buildTask solution copy in solution/ (must PASS).
python research/failure_proofs_L300.py
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np

LABS = Path(__file__).resolve().parents[1] / "labs" / "L300"
for lab in ("12-variance-reduction", "13-calibration", "14-global-sensitivity", "15-cosimulation-fmi",
            "16-performance-scale"):
    sys.path.insert(0, str(LABS / lab))

import calibrate as cal  # noqa: E402
import cosim  # noqa: E402
import perf  # noqa: E402
import sensitivity as sa  # noqa: E402
import variance_reduction as vr  # noqa: E402


def solution(lab, name):
    spec = importlib.util.spec_from_file_location(f"{name}_solution", LABS / lab / "solution" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check12(m):  # fix acceptance: pairs anti-correlate and the variance ratio is > 1.3
    r = m.antithetic_loop(20_000)
    return r["rho"] < -0.25 and vr.plain(20_000)["var_per_eval"] / r["var_per_eval"] > 1.3


def check13(m):  # fix acceptance: the chosen model forecasts the unseen 8-12 h within 0.2 C
    y = cal.observed()
    best = m.select(y)[0]
    return cal.scores(cal.candidates(cal.T_HOURS[cal.CAL], y[cal.CAL]), y, ~cal.CAL)[best] < 0.2


def check14(m):  # fix acceptance: the screened two-input model keeps > 95% of the output variance
    return sa.variance_kept(m.screen(sa.table())) > 0.95


def check15(m):  # fix acceptance: the default step gives last-hour swing < 0.2 C and at most 2 heater flips
    r = cosim.metrics(m.run())
    return r["last_hour_swing_C"] < 0.2 and r["heater_flips"] <= 2


def check16(m):  # fix acceptance: every replication distinct, identical on 1 and 2 workers
    one, two = perf.run_parallel(m.tasks_for(6), 1), perf.run_parallel(m.tasks_for(6), 2)
    return len(set(two.tolist())) == 6 and np.array_equal(one, two)


if __name__ == "__main__":  # spawn-safe: check16 starts process pools
    cases = [("12 antithetic pairs", check12, vr, solution("12-variance-reduction", "variance_reduction")),
             ("13 validation data", check13, cal, solution("13-calibration", "calibrate")),
             ("14 screening method", check14, sa, solution("14-global-sensitivity", "sensitivity")),
             ("15 communication step", check15, cosim, solution("15-cosimulation-fmi", "cosim")),
             ("16 worker seeds", check16, perf, solution("16-performance-scale", "perf"))]
    ok = True
    for name, check, fault, fix in cases:
        before, after = check(fault), check(fix)
        ok &= (not before) and after
        print(f"{name:24s} shipped file: {'PASS' if before else 'FAIL'}   solution: {'PASS' if after else 'FAIL'}")
    sys.exit(0 if ok else 1)
