"""Independent checks for lab 20 compilations (numpy density matrices on the used physical qubits only).

equivalent(): noiseless compiled circuit, mapped back through the final layout, reproduces the logical
distribution (TVD < 1e-9) - routing and cancellation must not change the answer.
noisy_fidelity(): depolarizing noise per gate at the device's error rates + readout flips; Hellinger fidelity
with the ideal distribution - the quantity ESP is meant to predict.
"""
import sys
from pathlib import Path

import numpy as np

import compile_lab as lab
import device as D

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from qsim import statevector as sv  # noqa: E402

MAT = {"h": lambda a: sv.H, "rx": sv.rx, "rz": sv.rz}
CX = np.eye(4)[[0, 3, 2, 1]]          # control = first listed qubit (least significant in the 2-qubit index)


def apply(rho, u, qs, m):
    """rho -> U rho U^dagger for a k-qubit U on local qubits qs (tensor contraction, no 2**m x 2**m U)."""
    k = len(qs)
    t = rho.reshape([2] * (2 * m))
    ut = u.reshape([2] * (2 * k))
    rows = [m - 1 - q for q in reversed(qs)]                        # tensor axes, most significant first
    t = np.moveaxis(np.tensordot(ut, t, axes=(list(range(k, 2 * k)), rows)), list(range(k)), rows)
    cols = [2 * m - 1 - q for q in reversed(qs)]
    t = np.moveaxis(np.tensordot(ut.conj(), t, axes=(list(range(k, 2 * k)), cols)), list(range(k)), cols)
    return t.reshape(2 ** m, 2 ** m)


def depolarize(rho, lam, qs, m):
    """(1 - lam) rho + lam * Tr_qs(rho) (x) I/2^k, via the Pauli twirl (average over all Paulis on qs)."""
    paulis = [np.eye(2), sv.X, np.array([[0, -1j], [1j, 0]]), sv.Z]
    out = np.zeros_like(rho)
    for combo in np.ndindex(*([4] * len(qs))):
        p = np.array([[1.0]])
        for c in reversed(combo):
            p = np.kron(p, paulis[c])
        out += apply(rho, p, qs, m)
    return (1 - lam) * rho + lam * out / 4 ** len(qs)


def distribution(ops, final, dev=None):
    used = sorted({q for _, qs, _ in ops for q in qs} | set(final))
    loc, m = {p: i for i, p in enumerate(used)}, len(used)
    rho = np.zeros((2 ** m, 2 ** m), dtype=complex)
    rho[0, 0] = 1
    for name, qs, arg in ops:
        local = [loc[q] for q in qs]
        rho = apply(rho, CX if name == "cx" else MAT[name](arg), local, m)
        if dev:
            e = D.cx_error(dev, *qs) if name == "cx" else dev["sq"][qs[0]] if name in ("h", "rx") else 0.0
            rho = depolarize(rho, e * 4 ** len(qs) / (4 ** len(qs) - 1), local, m)   # error prob = e
    probs = np.clip(np.real(np.diag(rho)), 0, 1)
    out = np.zeros(2 ** lab.NQ)
    for idx, pr in enumerate(probs):
        out[sum(((idx >> loc[p]) & 1) << lq for lq, p in enumerate(final))] += pr
    if dev:                                                          # readout flips on the measured qubits
        for lq, p in enumerate(final):
            r, flipped = dev["ro"][p], out.reshape(-1, 2, 2 ** lq)
            flipped[:] = (1 - r) * flipped + r * flipped[:, ::-1, :]
    return out


def ideal():
    return distribution(lab.logical_ops(), list(range(lab.NQ)))


def equivalent(ops, final):
    return float(0.5 * np.abs(distribution(ops, final) - ideal()).sum()) < 1e-9


def noisy_fidelity(ops, final, dev):
    return round(float(np.sum(np.sqrt(distribution(ops, final, dev) * ideal())) ** 2), 4)   # Hellinger fidelity
