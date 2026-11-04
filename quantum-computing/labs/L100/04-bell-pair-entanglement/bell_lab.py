"""Lab 04 - entanglement with a Bell pair: H + CNOT, then check only '00' and '11' appear.

Run:  python bell_lab.py
"""
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler   # Qiskit's reference sampler; Aer's SamplerV2 is an equivalent
from qiskit.quantum_info import Statevector


def bell_circuit(measure=True):
    qc = QuantumCircuit(2)
    qc.h(0)        # superposition on qubit 0; still a product state
    qc.cx(0, 1)    # entanglement: CNOT(control 0, target 1) -> (|00> + |11>)/sqrt(2)
    if measure:
        qc.measure_all()
    return qc


def ideal_probabilities():
    """Exact probabilities from Qiskit's statevector (Born rule, no shot noise)."""
    probs = Statevector(bell_circuit(measure=False)).probabilities_dict()
    return {k: round(float(v), 12) for k, v in probs.items() if v > 1e-12}


def run_bell(shots=1000, seed=7):
    result = StatevectorSampler(seed=seed).run([bell_circuit()], shots=shots).result()
    return result[0].data.meas.get_counts()


def only_correlated(counts):
    """Correlation check: True when every shot gave matching bits ('00' or '11')."""
    return set(counts) <= {"00", "11"}


if __name__ == "__main__":
    print(bell_circuit().draw())
    print("ideal probabilities:", ideal_probabilities())
    counts = run_bell()
    print("counts:", dict(sorted(counts.items())))
    print("only '00'/'11' seen:", only_correlated(counts))
