"""Lesson 23 (L500) - numerical checks of the theorems in Foundations I: linear algebra for qubits.

Run:  python theorems.py            (all checks)      python theorems.py T23.4   (one check)
Each check prints what it verified and raises AssertionError if the theorem's prediction fails.
numpy + the shared statevector simulator (labs/_shared/qsim) only. Seeds are fixed; only rounded
values and pass/fail tolerances are printed, so the output is the same on every OS.
Bit order follows qsim (= Qiskit): qubit 0 is the rightmost character of a bitstring.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from qsim import statevector as sv  # noqa: E402

TOL = 1e-12
CHECKS = {}


def check(tid, name):
    def register(fn):
        CHECKS[tid] = (name, fn)
        return fn
    return register


def random_state(rng, dim):
    v = rng.normal(size=dim) + 1j * rng.normal(size=dim)
    return v / np.linalg.norm(v)


def random_unitary(rng, dim):
    """QR of a complex Gaussian matrix, with the phases of R's diagonal fixed (Haar-distributed U)."""
    z = rng.normal(size=(dim, dim)) + 1j * rng.normal(size=(dim, dim))
    q, r = np.linalg.qr(z)
    return q * (np.diag(r) / np.abs(np.diag(r)))


@check("T23.1", "Unitaries preserve inner products, norms and total probability")
def unitaries_preserve_norm():
    rng = np.random.default_rng(23)
    worst_ip, worst_norm = 0.0, 0.0
    for dim in (2, 4, 8, 16):
        for _ in range(250):
            u = random_unitary(rng, dim)
            a, b = random_state(rng, dim), random_state(rng, dim)
            worst_ip = max(worst_ip, abs(np.vdot(u @ a, u @ b) - np.vdot(a, b)))
            worst_norm = max(worst_norm, abs(np.linalg.norm(u @ a) - 1))
    assert worst_ip < TOL and worst_norm < TOL
    circuit = [sv.h(0), sv.cx(0, 1), (sv.ry(0.7), 2, ()), sv.cp(0.3, 1, 2)]
    u = sv.unitary(3, circuit)
    assert float(np.max(np.abs(u.conj().T @ u - np.eye(8)))) < TOL
    probs = np.abs(u @ random_state(rng, 8)) ** 2
    assert abs(probs.sum() - 1) < TOL
    shear = np.array([[1, 1], [0, 1]])
    grows = np.linalg.norm(shear @ np.array([0, 1]))
    assert grows > 1.4
    return [
        "1000 random unitaries (dims 2,4,8,16): max |<Ua|Ub> - <a|b>| < 1e-12: True",
        "max | ||Ua|| - 1 | < 1e-12: True",
        "qsim circuit H, CX, RY(0.7), CP(0.3) on 3 qubits: U^dagger U = I within 1e-12: True",
        f"probabilities after the circuit sum to {probs.sum():.6f}",
        f"non-unitary [[1,1],[0,1]] maps |1> to a vector of norm {grows:.4f} "
        f"(probabilities would sum to {grows ** 2:.1f})",
    ]


@check("T23.2", "Tensor products: (A x B)(C x D) = AC x BD, <a x b|c x d> = <a|c><b|d>, U x V is unitary")
def tensor_rules():
    rng = np.random.default_rng(232)
    worst = 0.0
    for _ in range(200):
        a, b, c, d = (rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2)) for _ in range(4))
        worst = max(worst, float(np.max(np.abs(np.kron(a, b) @ np.kron(c, d) - np.kron(a @ c, b @ d)))))
    assert worst < 1e-10
    worst_ip = 0.0
    for _ in range(200):
        a, b, c, d = (random_state(rng, 2) for _ in range(4))
        worst_ip = max(worst_ip, abs(np.vdot(np.kron(a, b), np.kron(c, d)) - np.vdot(a, c) * np.vdot(b, d)))
    assert worst_ip < TOL
    u, v = random_unitary(rng, 2), random_unitary(rng, 4)
    uv = np.kron(u, v)
    assert float(np.max(np.abs(uv.conj().T @ uv - np.eye(8)))) < TOL
    plus = np.array([1, 1]) / np.sqrt(2)
    one = np.array([0, 1])
    prod = np.kron(plus, one)                      # textbook order |a>|b> = |a> (x) |b>
    q = sv.run(2, [sv.h(1), sv.x(0)])              # qsim: qubit 1 = left factor, qubit 0 = right factor
    assert np.allclose(prod, q)
    return [
        "mixed-product rule on 200 random 2x2 pairs: max error < 1e-10: True",
        "inner product of product states factorises (200 cases): max error < 1e-12: True",
        "U (x) V for random 2x2 and 4x4 unitaries is an 8x8 unitary: True",
        f"|+> (x) |1> = {np.round(prod.real, 4).tolist()} (basis 00,01,10,11) = qsim H on q1, X on q0: True",
    ]


