"""Lab 19 Qiskit path: build the same QAOA circuit in Qiskit and check the analytic CX count and depth.
Run: python count_qiskit.py   (CI job sdk-labs; not yet observed)
"""
import json

from qiskit import QuantumCircuit, transpile

import estimate_lab as lab
from counting import count, edge_colouring, mc, qaoa_ops


def build(n, p, seed=1):
    edges = mc.regular_graph(n, 3, seed=seed)
    qc = QuantumCircuit(n)
    for g, qs in qaoa_ops(n, edges, p):
        {"h": qc.h, "cx": qc.cx, "rz": lambda q: qc.rz(0.3, q), "rx": lambda q: qc.rx(0.8, q)}[g](*qs)
    return qc, edges


def check(n=10, p=2):
    qc, edges = build(n, p)
    tq = transpile(qc, basis_gates=["h", "cx", "rz", "rx"], optimization_level=0)
    colours = len(set(edge_colouring(edges).values()))
    return {"qiskit_cx": tq.count_ops().get("cx", 0), "analytic_cx": lab.qaoa_logical(n, p, colours)["cx"],
            "qiskit_depth": tq.depth(), "counted_depth": count(qaoa_ops(n, edges, p), n)["depth"]}


if __name__ == "__main__":
    print(json.dumps(check()))
