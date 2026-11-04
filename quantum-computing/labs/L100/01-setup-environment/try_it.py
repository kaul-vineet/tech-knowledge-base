"""Try-it checks for lab 01. Run: python try_it.py

The numpy part runs anywhere; the SDK part runs only when qiskit is installed (CI).
"""
import importlib.util

import numpy as np

import crosscheck_numpy as cc

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None


def x_twice_numpy():
    """Try 1: apply X twice to |0> (gate is reversible: X.X = I)."""
    probs = np.abs(cc.X @ cc.X @ cc.KET0) ** 2
    return {k: round(float(p) * 100) for k, p in zip("01", probs) if p > 0}


def x_twice_sdk(shots=100):
    from qiskit import QuantumCircuit
    from qiskit.primitives import StatevectorSampler
    qc = QuantumCircuit(1)
    qc.x(0)
    qc.x(0)
    qc.measure_all()
    return StatevectorSampler(seed=7).run([qc], shots=shots).result()[0].data.meas.get_counts()


def statevector_bytes(n):
    """Try 2: bytes a full statevector of n qubits needs (complex128 = 16 bytes per amplitude)."""
    return np.zeros(2**n, dtype=complex).nbytes if n <= 20 else 2**n * np.dtype(complex).itemsize


if __name__ == "__main__":
    print("try 1  X twice, numpy counts for 100 shots:", x_twice_numpy())
    if HAVE_QISKIT:
        print("try 1  X twice, StatevectorSampler counts:", x_twice_sdk())
    for n in (1, 3, 30):
        b = statevector_bytes(n)
        print(f"try 2  n={n:<2d} statevector bytes={b} ({b / 2**30:g} GiB)")
