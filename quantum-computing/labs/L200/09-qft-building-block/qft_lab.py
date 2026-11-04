"""Lab 09 - the QFT as a building block: build it for 3 qubits, compare with numpy's DFT, invert it.

Run:  python qft_lab.py
Needs: qiskit (QFTGate, Operator, Statevector) and numpy.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFTGate
from qiskit.quantum_info import Operator, Statevector


def qft_circuit(n, swaps=True):
    """Textbook QFT: per qubit (most significant first) an H, then controlled phases that halve."""
    qc = QuantumCircuit(n, name="qft")
    for j in reversed(range(n)):
        qc.h(j)
        for k in reversed(range(j)):
            qc.cp(np.pi / 2 ** (j - k), k, j)   # controlled phase: angle pi/2, pi/4, ... by distance
    if swaps:
        for i in range(n // 2):
            qc.swap(i, n - 1 - i)               # bit reversal: without it rows come out bit-reversed
    return qc


def inverse_qft_circuit(n):
    return qft_circuit(n).inverse()             # inverse: reversed gate order, negated phase angles


def dft_matrix(n):
    """numpy DFT with the QFT's sign and normalisation: e^{+2 pi i jk/N} / sqrt(N)."""
    return np.fft.ifft(np.eye(2 ** n), axis=0, norm="ortho")


def library_qft(n):
    qc = QuantumCircuit(n)
    qc.append(QFTGate(n), range(n))             # Qiskit's built-in (replaces the deprecated QFT class)
    return qc


def qft_of_basis_state(value, n):
    prep = QuantumCircuit(n)
    prep.x([q for q in range(n) if value >> q & 1])   # |5> = q0 and q2 set (Qiskit bit order)
    return Statevector(prep.compose(qft_circuit(n))).data


if __name__ == "__main__":
    n = 3
    u = Operator(qft_circuit(n)).data
    print("hand-built QFT == numpy DFT:", np.allclose(u, dft_matrix(n)))
    print("hand-built QFT == QFTGate:", Operator(qft_circuit(n)).equiv(Operator(library_qft(n))))
    roundtrip = qft_circuit(n).compose(inverse_qft_circuit(n))
    print("QFT then inverse QFT == identity:", Operator(roundtrip).equiv(Operator(QuantumCircuit(n))))
    amps = qft_of_basis_state(5, n)
    print("QFT|5> magnitudes:", np.round(np.abs(amps), 4).tolist())
    print("QFT|5> phases (turns):", np.round(np.angle(amps) / (2 * np.pi) % 1, 4).tolist())
    print("same as numpy ifft of |5>:", np.allclose(amps, np.fft.ifft(np.eye(2 ** n)[5], norm="ortho")))
    print(qft_circuit(n).draw(output="text"))
