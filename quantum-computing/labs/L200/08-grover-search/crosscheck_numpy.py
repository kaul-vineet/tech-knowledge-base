"""Independent numpy check for lab 08 (no quantum SDK). Run: python crosscheck_numpy.py

Grover as plain linear algebra: oracle = diagonal of +-1, diffusion = 2|s><s| - I,
compared with the closed form P(k) = sin^2((2k+1) * theta), theta = asin(sqrt(M/N)).
"""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from qsim import statevector as sv  # noqa: E402


def grover_state(marked, k):
    n = len(marked[0])
    dim = 2 ** n
    s = np.full(dim, 1 / math.sqrt(dim))
    oracle = np.ones(dim)
    for m in marked:
        oracle[int(m, 2)] = -1                     # int('101', 2) = 5: Qiskit strings are big-endian text
    diffusion = 2 * np.outer(s, s) - np.eye(dim)
    state = s.copy()
    for _ in range(k):
        state = diffusion @ (oracle * state)
    return state


def oracle_gates_diagonal(marked):
    """Same gate recipe as grover_oracle (X on '0' bits, multi-controlled Z, X again), built in numpy."""
    n = len(marked[0])
    ops = []
    for target in marked:
        zeros = [sv.x(q) for q, bit in enumerate(reversed(target)) if bit == "0"]
        ops += zeros + [sv.mcz(range(n - 1), n - 1)] + zeros
    return np.real_if_close(np.diag(sv.unitary(n, ops))).astype(int).tolist()


def success(marked, k):
    state = grover_state(marked, k)
    return round(float(sum(abs(state[int(m, 2)]) ** 2 for m in marked)), 4)


def closed_form(n_marked, n_qubits, k):
    theta = math.asin(math.sqrt(n_marked / 2 ** n_qubits))
    return round(math.sin((2 * k + 1) * theta) ** 2, 4)


def optimal_iterations(n_marked, n_qubits):
    return math.floor(math.pi / (4 * math.asin(math.sqrt(n_marked / 2 ** n_qubits))))


if __name__ == "__main__":
    for marked in (["11"], ["101"], ["011", "100"]):
        n, m = len(marked[0]), len(marked)
        sweep = {k: success(marked, k) for k in range(5)}
        same = all(abs(sweep[k] - closed_form(m, n, k)) <= 1e-4 for k in sweep)   # 4-dp rounding
        print(f"marked {marked}: oracle diagonal {oracle_gates_diagonal(marked)}")
        print(f"  optimal k={optimal_iterations(m, n)}  P by k {sweep}  matches sin^2 formula: {same}")
