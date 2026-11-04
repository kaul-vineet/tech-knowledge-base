"""Lab 06 - the same circuits in Qiskit and Cirq, compared on one bit-order convention.

Run:  python two_frameworks_lab.py
Convention used for comparison: Qiskit's (qubit 0 = RIGHTMOST bit of the string).
"""
import cirq
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler   # Qiskit's reference sampler; Aer's SamplerV2 is an equivalent

CIRCUITS = ("bell", "x_on_q0")   # bell: H(0), CX(0,1)   x_on_q0: X on qubit 0 only


def qiskit_counts(kind, shots=1000, seed=7):
    qc = QuantumCircuit(2)
    if kind == "bell":
        qc.h(0)
        qc.cx(0, 1)
    else:
        qc.x(0)
    qc.measure_all()
    result = StatevectorSampler(seed=seed).run([qc], shots=shots).result()
    return result[0].data.meas.get_counts()          # bit order: little-endian, keys like '01' = q1 q0


def cirq_counts_raw(kind, shots=1000, seed=7):
    q0, q1 = cirq.NamedQubit("q0"), cirq.NamedQubit("q1")
    ops = [cirq.H(q0), cirq.CX(q0, q1)] if kind == "bell" else [cirq.X(q0)]
    circuit = cirq.Circuit(*ops, cirq.measure(q0, q1, key="m"))
    result = cirq.Simulator(seed=seed).run(circuit, repetitions=shots)   # own RNG: same seed != same counts as Qiskit
    hist = result.histogram(key="m")                 # bit order: big-endian ints, q0 is the HIGHEST bit
    return {format(k, "02b"): v for k, v in hist.items()}   # keys like '10' = q0 q1


def to_qiskit_order(counts):
    """Normalise: reverse each bitstring so qubit 0 is rightmost, matching Qiskit."""
    return {bits[::-1]: v for bits, v in counts.items()}


def compare(kind, shots=1000, seed=7):
    return {
        "qiskit": qiskit_counts(kind, shots, seed),
        "cirq_raw": cirq_counts_raw(kind, shots, seed),
        "cirq_in_qiskit_order": to_qiskit_order(cirq_counts_raw(kind, shots, seed)),
    }


if __name__ == "__main__":
    for kind in CIRCUITS:
        print(f"== {kind}")
        for label, counts in compare(kind).items():
            print(f"  {label:22s} {dict(sorted(counts.items()))}")
