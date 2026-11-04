"""Independent numpy statevector cross-check for lab 02 (no quantum SDK needed).

Bit order follows Qiskit: qubit 0 is the least significant (rightmost) bit.
"""
import numpy as np

X = np.array([[0, 1], [1, 0]], dtype=complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
I2 = np.eye(2, dtype=complex)


def apply_1q(state, gate, qubit, n):
    """Apply a 1-qubit gate to `qubit` of an n-qubit state (little-endian)."""
    op = np.array([[1]], dtype=complex)
    for q in reversed(range(n)):          # kron from qubit n-1 (left) down to qubit 0 (right)
        op = np.kron(op, gate if q == qubit else I2)
    return op @ state


def probabilities(ops, n):
    """Run a list of (gate, qubit) on |0...0>; return {bitstring: probability > 0}."""
    state = np.zeros(2**n, dtype=complex)
    state[0] = 1
    for gate, qubit in ops:
        state = apply_1q(state, gate, qubit, n)
    probs = np.abs(state) ** 2
    return {format(i, f"0{n}b"): round(float(p), 12) for i, p in enumerate(probs) if p > 1e-12}


EXPECTED = {
    "nothing": probabilities([], 1),
    "x": probabilities([(X, 0)], 1),
    "h": probabilities([(H, 0)], 1),
    "h_h": probabilities([(H, 0), (H, 0)], 1),
    "x_on_q0_of_2": probabilities([(X, 0)], 2),
}

if __name__ == "__main__":
    for name, probs in EXPECTED.items():
        print(f"{name:14s} {probs}")
