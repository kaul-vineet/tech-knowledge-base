"""Independent numpy cross-check for lab 01 (no quantum SDK needed).

A qubit state is a length-2 complex vector; a gate is a 2x2 matrix.
Measurement probabilities are |amplitude|^2.
"""
import numpy as np

KET0 = np.array([1, 0], dtype=complex)        # |0>
X = np.array([[0, 1], [1, 0]], dtype=complex)  # NOT gate


def x_then_measure_probabilities():
    state = X @ KET0                     # apply X to |0>
    probs = np.abs(state) ** 2           # Born rule
    return {"0": float(probs[0]), "1": float(probs[1])}


if __name__ == "__main__":
    probs = x_then_measure_probabilities()
    print("numpy", np.__version__)
    print("P(X|0>):", probs)
    print("expected counts for 100 shots:", {k: round(v * 100) for k, v in probs.items() if v > 0})
