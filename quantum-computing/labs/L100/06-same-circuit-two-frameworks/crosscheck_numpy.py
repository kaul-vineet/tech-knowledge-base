"""Independent numpy cross-check for lab 06 (no quantum SDK needed).

One statevector, two ways of writing the same outcome:
  little-endian (Qiskit): string = q1 q0   -> qubit 0 rightmost
  big-endian (Cirq histogram over measure(q0, q1)): string = q0 q1 -> qubit 0 leftmost
"""
import numpy as np

H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
X = np.array([[0, 1], [1, 0]], dtype=complex)
I2 = np.eye(2, dtype=complex)
CX_0_TO_1 = np.zeros((4, 4), dtype=complex)
for i in range(4):  # index bit 0 = qubit 0; flip qubit 1 when qubit 0 is 1
    CX_0_TO_1[i ^ 2 if i & 1 else i, i] = 1


def state(kind):
    s = np.zeros(4, dtype=complex)
    s[0] = 1
    if kind == "bell":
        s = CX_0_TO_1 @ (np.kron(I2, H) @ s)   # kron(qubit1, qubit0)
    else:
        s = np.kron(I2, X) @ s                 # X on qubit 0
    return s


def probabilities(kind, convention="qiskit"):
    probs = np.abs(state(kind)) ** 2
    out = {}
    for i, p in enumerate(probs):
        if p > 1e-12:
            little = format(i, "02b")                       # q1 q0
            key = little if convention == "qiskit" else little[::-1]  # q0 q1 for cirq
            out[key] = round(float(p), 12)
    return out


if __name__ == "__main__":
    for kind in ("bell", "x_on_q0"):
        print(f"{kind:8s} qiskit-order {probabilities(kind, 'qiskit')}  cirq-order {probabilities(kind, 'cirq')}")