@check("T23.3", "Born rule in any orthonormal basis; global phase unobservable, relative phase observable")
def born_rule():
    rng = np.random.default_rng(233)
    worst = 0.0
    for dim in (2, 4, 8):
        for _ in range(100):
            psi, basis = random_state(rng, dim), random_unitary(rng, dim)
            p = np.abs(basis.conj().T @ psi) ** 2          # p_k = |<b_k|psi>|^2, b_k = column k
            worst = max(worst, abs(p.sum() - 1))
            phased = np.exp(1j * rng.uniform(0, 2 * np.pi)) * psi
            worst = max(worst, float(np.max(np.abs(np.abs(basis.conj().T @ phased) ** 2 - p))))
    assert worst < TOL
    plus, minus = sv.run(1, [sv.h(0)]), sv.run(1, [sv.x(0), sv.h(0)])
    z_plus, z_minus = sv.probabilities(plus, 4), sv.probabilities(minus, 4)
    x_plus = sv.probabilities(sv.run(1, [sv.h(0)], plus), 4)
    x_minus = sv.probabilities(sv.run(1, [sv.h(0)], minus), 4)
    assert z_plus == z_minus and x_plus == {"0": 1.0} and x_minus == {"1": 1.0}
    return [
        "300 random states and bases (dims 2,4,8): sum_k |<b_k|psi>|^2 = 1 within 1e-12: True",
        "multiplying by a random global phase changes no probability (within 1e-12): True",
        f"Z basis: |+> gives {z_plus}, |-> gives {z_minus} (identical)",
        f"X basis (H then measure): |+> gives {x_plus}, |-> gives {x_minus} (relative phase is visible)",
    ]


def measure_in(angle):
    """Rotate so that a Z measurement measures in the basis {cos a|0>+sin a|1>, -sin a|0>+cos a|1>}."""
    return sv.ry(-2 * angle)


@check("T23.4", "Bell state statistics: P(same outcome) = cos^2(a - b), E = cos 2(a - b)")
def bell_statistics():
    bell = sv.run(2, [sv.h(0), sv.cx(0, 1)])
    zz = sv.probabilities(bell, 4)
    assert zz == {"00": 0.5, "11": 0.5}
    rng = np.random.default_rng(234)
    worst, rows = 0.0, []
    for a, b in [(0.0, 0.0), (0.0, np.pi / 8), (0.0, np.pi / 4), (np.pi / 8, -np.pi / 8), (0.3, 1.1)]:
        state = sv.run(2, [(measure_in(a), 0, ()), (measure_in(b), 1, ())], bell)
        p = np.abs(state) ** 2
        same = p[0] + p[3]
        worst = max(worst, abs(same - np.cos(a - b) ** 2))
        shots = 20000
        counts = rng.multinomial(shots, p / p.sum())
        freq = (counts[0] + counts[3]) / shots
        sigma = np.sqrt(same * (1 - same) / shots) + 1e-12
        assert abs(freq - same) <= 4 * sigma + 1e-9
        rows.append(f"a = {a:.4f}, b = {b:.4f}: P(same) = {same:.4f}, cos^2(a-b) = {np.cos(a - b) ** 2:.4f}, "
                    f"E = {round(2 * same - 1, 4) + 0.0:.4f}; 20000 sampled shots within 4 sigma: True")
    assert worst < TOL
    bells = [sv.run(2, ops) for ops in ([sv.h(0), sv.cx(0, 1)], [sv.x(0), sv.h(0), sv.cx(0, 1)],
                                        [sv.x(1), sv.h(0), sv.cx(0, 1)], [sv.x(1), sv.x(0), sv.h(0), sv.cx(0, 1)])]
    gram = np.array([[np.vdot(x, y) for y in bells] for x in bells])
    assert np.allclose(gram, np.eye(4))
    decoded = [max(sv.probabilities(sv.run(2, [sv.cx(0, 1), sv.h(0)], s), 6).items(), key=lambda kv: kv[1])
               for s in bells]
    assert all(p == 1.0 for _, p in decoded)
    return [f"computational basis: {zz}"] + rows + [
        "the four Bell states are orthonormal (Gram matrix = I): True",
        "CX then H maps them to " + ", ".join(k for k, _ in decoded) + " with probability 1 (Bell measurement)",
    ]


def run(ids=None):
    out = []
    for tid, (name, fn) in CHECKS.items():
        if ids and tid not in ids:
            continue
        out.append(f"[{tid}] {name}")
        out.extend("  " + line for line in fn())
    return out


if __name__ == "__main__":
    print("\n".join(run(sys.argv[1:])))
