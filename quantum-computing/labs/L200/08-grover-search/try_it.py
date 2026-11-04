"""Try-it checks for lab 08. Run: python try_it.py

The numpy part runs anywhere; the SDK part runs only when qiskit is installed (CI).
"""
import importlib.util

import crosscheck_numpy as cc

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None
TRIES = {
    "overshoot": (["101"], 3),          # Try 1: one iteration more than the optimum (k=2)
    "two_marked_k2": (["101", "110"], 2),  # Try 2: mark a second state but keep k=2
}


def numpy_success(name):
    marked, k = TRIES[name]
    return {"k": k, "P": cc.success(marked, k), "optimal_k": cc.optimal_iterations(len(marked), 3),
            "P_at_optimal": cc.success(marked, cc.optimal_iterations(len(marked), 3))}


def sdk_success(name):
    import grover_lab
    marked, k = TRIES[name]
    return grover_lab.success_probability(marked, k)


if __name__ == "__main__":
    for name in TRIES:
        print(f"{name:14s} numpy {numpy_success(name)}")
        if HAVE_QISKIT:
            print(f"{name:14s} qiskit P={sdk_success(name)}")
