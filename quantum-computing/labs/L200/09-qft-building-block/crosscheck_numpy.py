"""Independent numpy check for lab 09 (no quantum SDK). Run: python crosscheck_numpy.py

Builds the QFT from H, controlled-phase and SWAP gates on the shared numpy simulator (Qiskit bit
order) and compares the matrix with numpy's DFT, np.fft.ifft(..., norm="ortho") (sign e^{+2 pi i jk/N}).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from qsim import statevector as sv  # noqa: E402


def qft_ops(n, swaps=True, sign=1):
    ops = []
    for j in reversed(range(n)):
        ops.append(sv.h(j))
        for k in reversed(range(j)):
            ops.append(sv.cp(sign * np.pi / 2 ** (j - k), k, j))
    if swaps:
        ops += [sv.swap(i, n - 1 - i) for i in range(n // 2)]
    return ops


def dft_matrix(n):
    return np.fft.ifft(np.eye(2 ** n), axis=0, norm="ortho")


def inverse_qft_ops(n):
    """Inverse = same gates in reverse order with negated angles (H and SWAP are their own inverse)."""
    inv = []
    for gate, target, controls in reversed(list(sv.flatten(qft_ops(n)))):
        inv.append((gate.conj().T, target, controls))
    return inv


def max_error(u, v):
    return float(np.max(np.abs(u - v)))


def bit_reverse_rows(m, n):
    order = [int(format(i, f"0{n}b")[::-1], 2) for i in range(2 ** n)]
    return m[order]


if __name__ == "__main__":
    n = 3
    u = sv.unitary(n, qft_ops(n))
    print("QFT gates vs numpy DFT, max |difference|:", round(max_error(u, dft_matrix(n)), 12))
    print("inverse QFT gates vs numpy DFT^-1 (np.fft.fft ortho):",
          round(max_error(sv.unitary(n, inverse_qft_ops(n)), np.fft.fft(np.eye(2 ** n), axis=0, norm="ortho")), 12))
    state = sv.run(n, [sv.x(0), sv.x(2)] + qft_ops(n))           # QFT of basis state |5>
    print("QFT|5> magnitudes:", np.round(np.abs(state), 4).tolist())
    print("QFT|5> phases (turns):", np.round(np.angle(state) / (2 * np.pi) % 1, 4).tolist())
