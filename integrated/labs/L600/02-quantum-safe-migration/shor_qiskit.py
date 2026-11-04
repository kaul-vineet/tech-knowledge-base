"""PENDING CI (needs qiskit >= 2.0, not installed in the authoring sandbox): the same order-finding circuit in Qiskit.

Run: pip install qiskit && python shor_qiskit.py
Controlled-U^(2^j) is a UnitaryGate permutation (compiled oracle, as in shor_sim.py); the inverse QFT is QFTGate(t).inverse().
Prints whether Qiskit's counting-register distribution equals shor_sim's numpy one for N = 15 and N = 21.
"""
import math

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFTGate, UnitaryGate
from qiskit.quantum_info import Statevector

import shor_sim


def mult_gate(mult, modulus, n):
    u = np.zeros((2 ** n, 2 ** n))
    for y in range(2 ** n):
        u[(mult * y) % modulus if y < modulus else y, y] = 1
    return UnitaryGate(u, label=f"x{mult} mod {modulus}")


def circuit(modulus, a):
    n = math.ceil(math.log2(modulus))
    t = 2 * n
    qc = QuantumCircuit(t + n)
    qc.x(t)
    qc.h(range(t))
    for j in range(t):
        qc.append(mult_gate(pow(a, 2 ** j, modulus), modulus, n).control(1), [j] + list(range(t, t + n)))
    qc.append(QFTGate(t).inverse(), range(t))
    return qc, t


def counting_probs(modulus, a):
    qc, t = circuit(modulus, a)
    return Statevector(qc).probabilities(list(range(t)))      # qubit 0 = least-significant bit, as in qsim


if __name__ == "__main__":
    for modulus, a in ((15, 7), (21, 2)):
        same = np.allclose(counting_probs(modulus, a), shor_sim.run_order_finding(modulus, a)["probs"], atol=1e-9)
        print(f"N = {modulus}, a = {a}: Qiskit distribution == numpy qsim distribution: {same}")
