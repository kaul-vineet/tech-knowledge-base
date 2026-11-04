"""Lesson 24 (L500) - numerical checks of the theorems in Foundations II: quantum information basics.

Run:  python theorems.py            (all checks)      python theorems.py T24.2   (one check)
Each check prints what it verified and raises AssertionError if the theorem's prediction fails.
numpy + the shared statevector simulator (labs/_shared/qsim) only; fixed seeds, rounded output.
Bit order follows qsim (= Qiskit): qubit 0 is the rightmost character of a bitstring, and a
statevector reshaped to (2,)*n has axes (q[n-1], ..., q1, q0).
"""
import itertools
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
    z = rng.normal(size=(dim, dim)) + 1j * rng.normal(size=(dim, dim))
    q, r = np.linalg.qr(z)
    return q * (np.diag(r) / np.abs(np.diag(r)))


def ptrace_left(rho):
    """rho on (left (x) right) for two qubits -> reduced state of the RIGHT qubit (trace out the left)."""
    return np.einsum("abac->bc", rho.reshape(2, 2, 2, 2))


def ptrace_right(rho):
    """rho on (left (x) right) for two qubits -> reduced state of the LEFT qubit (trace out the right)."""
    return np.einsum("abcb->ac", rho.reshape(2, 2, 2, 2))


def fidelity(a, b):
    return abs(np.vdot(a, b)) ** 2


@check("T24.1", "No-cloning: no unitary U and blank |e> give U|psi>|e> = |psi>|psi> for all psi")
def no_cloning():
    copier = sv.unitary(2, [sv.cx(1, 0)])            # input on qubit 1 (left), blank |0> on qubit 0 (right)
    zero, one = np.array([1, 0]), np.array([0, 1])
    for basis_state in (zero, one):
        out = copier @ np.kron(basis_state, zero)
        assert fidelity(out, np.kron(basis_state, basis_state)) > 1 - TOL
    rows = []
    worst = 1.0
    for theta in (0.0, np.pi / 3, np.pi / 2, 2 * np.pi / 3, np.pi):
        psi = np.array([np.cos(theta / 2), np.sin(theta / 2)])
        out = copier @ np.kron(psi, zero)
        f = fidelity(out, np.kron(psi, psi))
        c, s = np.cos(theta / 2), np.sin(theta / 2)
        predicted = (c ** 3 + s ** 3) ** 2
        copy_b = ptrace_left(np.outer(out, out.conj()))            # the "copy" qubit on its own
        f_copy = float(np.real(psi.conj() @ copy_b @ psi))
        assert abs(f - predicted) < TOL and abs(f_copy - (c ** 4 + s ** 4)) < TOL
        worst = min(worst, f)
        rows.append(f"theta = {theta:.4f}: joint fidelity {f:.4f} = (c^3 + s^3)^2 = {predicted:.4f}; "
                    f"copy alone {f_copy:.4f} = c^4 + s^4")
    assert abs(worst - 0.5) < TOL
    plus = np.array([1, 1]) / np.sqrt(2)
    need = np.vdot(zero, plus) ** 2                  # <0|+>^2 : overlap two perfect clones would need
    rng = np.random.default_rng(241)
    worst_keep = 0.0
    for _ in range(500):
        u = random_unitary(rng, 4)
        kept = np.vdot(u @ np.kron(zero, zero), u @ np.kron(plus, zero))
        worst_keep = max(worst_keep, abs(kept - np.vdot(zero, plus)))
    assert worst_keep < TOL
    return ["CNOT copier clones |0> and |1> exactly (fidelity 1)"] + rows + [
        f"minimum fidelity {worst:.4f} at theta = pi/2 (|+> becomes a Bell state, not |+>|+>)",
        f"500 random unitaries keep <0,e|+,e> = {np.vdot(zero, plus).real:.4f}; perfect clones would need "
        f"<0|+>^2 = {need.real:.4f}: impossible",
    ]


def teleport_branches(psi):
    """q0 = message, q1 = Alice's half, q2 = Bob's half. Returns {(m0, m1): (prob, Bob's corrected state)}."""
    start = np.kron(np.kron([1, 0], [1, 0]), psi)       # |q2 q1 q0> = |0>|0>|psi>
    state = sv.run(3, [sv.h(1), sv.cx(1, 2), sv.cx(0, 1), sv.h(0)], start)
    t = state.reshape(2, 2, 2)                          # axes (q2, q1, q0)
    out = {}
    for m0, m1 in itertools.product((0, 1), repeat=2):
        bob = t[:, m1, m0]
        prob = float(np.vdot(bob, bob).real)
        bob = bob / np.sqrt(prob)
        if m1:
            bob = sv.X @ bob                            # X correction for Alice's q1 outcome
        if m0:
            bob = sv.Z @ bob                            # Z correction for Alice's q0 outcome
        out[(m0, m1)] = (prob, bob)
    return out


