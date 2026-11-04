"""Lab 11 - transpiling to a device layout: basis gates, coupling maps, depth and 2-qubit gate counts.

Run:  python transpile_lab.py
Needs: qiskit (GenericBackendV2 = configurable fake backend that ships with qiskit; no account, no network).
"""
from collections import Counter

from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.transpiler import CouplingMap, generate_preset_pass_manager


def ghz_star(n=5):
    qc = QuantumCircuit(n)
    qc.h(0)
    for t in range(1, n):
        qc.cx(0, t)                  # every CX touches qubit 0: fine all-to-all, costly on a line
    qc.measure_all()
    return qc


def backends(n=5):
    return {
        "all-to-all": GenericBackendV2(n, seed=42),     # no coupling_map -> fully connected
        "line": GenericBackendV2(n, coupling_map=CouplingMap.from_line(n), seed=42),
        "heavy-hex": GenericBackendV2(19, coupling_map=CouplingMap.from_heavy_hex(3), seed=42),  # 19 qubits, degree <= 3
    }


def two_qubit_count(qc):
    return sum(1 for inst in qc.data if inst.operation.num_qubits == 2)


def stats(qc):
    return {"depth": qc.depth(), "2q": two_qubit_count(qc),
            "2q_depth": qc.depth(lambda inst: inst.operation.num_qubits == 2)}


def transpile_for(qc, backend, level, seed=7):
    pm = generate_preset_pass_manager(optimization_level=level, backend=backend, seed_transpiler=seed)
    return pm.run(qc)                # layout -> routing (SWAPs) -> basis translation -> optimization


def same_outcomes(tqc, n=5, shots=200):
    """Behaviour check after transpiling: a GHZ state may only give all-0 or all-1."""
    counts = StatevectorSampler(seed=3).run([tqc], shots=shots).result()[0].data.meas.get_counts()
    return set(counts) <= {"0" * n, "1" * n}


if __name__ == "__main__":
    qc = ghz_star()
    print("before:", stats(qc))
    for name, backend in backends().items():
        print(f"{name}: basis {sorted(backend.operation_names)}")
        for level in range(4):
            tqc = transpile_for(qc, backend, level)
            ops = dict(Counter(inst.operation.name for inst in tqc.data))
            print(f"  level {level}: {stats(tqc)} ops {ops} GHZ outcomes only: {same_outcomes(tqc)}")
