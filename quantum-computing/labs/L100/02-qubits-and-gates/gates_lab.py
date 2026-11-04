"""Lab 02 - build small circuits with X, H and measure, run them, read the counts.

Run:  python gates_lab.py
"""
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler   # Qiskit's reference sampler; Aer's SamplerV2 is an equivalent


def build_circuits():
    """Return {name: circuit}. Every circuit ends with measure_all() -> register 'meas'."""
    circuits = {}

    qc = QuantumCircuit(1)          # qubits start in |0>
    qc.measure_all()
    circuits["nothing"] = qc        # always '0'

    qc = QuantumCircuit(1)
    qc.x(0)                         # X = NOT: |0> -> |1>
    qc.measure_all()
    circuits["x"] = qc              # always '1'

    qc = QuantumCircuit(1)
    qc.h(0)                         # superposition: H gives amplitudes (0.7071, 0.7071)
    qc.measure_all()                # Born rule: P = |amplitude|^2 -> 50% '0', 50% '1'
    circuits["h"] = qc

    qc = QuantumCircuit(1)
    qc.h(0)
    qc.h(0)                         # interference: H twice undoes itself -> always '0'
    qc.measure_all()
    circuits["h_h"] = qc

    qc = QuantumCircuit(2)
    qc.x(0)                         # flip qubit 0 only
    qc.measure_all()
    circuits["x_on_q0_of_2"] = qc   # bit order: prints '01', qubit 0 is the RIGHTMOST bit

    return circuits


def run_all(shots=1000, seed=7):
    """Run every circuit on the local reference sampler; return {name: counts}."""
    circuits = build_circuits()
    names = list(circuits)
    sampler = StatevectorSampler(seed=seed)   # fixed seed -> same counts every run
    result = sampler.run([circuits[n] for n in names], shots=shots).result()
    return {name: result[i].data.meas.get_counts() for i, name in enumerate(names)}


if __name__ == "__main__":
    print(build_circuits()["h"].draw())   # text drawing of the H circuit
    for name, counts in run_all().items():
        print(f"{name:14s} {dict(sorted(counts.items()))}")
