"""Lab 15 SDK path: the same VQE with Qiskit primitives and scipy's COBYLA / the lab's SPSA.

Run:  python vqe_qiskit.py      (CI job sdk-labs; not yet observed). Writes logs/vqe_qiskit_<opt>.jsonl.
Exact energies: StatevectorEstimator with a SparsePauliOp. Shot-noise energies: StatevectorSampler on two
measurement circuits (Z basis, and X basis via H on both qubits) - the same grouping as vqe_lab.energy.
"""
import json

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.primitives import StatevectorEstimator, StatevectorSampler
from qiskit.quantum_info import SparsePauliOp
from scipy.optimize import minimize

import solution_spsa
import vqe_lab as lab

HAM = SparsePauliOp.from_list(list(lab.TERMS.items()))
THETA = ParameterVector("t", 4)


def ansatz(measure_basis=None):
    qc = QuantumCircuit(2)
    qc.ry(THETA[0], 0)
    qc.ry(THETA[1], 1)
    qc.cx(0, 1)
    qc.ry(THETA[2], 0)
    qc.ry(THETA[3], 1)
    if measure_basis == "X":
        qc.h([0, 1])
    if measure_basis:
        qc.measure_all()
    return qc


def exact_energy(t):
    return float(StatevectorEstimator().run([(ansatz(), HAM, [list(t)])]).result()[0].data.evs[0])


def sampled_energy(t, shots=1000, sampler=None):
    sampler = sampler or StatevectorSampler(seed=7)
    res = sampler.run([(ansatz("Z"), [list(t)]), (ansatz("X"), [list(t)])], shots=shots).result()
    fz, fx = (np.array([r.data.meas.get_counts(0).get(format(i, "02b"), 0) for i in range(4)]) / shots for r in res)
    z0, z1 = lab.SIGN[:, 0], lab.SIGN[:, 1]
    c = lab.TERMS
    return float(c["II"] + c["ZI"] * fz @ z1 + c["IZ"] * fz @ z0 + c["ZZ"] * fz @ (z0 * z1) + c["XX"] * fx @ (z0 * z1))


def run(optimizer="cobyla", shots=1000, seed=0):
    sampler, rows = StatevectorSampler(seed=seed), []

    def f(t):
        e = sampled_energy(t, shots, sampler)
        rows.append({"optimizer": optimizer, "shots": shots, "eval": len(rows), "energy_est": round(e, 5)})
        return e

    x0 = np.full(4, 0.1)
    if optimizer == "cobyla":
        x = minimize(f, x0, method="COBYLA", options={"maxiter": 200, "rhobeg": 0.5}).x
    else:
        x = solution_spsa.spsa(f, x0, np.random.default_rng(seed), **solution_spsa.SETTINGS)
    path = lab.HERE / "logs" / f"vqe_qiskit_{optimizer}.jsonl"
    path.parent.mkdir(exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return x, round(exact_energy(x) - lab.E0, 4)


if __name__ == "__main__":
    print("exact energy at t = 0.1:", round(exact_energy([0.1] * 4), 5), "| numpy:", round(lab.energy(np.full(4, 0.1)), 5))
    for opt in ("cobyla", "spsa"):
        x, err = run(opt, shots=4000)
        print(json.dumps({"optimizer": opt, "shots": 4000, "error": err}))
