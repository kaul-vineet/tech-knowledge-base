"""Lab 14 SDK path: the same QAOA circuit in Qiskit, evaluated with StatevectorEstimator, optimized with
scipy's COBYLA (as in IBM's QAOA tutorial). Run: python qaoa_qiskit.py   (CI job sdk-labs; not yet observed)

Cost layer exp(-i gamma C) with C = sum over edges (1 - Z_i Z_j)/2 equals RZZ(-gamma) per edge up to a global
phase, because RZZ(theta) = exp(-i theta/2 Z_i Z_j). QAOAAnsatz(cost_operator, reps=p) builds the same shape.
"""
import json

import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp
from scipy.optimize import minimize

import qaoa_lab as lab

ZZ = SparsePauliOp.from_sparse_list([("ZZ", [i, j], 1.0) for i, j in lab.EDGES], num_qubits=lab.N)


def circuit(params):
    p = len(params) // 2
    qc = QuantumCircuit(lab.N)
    qc.h(range(lab.N))
    for gamma, beta in zip(params[:p], params[p:]):
        for i, j in lab.EDGES:
            qc.rzz(-gamma, i, j)
        qc.rx(2 * beta, range(lab.N))
    return qc


def expected_cut(params, estimator=StatevectorEstimator()):
    zz = float(estimator.run([(circuit(params), ZZ)]).result()[0].data.evs)
    return len(lab.EDGES) / 2 - zz / 2                       # <C> = sum (1 - <ZZ>)/2


def cobyla(x0):
    res = minimize(lambda x: -expected_cut(x), x0, method="COBYLA", options={"maxiter": 300})
    return res.x, -res.fun / lab.CUT.max()


if __name__ == "__main__":
    x = np.array([0.585, 1.029, 0.517, 0.309])
    print("Qiskit <C> at the lab's p=2 optimum:", round(expected_cut(x), 4), "| numpy:", round(-lab.cost(x), 4))
    for name, x0 in (("random seed 0", np.random.default_rng(0).uniform(0, np.pi, 4)),
                     ("warm start", np.array([0.649 / 2, 0.649, 0.354, 0.354 / 2]))):
        xs, r = cobyla(x0)
        print(json.dumps({"optimizer": "COBYLA", "start": name, "ratio": round(r, 4)}))
