"""Lab 18 SDK path: sample the QAOA p=1 circuit with Qiskit's StatevectorSampler and compare the cut-size
distribution with the numpy solver's. Run: python bench_qiskit.py   (CI job sdk-labs; not yet observed)
Shots are the budget unit on hardware too, so the harness's accounting carries over unchanged.
"""
import json

import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

import bench_lab as lab

N, ANGLES, SHOTS = 12, (0.6, 0.4), 4000


def circuit(edges, gamma, beta):
    qc = QuantumCircuit(N)
    qc.h(range(N))
    for i, j in edges:
        qc.rzz(-gamma, i, j)
    qc.rx(2 * beta, range(N))
    qc.measure_all()
    return qc


def compare_distributions():
    edges, opt = lab.instance(N)
    cuts = lab.S.mc.cut_values(N, edges)
    bits = StatevectorSampler(seed=7).run([(circuit(edges, *ANGLES), None, SHOTS)]).result()[0].data.meas.get_bitstrings()
    q = np.bincount([cuts[int(b, 2)] for b in bits], minlength=opt + 1) / SHOTS
    probs = np.abs(lab.S.mc.qaoa_state(N, cuts, list(ANGLES))) ** 2
    exact = np.bincount(cuts, weights=probs, minlength=opt + 1)
    return {"tvd": round(float(0.5 * np.abs(q - exact).sum()), 4), "p_opt_qiskit": round(float(q[opt]), 4),
            "p_opt_numpy": round(float(exact[opt]), 4)}


if __name__ == "__main__":
    print(json.dumps(compare_distributions()))
