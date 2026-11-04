"""Try-it checks for lab 07. Run: python try_it.py

The numpy part runs anywhere; the SDK part runs only when qiskit is installed (CI).
"""
import importlib.util

import crosscheck_numpy as cc
from qsim import statevector as sv

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None


def no_kickback_numpy(secret="1011"):
    """Try 1: delete qc.x(n), so the ancilla starts in |+> instead of |->."""
    return cc.bv_probabilities(secret, kickback=False)


def unreversed_oracle_numpy(secret="1011"):
    """Try 2: loop over `secret` instead of `reversed(secret)` in bv_oracle."""
    n = len(secret)
    return cc.input_probabilities(sv.run(n + 1, cc.bv_ops(cc.oracle_ops(secret, reverse=False), n)), n)


def sdk_counts(kind, secret="1011"):
    from qiskit import QuantumCircuit

    import bv_lab
    n = len(secret)
    if kind == "no_kickback":
        qc = QuantumCircuit(n + 1, n)
        qc.h(range(n + 1))
        qc.compose(bv_lab.bv_oracle(secret), inplace=True)
        qc.h(range(n))
        qc.measure(range(n), range(n))
    else:
        oracle = QuantumCircuit(n + 1)
        for q, bit in enumerate(secret):
            if bit == "1":
                oracle.cx(q, n)
        qc = bv_lab.bv_circuit(oracle)
    return bv_lab.run(qc)


if __name__ == "__main__":
    for name, fn in (("no_kickback", no_kickback_numpy), ("unreversed", unreversed_oracle_numpy)):
        print(f"{name:12s} numpy {fn()}")
        if HAVE_QISKIT:
            print(f"{name:12s} qiskit {sdk_counts(name)}")
