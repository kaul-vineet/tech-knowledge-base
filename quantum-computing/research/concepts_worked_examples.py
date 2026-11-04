"""Computes every number used in the concept notes (content/concepts/*.md) and the primer.

Run from the domain folder:  python research/concepts_worked_examples.py
Output is recorded in research/concepts_worked_examples.out.txt. numpy only.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "labs", "L100", "05-openqasm-portability"))
import crosscheck_qasm_numpy as qasm  # noqa: E402

H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
X = np.array([[0, 1], [1, 0]], dtype=complex)
I2 = np.eye(2, dtype=complex)
KET0, KET1 = np.array([1, 0], dtype=complex), np.array([0, 1], dtype=complex)


def r(v):
    return np.round(np.real_if_close(v), 4).tolist()


def cnot_0_to_1():
    m = np.zeros((4, 4), dtype=complex)
    for i in range(4):
        m[i ^ 2 if i & 1 else i, i] = 1
    return m


print("== 01 setup: statevector memory (2**n amplitudes x 16 bytes, complex128)")
for n in (2, 20, 30, 40):
    b = (2**n) * 16
    print(f"n={n:2d} amplitudes={2**n} bytes={b} = {b / 2**30:.6g} GiB")

print("\n== 02 gates")
print("X|0> =", r(X @ KET0))
print("H|0> =", r(H @ KET0), "probs", r(np.abs(H @ KET0) ** 2))
print("H|1> =", r(H @ KET1), "probs", r(np.abs(H @ KET1) ** 2))
print("H(H|0>) =", r(H @ H @ KET0))
psi = np.array([(1 + 2j) / 3, -2 / 3])
print("psi=((1+2i)/3, -2/3) probs", r(np.abs(psi) ** 2), "norm^2", round(float(np.sum(np.abs(psi) ** 2)), 12))
two = np.kron(I2, X) @ np.kron(KET0, KET0)  # X on qubit 0 (rightmost factor)
idx = int(np.argmax(np.abs(two)))
print("X on qubit 0 of 2: index", idx, "qiskit label", format(idx, "02b"))

print("\n== 03 shots")
for n in (100, 1000, 10000):
    se = math.sqrt(0.25 / n)
    lo, hi = n * 0.5 - 1.96 * math.sqrt(n * 0.25), n * 0.5 + 1.96 * math.sqrt(n * 0.25)
    print(f"N={n:5d} standard error={se:.4f} ~95% range of count('1')=[{lo:.1f}, {hi:.1f}]")
print("shots for +/-0.01 standard error at p=0.5:", math.ceil(0.25 / 0.01**2))
rng = np.random.default_rng(42)
print("numpy seed 42, 10 coin shots:", "".join(str(b) for b in rng.integers(0, 2, 10)))

print("\n== 04 bell")
s = np.kron(KET0, KET0)
s1 = np.kron(I2, H) @ s
s2 = cnot_0_to_1() @ s1
print("after H on q0:", r(s1))
print("after CNOT(0->1):", r(s2), "probs", {format(i, '02b'): round(float(p), 4) for i, p in enumerate(np.abs(s2) ** 2) if p > 1e-12})
det = lambda v: complex(v[0] * v[3] - v[1] * v[2])  # a00*a11 - a01*a10 (0 iff product state)
print("product test a00*a11-a01*a10: bell", round(det(s2).real, 4), " |q1=0>|q0=+>", round(abs(det(s1)), 4))
p_q0_1 = float(np.abs(s2[1]) ** 2 + np.abs(s2[3]) ** 2)
print("P(q0=1) =", round(p_q0_1, 4), " P(q1=1 | q0=1) =", round(float(np.abs(s2[3]) ** 2) / p_q0_1, 4))

print("\n== 05 openqasm")
with open(os.path.join(HERE, "..", "labs", "L100", "05-openqasm-portability", "reference_bell_qasm3.qasm"), encoding="utf-8") as f:
    ref = f.read()
print("reference_bell_qasm3.qasm bytes", len(ref.encode()), "parsed", qasm.parse(ref), "probs", qasm.probabilities(ref))
swapped = 'OPENQASM 3.0; include "stdgates.inc"; qubit[2] q; h q[0]; cx q[1], q[0];'
print("control/target swapped (cx q[1], q[0]) probs", qasm.probabilities(swapped))
v2 = 'OPENQASM 2.0; include "qelib1.inc"; qreg q[2]; creg c[2]; h q[0]; cx q[0],q[1]; measure q[0] -> c[0]; measure q[1] -> c[1];'
print("same circuit in OpenQASM 2 probs", qasm.probabilities(v2))

print("\n== 06 two frameworks")
for n, q in ((2, 0), (3, 0), (3, 2)):
    i = 1 << q
    little = format(i, f"0{n}b")
    print(f"n={n} X on qubit {q}: qiskit '{little}'  cirq-histogram '{little[::-1]}' (int {int(little[::-1], 2)})")
counts_cirq = {"10": 1000}
print("cirq raw", counts_cirq, "-> qiskit order", {k[::-1]: v for k, v in counts_cirq.items()})

print("\n== check-yourself answers")
print("probs of (0.6, 0.8):", r(np.abs(np.array([0.6, 0.8])) ** 2))
print("shots for 0.005 standard error at p=0.5:", round(0.25 / 0.005**2))
v = np.array([1, 1, 0, 0]) / np.sqrt(2)  # (|00>+|01>)/sqrt2 in index order 00,01,10,11
print("product test (|00>+|01>)/sqrt2:", round(abs(det(v)), 4))
print("crosscheck_qasm_numpy.py lines:", sum(1 for _ in open(qasm.__file__, encoding="utf-8")))
