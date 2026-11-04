"""Try-it checks for lab 04. Run: python try_it.py

The numpy part runs anywhere; the SDK part runs only when qiskit is installed (CI).
"""
import importlib.util

import numpy as np

import crosscheck_numpy as cc

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None
X = np.array([[0, 1], [1, 0]], dtype=complex)


def _probs(state):
    return {format(i, "02b"): round(float(p), 12) for i, p in enumerate(np.abs(state) ** 2) if p > 1e-12}


def _product_test(s):
    """a00*a11 - a01*a10: 0 for a product state, non-zero when entangled."""
    return round(float(abs(s[0] * s[3] - s[1] * s[2])), 4)


def swapped_cx_numpy():
    """Try 1: qc.cx(1, 0) instead of qc.cx(0, 1)."""
    s = cc.cnot(1, 0, 2) @ (np.kron(cc.I2, cc.H) @ np.array([1, 0, 0, 0], dtype=complex))
    return _probs(s), _product_test(s)


def x_after_cx_numpy():
    """Try 2: add qc.x(0) after qc.cx(0, 1)."""
    s = np.kron(cc.I2, X) @ cc.bell_state()
    return _probs(s), _product_test(s)


def sdk_probabilities(kind):
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector
    qc = QuantumCircuit(2)
    qc.h(0)
    if kind == "swapped_cx":
        qc.cx(1, 0)
    else:
        qc.cx(0, 1)
        qc.x(0)
    return {k: round(float(v), 12) for k, v in Statevector(qc).probabilities_dict().items() if v > 1e-12}


if __name__ == "__main__":
    for name, fn in (("swapped_cx", swapped_cx_numpy), ("x_after_cx", x_after_cx_numpy)):
        probs, det = fn()
        print(f"{name:11s} numpy {probs}  product test {det}")
        if HAVE_QISKIT:
            print(f"{name:11s} qiskit {sdk_probabilities(name)}")
