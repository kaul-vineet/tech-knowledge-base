"""Lab 05 - portable circuits: export to OpenQASM 3 (and 2), re-import, compare.

Run:  python qasm_lab.py
Needs: qiskit, qiskit-qasm3-import (qasm3.loads depends on it).
"""
from pathlib import Path

from qiskit import QuantumCircuit, qasm2, qasm3
from qiskit.primitives import StatevectorSampler   # Qiskit's reference sampler; Aer's SamplerV2 is an equivalent
from qiskit.quantum_info import Operator


def bell_circuit(measure=True):
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    if measure:
        qc.measure_all()
    return qc


def roundtrip_qasm3(qc):
    text = qasm3.dumps(qc)          # portability: QuantumCircuit -> neutral OpenQASM 3 text
    return text, qasm3.loads(text)  # round-trip: text -> new QuantumCircuit


def roundtrip_qasm2(qc):
    text = qasm2.dumps(qc)          # older, simpler format; still widely accepted
    return text, qasm2.loads(text)


def same_unitary(a, b):
    """True if two measurement-free circuits do the same thing (up to global phase)."""
    return Operator(a).equiv(Operator(b))   # unitary equivalence: compare behaviour, not text


def counts(qc, shots=1000, seed=7):
    result = StatevectorSampler(seed=seed).run([qc], shots=shots).result()
    register = qc.cregs[0].name                  # 'meas' from measure_all(); read it, don't assume
    return getattr(result[0].data, register).get_counts()


if __name__ == "__main__":
    text3, back3 = roundtrip_qasm3(bell_circuit())
    print(text3)
    out = Path(__file__).resolve().parent / "bell.qasm"   # the neutral artifact you can share
    out.write_text(text3, encoding="utf-8")
    text2, _ = roundtrip_qasm2(bell_circuit())
    print(text2)
    _, gates_only = roundtrip_qasm3(bell_circuit(measure=False))
    print("qasm3 round-trip same unitary:", same_unitary(bell_circuit(False), gates_only))
    print("qasm2 round-trip same unitary:", same_unitary(bell_circuit(False), roundtrip_qasm2(bell_circuit(False))[1]))
    print("original counts:  ", counts(bell_circuit()))
    print("re-imported counts:", counts(back3))   # same seed -> expected identical
