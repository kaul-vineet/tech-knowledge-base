"""Capstone - an end-to-end quantum optimisation service (simulator only).

Run:  python pipeline.py          (numpy; one request through every stage; prints the report as JSON)
      python run_capstone.py      (API server + requests + agent explanation + scorecard)
Stages, each reused from an earlier lab:
  validate -> feasibility gate (19) -> compile for the fake device (20) -> orchestrated noisy QAOA with batched jobs,
  transpile cache and retries (17 + 12's noise idea) -> readout mitigation (13) -> fair benchmark against greedy and
  annealing at the same budget and seeds (18) -> code decides the winner -> report.
"""
import json

import numpy as np

import noisy_backend as nb
from reuse import l13_mitigate, l17_backend, l17_cache, l17_orch, l18_bench, l18_fair, l18_solvers, l19_distance, l19_estimate

DEFAULT = {"n": 8, "graph_seed": 3, "budget": 2000, "seeds": 5, "faults": [3, 4], "drift": True}
LIMITS = {"n": (4, 16), "budget": (200, 20000), "seeds": (3, 20)}
DEPTH_BUDGET = 60
DEVICE_QUBITS = 8


def validate(req):
    req = {**DEFAULT, **req}
    for key, (lo, hi) in LIMITS.items():
        if not isinstance(req[key], int) or not lo <= req[key] <= hi:
            raise ValueError(f"{key} must be an integer in [{lo}, {hi}]")
    return req


def feasibility(n):
    row = l19_estimate.physical(l19_estimate.qaoa_logical(n, 1), choose=l19_distance.choose_distance)
    cls = l19_estimate.classify(row)
    quantum = n <= DEVICE_QUBITS and cls in ("simulate", "nisq-candidate")
    return {"class": cls, "device_qubits": DEVICE_QUBITS, "quantum_path": quantum,
            "reason": "fits the device and the simulator" if quantum else f"needs {n} qubits > {DEVICE_QUBITS} on the device"}


def qaoa_solver(dev, faults, stats):
    """Lesson-18-compatible solver: half the budget trains angles (SPSA via the orchestrator), half samples answers."""
    def solve(n, edges, budget, seed):
        template = l17_backend.Template("qaoa-maxcut", n, tuple(edges), 1)
        clock = l17_backend.FakeClock()
        backend = nb.NoisyBackend(clock, dev, depth_budget=DEPTH_BUDGET, fail_jobs=faults)
        orch = l17_orch.Orchestrator(backend, clock, key=l17_cache.cache_key)
        w = {"starts": 2, "iters": 10, "shots": budget // 2 // 40, "seed": seed, "classical_s": 0.05}
        x = l17_orch.spsa_multistart(orch, w, template=template)
        used = 40 * w["shots"]
        compiled = next(iter(orch.cache.values()))
        cuts, per_start = compiled["cuts"], (budget - used) // len(x)
        samples = np.concatenate([backend.sample(compiled, l17_backend.Circuit(template, tuple(xi), seed + 7 * i), per_start)
                                  for i, xi in enumerate(x)])
        found = cuts[samples]
        stats.append({"seed": seed, "x": [round(float(v), 4) for v in x[0]], "jobs": backend.jobs, "retries": orch.retries,
                      "transpiles": backend.transpiles, "wall_s": round(clock.now, 2), "compile": compiled["metrics"],
                      "layout": compiled["layout"], "fidelity": round(compiled["fidelity"], 4), "compiled": compiled})
        return {"cut": int(found.max()), "used": used + per_start * len(x),
                "first_best": used + int(np.argmax(found == found.max())) + 1}
    return solve


def mitigation(compiled, params, shots=4000, cal_shots=2000, seed=11):
    """Readout mitigation (lesson 13, constrained) of <C>: tensored per-qubit calibration, then compare."""
    rng = np.random.default_rng(seed)
    n, cuts, ro = compiled["template"].n, compiled["cuts"], compiled["ro"]
    m = np.array([[1.0]])
    for r in ro:                                                   # calibrate each measured qubit: prep 0, prep 1
        p01, p10 = rng.binomial(cal_shots, r) / cal_shots, rng.binomial(cal_shots, r) / cal_shots
        m = np.kron(np.array([[1 - p01, p10], [p01, 1 - p10]]), m)
    noisy = nb.probabilities(compiled, params)
    raw = np.bincount(rng.choice(2 ** n, size=shots, p=noisy / noisy.sum()), minlength=2 ** n) / shots
    fixed = l13_mitigate.mitigate(raw, m)
    f = compiled["fidelity"]
    target = cuts @ (f * np.abs(nb.mc.qaoa_state(n, cuts, params)) ** 2 + (1 - f) / 2 ** n)   # gate noise only
    return {"ideal": round(float(cuts @ (np.abs(nb.mc.qaoa_state(n, cuts, params)) ** 2)), 4),
            "gate_noise_only": round(float(target), 4), "raw": round(float(cuts @ raw), 4),
            "mitigated": round(float(cuts @ fixed), 4), "calibration_shots": 2 * n * cal_shots}


def solve(req):
    req = validate(req)
    n, edges = req["n"], l18_solvers.mc.regular_graph(req["n"], 3, seed=req["graph_seed"])
    report = {"request": req, "optimum": l18_solvers.exact(n, edges)["cut"], "feasibility": feasibility(n)}
    solvers = {k: l18_solvers.BUDGETED[k] for k in ("greedy", "annealing")}
    stats = []
    if report["feasibility"]["quantum_path"]:
        dev = nb.l20_device.make_device(drift=nb.l20_device.DRIFT if req["drift"] else None)
        solvers["qaoa-noisy"] = qaoa_solver(dev, tuple(req["faults"]), stats)
    rows, winner = l18_fair.compare(n, solvers, budget=req["budget"], seeds=tuple(range(req["seeds"])), edges=edges)
    report.update(benchmark=rows, winner=winner, decided_by="code: median ratio > success > samples to best; ties -> classical")
    if stats:
        s = stats[0]
        report["execution"] = {k: s[k] for k in ("jobs", "retries", "transpiles", "wall_s")} | {"mode": l17_orch.DEFAULT_MODE}
        report["compile"] = {"layout": s["layout"], **s["compile"], "within_depth_budget": s["compile"]["depth"] <= DEPTH_BUDGET,
                             "gate_fidelity": s["fidelity"]}
        report["mitigation"] = mitigation(s["compiled"], s["x"])
    return report


if __name__ == "__main__":
    print(json.dumps(solve({}), indent=1))
