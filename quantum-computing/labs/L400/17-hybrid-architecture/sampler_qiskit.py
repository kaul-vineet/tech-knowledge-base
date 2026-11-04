"""Lab 17 SDK path: the same orchestration with Qiskit 2.x primitives. Run: python sampler_qiskit.py  (CI job sdk-labs)

- Transpile cache: one parameterised template, compiled ONCE for a GenericBackendV2 line-8 target with
  generate_preset_pass_manager; angles are bound per evaluation (assign at run time via the PUB's parameter array).
- Job queue: 'sync' sends one PUB per circuit (one sampler.run per circuit); 'batched' sends one PUB with all
  8 parameter sets of an SPSA step (one sampler.run per step). StatevectorSampler is local, so only the
  job and transpile COUNTS transfer to hardware; real queue times would come from the provider.
"""
import json
import time

import numpy as np
from qiskit.circuit import Parameter, QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.transpiler import CouplingMap
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

import orchestrator as lab

GAMMA, BETA = Parameter("gamma"), Parameter("beta")
COUNTERS = {"transpiles": 0, "jobs": 0}


def template():
    qc = QuantumCircuit(lab.TEMPLATE.n)
    qc.h(range(lab.TEMPLATE.n))
    for i, j in lab.TEMPLATE.edges:
        qc.rzz(-GAMMA, i, j)                       # exp(-i gamma C) up to a global phase (lesson 14)
    qc.rx(2 * BETA, range(lab.TEMPLATE.n))
    qc.measure_all()
    return qc


def compile_once():
    backend = GenericBackendV2(num_qubits=8, coupling_map=CouplingMap.from_line(8), seed=11)
    pm = generate_preset_pass_manager(optimization_level=1, backend=backend, seed_transpiler=11)
    COUNTERS["transpiles"] += 1
    return pm.run(template())


def mean_cut(bitstrings):
    cuts = lab.mc.cut_values(lab.TEMPLATE.n, lab.TEMPLATE.edges)
    return float(np.mean([cuts[int(b, 2)] for b in bitstrings]))


def run(mode, iters=30, starts=4, shots=512, seed=2026):
    isa, sampler = compile_once(), StatevectorSampler(seed=seed)
    rng = np.random.default_rng(seed)
    x = rng.uniform(0.1, 1.5, size=(starts, 2))
    t0 = time.perf_counter()
    for k in range(iters):
        ak, ck = 0.2 / (k + 4) ** 0.602, 0.15 / (k + 1) ** 0.101
        delta = rng.choice([-1.0, 1.0], size=x.shape)
        values = np.array([x[i] + s * ck * delta[i] for i in range(starts) for s in (+1, -1)])
        if mode == "sync":
            results = [sampler.run([(isa, v, shots)]).result()[0] for v in values]
            COUNTERS["jobs"] += len(values)
            means = [mean_cut(r.data.meas.get_bitstrings()) for r in results]
        else:
            res = sampler.run([(isa, values, shots)]).result()[0]       # one job: 8 parameter sets
            COUNTERS["jobs"] += 1
            means = [mean_cut(res.data.meas[i].get_bitstrings()) for i in range(len(values))]
        for i in range(starts):
            x[i] += ak * (means[2 * i] - means[2 * i + 1]) / (2 * ck) * delta[i]
    cuts = lab.mc.cut_values(lab.TEMPLATE.n, lab.TEMPLATE.edges)
    best = max(lab.mc.expectation(lab.TEMPLATE.n, cuts, xi) for xi in x) / cuts.max()
    return {"mode": mode, "best_ratio": round(best, 4), "local_s": round(time.perf_counter() - t0, 2), **COUNTERS}


if __name__ == "__main__":
    for mode in ("sync", "batched"):
        COUNTERS.update(transpiles=0, jobs=0)
        print(json.dumps(run(mode)))
