"""Lab 08 - small Grover search: amplitude amplification on 2-3 qubits, and how many iterations.

Run:  python grover_lab.py
Needs: qiskit (grover_operator, MCMTGate, Statevector, StatevectorSampler; no Aer needed).
"""
import math

from qiskit import QuantumCircuit
from qiskit.circuit.library import MCMTGate, ZGate, grover_operator
from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import Statevector


def grover_oracle(marked):
    """Phase oracle: multiply each marked basis state by -1 (pattern from the IBM Grover tutorial)."""
    n = len(marked[0])
    qc = QuantumCircuit(n, name="oracle")
    for target in marked:
        zeros = [q for q, bit in enumerate(reversed(target)) if bit == "0"]   # Qiskit bit order
        if zeros:
            qc.x(zeros)                                   # open controls: X before and after
        qc.compose(MCMTGate(ZGate(), n - 1, 1), inplace=True)   # multi-controlled Z flips |1...1>
        if zeros:
            qc.x(zeros)
    return qc


def optimal_iterations(n_marked, n_qubits):
    return math.floor(math.pi / (4 * math.asin(math.sqrt(n_marked / 2 ** n_qubits))))


def grover_circuit(marked, iterations, measure=True):
    n = len(marked[0])
    qc = QuantumCircuit(n)
    qc.h(range(n))                                        # uniform superposition = the start state
    qc.compose(grover_operator(grover_oracle(marked)).power(iterations), inplace=True)  # oracle + diffusion, k times
    if measure:
        qc.measure_all()
    return qc


def success_probability(marked, iterations):
    probs = Statevector(grover_circuit(marked, iterations, measure=False)).probabilities_dict()
    return round(sum(probs.get(m, 0.0) for m in marked), 4)   # amplitude amplification, read exactly


def counts(marked, iterations, shots=1000, seed=5):
    result = StatevectorSampler(seed=seed).run([grover_circuit(marked, iterations)], shots=shots).result()
    return result[0].data.meas.get_counts()


if __name__ == "__main__":
    for marked in (["11"], ["101"]):
        n = len(marked[0])
        k = optimal_iterations(len(marked), n)
        sweep = {i: success_probability(marked, i) for i in range(5)}
        print(f"{n} qubits, marked {marked}: optimal k={k}; P(success) by k: {sweep}")
        c = counts(marked, k)
        top = max(c, key=c.get)
        print(f"  counts at k={k} (1000 shots, seed 5): top {top!r} with {c[top]}")
