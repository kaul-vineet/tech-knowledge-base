"""Independent numpy cross-check for lab 04: Bell pair statevector (no quantum SDK needed).

Little-endian like Qiskit: basis index i, bit k of i = qubit k; label = format(i, '02b') -> 'q1q0'.
"""
import numpy as np

H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
I2 = np.eye(2, dtype=complex)


def cnot(control, target, n):
    """Permutation matrix: flip `target` bit when `control` bit is 1."""
    m = np.zeros((2**n, 2**n), dtype=complex)
    for i in range(2**n):
        j = i ^ (1 << target) if (i >> control) & 1 else i
        m[j, i] = 1
    return m


def bell_state():
    state = np.zeros(4, dtype=complex)
    state[0] = 1                          # |00>
    state = np.kron(I2, H) @ state        # H on qubit 0 (rightmost factor = qubit 0)
    return cnot(0, 1, 2) @ state          # CNOT control 0 -> target 1


def bell_probabilities():
    probs = np.abs(bell_state()) ** 2
    return {format(i, "02b"): round(float(p), 12) for i, p in enumerate(probs) if p > 1e-12}


if __name__ == "__main__":
    print("amplitudes:", np.round(bell_state(), 4))
    print("probabilities:", bell_probabilities())
