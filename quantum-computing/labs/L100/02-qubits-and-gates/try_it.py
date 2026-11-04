"""Try-it checks for lab 02. Run: python try_it.py

The numpy part runs anywhere; the SDK part runs only when qiskit is installed (CI).
"""
import importlib.util

import crosscheck_numpy as cc

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None

# (gate name, qubit), number of qubits
TRIES = {
    "h_x_h": ([("h", 0), ("x", 0), ("h", 0)], 1),   # try 1: put X between the two H gates
    "x_on_q1_of_2": ([("x", 1)], 2),                # try 2: flip qubit 1 instead of qubit 0
}


def numpy_probabilities(name):
    ops, n = TRIES[name]
    return cc.probabilities([({"h": cc.H, "x": cc.X}[g], q) for g, q in ops], n)


def sdk_counts(name, shots=1000, seed=7):
    from qiskit import QuantumCircuit
    from qiskit.primitives import StatevectorSampler
    ops, n = TRIES[name]
    qc = QuantumCircuit(n)
    for g, q in ops:
        getattr(qc, g)(q)
    qc.measure_all()
    result = StatevectorSampler(seed=seed).run([qc], shots=shots).result()
    return result[0].data.meas.get_counts()


if __name__ == "__main__":
    for name in TRIES:
        print(f"{name:13s} numpy {numpy_probabilities(name)}")
        if HAVE_QISKIT:
            print(f"{name:13s} SDK   {sdk_counts(name)}")
