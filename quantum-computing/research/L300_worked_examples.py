"""Computes every number used in the L300 concept notes (content/concepts/L300/*.md).

Run from the domain folder:  python research/L300_worked_examples.py
Output is recorded in research/L300_worked_examples.out.txt. numpy only (imports the L300 numpy labs).
"""
import importlib
import sys
from pathlib import Path

import numpy as np

LABS = Path(__file__).resolve().parent.parent / "labs" / "L300"


def load(lab, *modules):
    sys.path.insert(0, str(LABS / lab))
    for m in list(sys.modules):
        if m in ("try_it", "test_build_task") or m.startswith("solution_"):
            del sys.modules[m]
    out = [importlib.import_module(m) for m in modules]
    sys.path.pop(0)
    return out


nl, = load("12-noise-models", "noise_lab")
print("[12] noisy Bell counts:", nl.counts(2, nl.NOISE))
print("[12] Bell model:", nl.metrics(2, nl.NOISE), "| GHZ-4 p2=0.1:", nl.metrics(4, {**nl.NOISE, "p2": 0.1}))
print("[12] p2=0.05 success Bell / GHZ-4:", nl.metrics(2, {**nl.NOISE, "p2": 0.05})["success"], nl.metrics(4, {**nl.NOISE, "p2": 0.05})["success"])
print("[12] naive check on noisy counts:", nl.bell_check(nl.counts(2, nl.NOISE)))

ml, ms, mt = load("13-error-mitigation", "mitigation_lab", "solution_constrained", "try_it")
v = [float(ml.noisy_value(s)) for s in (1, 3, 5)]
print("[13] P000 at scales 1,3,5:", np.round(v, 4).tolist(), "linear", round(float(ml.linear([1, 3, 5], v)), 4),
      "richardson", round(float(ml.richardson([1, 3, 5], v)), 4))
print("[13] mean TVD cal100/run200: plain", ms.mean_tvd(ml.mitigate, 100, 200), "constrained", ms.mean_tvd(ms.mitigate, 100, 200))
print("[13] tryIt:", mt.zne_shot_noise(), mt.clip_vs_constrained())

ql, qs, qt = load("14-qaoa-maxcut", "qaoa_lab", "solution_restarts", "try_it")
g, b, _ = ql.landscape()
print("[14] brute force:", ql.brute_force(), "| grid p1:", round(g, 4), round(b, 4), ql.ratio([g, b]), "descent", ql.ratio(ql.optimize([g, b])))
print("[14] p2 seed 0:", ql.ratio(ql.solve(2, 0)), "| restarts p2:", ql.ratio(qs.solve(2)), "| tryIt:", qt.random_starts(), qt.sample_the_answer())

vl, vs, vt = load("15-hybrid-vqe-loop", "vqe_lab", "solution_spsa", "try_it")
p = vl.HERE / "logs" / "vqe_gd_1000.jsonl"
print("[15] E0", round(vl.E0, 4), "| gd exact", vl.vqe(None)[1], "| gd 1000", vl.vqe(1000, log_path=p)[1], vl.summarize(p))
print("[15] spsa 1000:", vs.vqe(1000)[1], "| tryIt:", vt.more_shots_same_optimizer(), vt.below_the_ground_energy())

cl, cs, ct = load("16-quantum-classifier", "classifier_lab", "solution_init", "try_it")
d = cl.make_dataset()
print("[16] quantum", cl.train_quantum(*d)[:2], "logistic", cl.logistic_baseline(*d))
print("[16] scan random init:", [cl.gradient_scan(n, L)["median_abs_grad"] for n, L in ((2, 2), (6, 12), (10, 20))],
      "floor", cl.SHOT_FLOOR, "| near-identity 10x20:", cl.gradient_scan(10, 20, init=cs.init_weights)["median_abs_grad"])
print("[16] tryIt:", ct.global_readout_with_good_init(), ct.shot_noise_at_prediction())