@check("T24.2", "Teleportation and superdense coding are exact for every input")
def teleport_and_superdense():
    rng = np.random.default_rng(242)
    worst_f, worst_p = 1.0, 0.0
    for _ in range(200):
        psi = random_state(rng, 2)
        for prob, bob in teleport_branches(psi).values():
            worst_f = min(worst_f, fidelity(psi, bob))
            worst_p = max(worst_p, abs(prob - 0.25))
    assert worst_f > 1 - TOL and worst_p < TOL
    example = np.array([np.cos(np.pi / 8), np.sin(np.pi / 8)])
    probs = sorted(round(p, 4) for p, _ in teleport_branches(example).values())
    decoded = {}
    for a, b in itertools.product((0, 1), repeat=2):
        enc = ([sv.x(0)] if b else []) + ([(sv.Z, 0, ())] if a else [])      # Alice applies Z^a X^b to q0
        state = sv.run(2, [sv.h(0), sv.cx(0, 1)] + enc + [sv.cx(0, 1), sv.h(0)])
        probs_out = sv.probabilities(state, 6)
        (bits, p), = probs_out.items()
        assert p == 1.0 and bits == f"{b}{a}"             # printed q1 q0 = b a
        decoded[f"{a}{b}"] = bits[::-1]
    return [
        "200 random states x 4 outcomes: each outcome has probability 0.25 (within 1e-12) and Bob's corrected "
        "qubit has fidelity 1 (within 1e-12): True",
        f"psi = cos(pi/8)|0> + sin(pi/8)|1>: outcome probabilities {probs}",
        "superdense coding, message ab -> Bob decodes (q0 q1): "
        + ", ".join(f"{k} -> {v}" for k, v in decoded.items()) + " with probability 1",
    ]


def dj_probability_all_zero(n, f):
    """Phase-oracle form of Deutsch-Jozsa: H^n, diag((-1)^f(x)), H^n on |0...0>; returns P(0...0)."""
    hn = sv.unitary(n, [sv.h(q) for q in range(n)])
    oracle = np.diag([(-1.0) ** f(x) for x in range(2 ** n)])
    final = hn @ oracle @ hn @ np.eye(2 ** n)[0]
    return float(abs(final[0]) ** 2)


@check("T24.3", "Deutsch-Jozsa: P(0^n) = 1 if f is constant and 0 if f is balanced, with one query")
def deutsch_jozsa():
    n = 3
    consts = [dj_probability_all_zero(n, lambda x, c=c: c) for c in (0, 1)]
    balanced = []
    for ones in itertools.combinations(range(2 ** n), 2 ** (n - 1)):
        table = set(ones)
        balanced.append(dj_probability_all_zero(n, lambda x, t=table: int(x in t)))
    assert all(abs(p - 1) < TOL for p in consts) and max(balanced) < TOL
    # ancilla form (phase kickback) for f(x) = x0 XOR x2: inputs q0..q2, ancilla q3 prepared in |->
    ops = [sv.x(3), sv.h(3)] + [sv.h(q) for q in range(3)] + [sv.cx(0, 3), sv.cx(2, 3)] + [sv.h(q) for q in range(3)]
    probs = sv.probabilities(sv.run(4, ops), 6)
    p000 = sum(p for bits, p in probs.items() if bits[1:] == "000")
    assert p000 < TOL
    return [
        f"n = 3: both constant functions give P(000) = {consts[0]:.4f}, {consts[1]:.4f}",
        f"all {len(balanced)} balanced functions give P(000) = {max(balanced):.4f} (max)",
        f"ancilla circuit for f = x0 XOR x2 (|-> ancilla, phase kickback): P(inputs 000) = {p000 + 0.0:.4f}",
        f"a deterministic classical algorithm needs 2^(n-1) + 1 = {2 ** (n - 1) + 1} queries in the worst case",
    ]


@check("T24.4", "Density matrices: trace 1, PSD, purity; partial trace of a Bell pair is I/2; no signalling")
def density_and_partial_trace():
    rng = np.random.default_rng(244)
    bell = sv.run(2, [sv.h(0), sv.cx(0, 1)])
    rho = np.outer(bell, bell.conj())
    rho_a, rho_b = ptrace_right(rho), ptrace_left(rho)
    assert np.allclose(rho_a, np.eye(2) / 2) and np.allclose(rho_b, np.eye(2) / 2)
    purity_global = float(np.trace(rho @ rho).real)
    purity_b = float(np.trace(rho_b @ rho_b).real)
    worst = 0.0
    for _ in range(200):
        psi = random_state(rng, 4)
        r = np.outer(psi, psi.conj())
        eig = np.linalg.eigvalsh(r)
        assert eig.min() > -TOL and abs(np.trace(r) - 1) < TOL and np.allclose(r, r.conj().T)
        ua = np.kron(random_unitary(rng, 2), np.eye(2))           # anything Alice (left qubit) does
        worst = max(worst, float(np.max(np.abs(ptrace_left(ua @ r @ ua.conj().T) - ptrace_left(r)))))
        p0, p1 = np.kron(np.diag([1, 0]), np.eye(2)), np.kron(np.diag([0, 1]), np.eye(2))
        measured = p0 @ r @ p0 + p1 @ r @ p1                       # Alice measures, result not sent
        worst = max(worst, float(np.max(np.abs(ptrace_left(measured) - ptrace_left(r)))))
    assert worst < TOL
    plus = np.array([1, 1]) / np.sqrt(2)
    mix = 0.5 * np.outer([1, 0], [1, 0]) + 0.5 * np.outer(plus, plus)
    eig_mix = np.sort(np.linalg.eigvalsh(mix))[::-1]
    purity_mix = float(np.trace(mix @ mix).real)
    assert abs(purity_mix - 0.75) < TOL
    return [
        f"Bell pair: global purity Tr(rho^2) = {purity_global:.4f}; rho_A = rho_B = I/2: True; "
        f"Tr(rho_B^2) = {purity_b:.4f}",
        "200 random 2-qubit pure states: Hermitian, eigenvalues >= 0, trace 1: True",
        "no signalling: Alice's random unitary or unread measurement changes rho_B by < 1e-12: True",
        f"mixture 1/2|0><0| + 1/2|+><+|: eigenvalues {np.round(eig_mix, 4).tolist()}, purity {purity_mix:.4f}",
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
