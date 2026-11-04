"""Lab 13 SDK path: the same ZNE with Mitiq 1.1.0 on Cirq's DensityMatrixSimulator.

Run:  python mitiq_zne.py     (needs labs/L300/requirements-extras.txt; CI job l300-extras, not yet observed)
API from the Mitiq 1.1.0 user guide: zne.execute_with_zne, zne.scaling.fold_gates_at_random(fidelities=,
random_state=), zne.inference.RichardsonFactory / LinearFactory, rem.generate_inverse_confusion_matrix.
"""
from functools import partial

import cirq
import numpy as np
from mitiq import zne
from mitiq.rem import generate_inverse_confusion_matrix

import mitigation_lab as lab


def to_cirq_p(lam, k):
    """Aer/numpy depolarizing lam (rho -> (1-lam) rho + lam I/2^k) as cirq.depolarize's p (p/(4^k-1) per Pauli)."""
    return lam * (4 ** k - 1) / 4 ** k


def mirror_circuit(n=3):
    q = cirq.LineQubit.range(n)
    ops = [cirq.H(q[0])] + [cirq.CNOT(q[i], q[i + 1]) for i in range(n - 1)]
    ops += [cirq.CNOT(q[i], q[i + 1]) for i in reversed(range(n - 1))] + [cirq.H(q[0])]
    return cirq.Circuit(ops)


def execute(circuit):
    """Executor: P(000) after depolarizing noise on every gate (same model as mitigation_lab.noisy_value)."""
    noisy = cirq.Circuit()
    for op in circuit.all_operations():
        k = len(op.qubits)
        lam = lab.GATE["p2"] if k == 2 else lab.GATE["p1"]
        noisy.append([op, cirq.depolarize(to_cirq_p(lam, k), n_qubits=k).on(*op.qubits)])
    rho = cirq.DensityMatrixSimulator().simulate(noisy).final_density_matrix
    return float(np.real(rho[0, 0]))


def mitiq_zne(factory):
    fold = partial(zne.scaling.fold_gates_at_random, fidelities={"single": 1.0},    # fold only the CX gates
                   random_state=np.random.RandomState(0))
    return zne.execute_with_zne(mirror_circuit(), execute, factory=factory, scale_noise=fold)


if __name__ == "__main__":
    print("raw P(000):", round(execute(mirror_circuit()), 4), "| numpy:", round(float(lab.noisy_value(1)), 4))
    print("Richardson [1,3,5]:", round(mitiq_zne(zne.inference.RichardsonFactory(scale_factors=[1, 3, 5])), 4))
    print("Linear [1,3,5]:   ", round(mitiq_zne(zne.inference.LinearFactory(scale_factors=[1, 3, 5])), 4))
    print("REM inverse (p=0.05, 2 qubits) == numpy inverse:",
          np.allclose(generate_inverse_confusion_matrix(2, 0.05, 0.05), np.linalg.inv(lab.dm.readout_matrix(0.05, 0.05, 2))))
