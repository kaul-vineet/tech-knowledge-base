"""Density-matrix extension of the numpy simulator (L300 noise labs; no quantum SDK needed).

Same conventions as statevector.py: qubit 0 is the least-significant bit, bitstrings print q(n-1)...q0.
A noisy circuit is a list of steps: unitary ops from statevector.py (h, x, cx, ...) or channel tuples
("depol", p, qubits) / ("damp", gamma, qubit). Channel conventions follow Qiskit Aer's documentation:
  depolarizing_error(p, k):     rho -> (1 - p) rho + p * I / 2**k     on the k qubits it acts on
  amplitude_damping_error(g):   Kraus A0 = [[1, 0], [0, sqrt(1 - g)]], A1 = [[0, sqrt(g)], [0, 0]]
  ReadoutError per qubit:       [[P(0|0), P(1|0)], [P(0|1), P(1|1)]]   (row = true bit, column = recorded bit)
"""
import itertools

import numpy as np

try:
    from . import statevector as sv
except ImportError:          # imported as a top-level module (self-test run from this folder)
    import statevector as sv

PAULI = {"I": np.eye(2, dtype=complex), "X": sv.X, "Y": np.array([[0, -1j], [1j, 0]]), "Z": sv.Z}


def pure(state):
    state = np.asarray(state, dtype=complex)
    return np.outer(state, state.conj())


def zero_state(n):
    rho = np.zeros((2 ** n, 2 ** n), dtype=complex)
    rho[0, 0] = 1
    return rho


def embed(gate, qubits, n):
    """Full 2**n matrix of a k-qubit gate acting on `qubits` (gate's qubit 0 = qubits[0])."""
    k = len(qubits)
    full = np.zeros((2 ** n, 2 ** n), dtype=complex)
    others = [q for q in range(n) if q not in qubits]
    for rest in range(2 ** (n - k)):
        base = 0
        for i, q in enumerate(others):
            base |= ((rest >> i) & 1) << q
        idx = [base | sum(((j >> i) & 1) << q for i, q in enumerate(qubits)) for j in range(2 ** k)]
        full[np.ix_(idx, idx)] = gate
    return full


def apply_unitary(rho, op, n):
    u = sv.unitary(n, [op])
    return u @ rho @ u.conj().T


def apply_kraus(rho, kraus, qubits, n):
    out = np.zeros_like(rho)
    for k in kraus:
        full = embed(k, qubits, n)
        out += full @ rho @ full.conj().T
    return out


def depolarizing_kraus(p, k):
    """Pauli form of (1 - p) rho + p I/2**k: weight 1 - p + p/4**k on I..I, p/4**k on each other Pauli string."""
    ops = []
    for labels in itertools.product("IXYZ", repeat=k):
        weight = 1 - p + p / 4 ** k if set(labels) == {"I"} else p / 4 ** k
        mat = np.array([[1]], dtype=complex)
        for lab in reversed(labels):      # labels[0] acts on the first listed qubit (least significant)
            mat = np.kron(mat, PAULI[lab])
        ops.append(np.sqrt(weight) * mat)
    return ops


def damping_kraus(gamma):
    return [np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex),
            np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=complex)]


def run(n, steps, rho=None):
    rho = zero_state(n) if rho is None else rho
    for step in sv.flatten(steps):
        kind = step[0] if isinstance(step[0], str) else "unitary"
        if kind == "depol":
            _, p, qubits = step
            rho = apply_kraus(rho, depolarizing_kraus(p, len(qubits)), list(qubits), n)
        elif kind == "damp":
            _, gamma, q = step
            rho = apply_kraus(rho, damping_kraus(gamma), [q], n)
        else:
            rho = apply_unitary(rho, step, n)
    return rho


def probabilities(rho):
    return np.clip(np.real(np.diag(rho)), 0, 1)


def readout_matrix(p01, p10, n):
    """Assignment matrix A[recorded, true] for n qubits with the same per-qubit flip rates.
    p01 = P(record 1 | true 0), p10 = P(record 0 | true 1)."""
    single = np.array([[1 - p01, p10], [p01, 1 - p10]])
    a = np.array([[1.0]])
    for _ in range(n):
        a = np.kron(single, a)
    return a


def fidelity(rho, state):
    """<psi|rho|psi> for a pure target state."""
    state = np.asarray(state, dtype=complex)
    return float(np.real(state.conj() @ rho @ state))


def label(i, n):
    return format(i, f"0{n}b")


def sample(probs, shots, rng):
    n = int(np.log2(len(probs)))
    p = np.clip(probs, 0, None)
    hits = rng.multinomial(shots, p / p.sum())
    return {label(i, n): int(c) for i, c in enumerate(hits) if c}
