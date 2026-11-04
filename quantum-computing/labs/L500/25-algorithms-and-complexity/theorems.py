"""Lesson 25 (L500) - numerical checks of the theorems in Foundations III: algorithms and complexity.

Run:  python theorems.py            (all checks)      python theorems.py T25.1   (one check)
Each check prints what it verified and raises AssertionError if the theorem's prediction fails.
numpy + the shared statevector simulator (labs/_shared/qsim) + the standard library only.
Bit order follows qsim (= Qiskit): qubit j carries weight 2**j in the basis index.
"""
import math
import sys
from fractions import Fraction
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


# ---------------- Grover ----------------
def grover_curve(n, marked, k_max):
    """Statevector Grover: oracle flips marked amplitudes, diffusion reflects about the mean (2|s><s| - I)."""
    dim = 2 ** n
    psi = np.full(dim, 1 / np.sqrt(dim))
    idx = np.array(sorted(marked))
    out = [float(np.sum(psi[idx] ** 2))]
    for _ in range(k_max):
        psi[idx] *= -1
        psi = 2 * psi.mean() - psi
        out.append(float(np.sum(psi[idx] ** 2)))
    return out


def grover_formula(n_items, m, k):
    theta = math.asin(math.sqrt(m / n_items))
    return math.sin((2 * k + 1) * theta) ** 2


def k_opt_formula(n_items, m):
    theta = math.asin(math.sqrt(m / n_items))
    return math.floor(math.pi / (4 * theta))


@check("T25.1", "Grover: P_k = sin^2((2k+1) theta), sin theta = sqrt(M/N); best k ~ (pi/4) sqrt(N/M)")
def grover():
    rng = np.random.default_rng(251)
    rows, worst = [], 0.0
    for n, m in [(2, 1), (4, 1), (6, 1), (8, 1), (10, 1), (10, 4), (12, 1)]:
        n_items = 2 ** n
        marked = set(rng.choice(n_items, size=m, replace=False).tolist())
        kf = k_opt_formula(n_items, m)
        curve = grover_curve(n, marked, 2 * kf + 2)
        worst = max(worst, max(abs(p - grover_formula(n_items, m, k)) for k, p in enumerate(curve)))
        k_best = int(np.argmax(curve[: kf + 2]))
        assert k_best == kf, (n, m, k_best, kf)
        rows.append(f"N = {n_items:5d}, M = {m}: best k = {k_best:3d} (floor(pi/(4 theta)) = {kf:3d}, "
                    f"(pi/4) sqrt(N/M) = {math.pi / 4 * math.sqrt(n_items / m):7.2f}), P = {curve[k_best]:.4f}")
    assert worst < 1e-9
    over = grover_curve(6, {37}, 12)
    return rows + [
        "statevector simulation matches sin^2((2k+1) theta) for every k tested (max error < 1e-9): True",
        f"overshoot, N = 64: P at k = 6 is {over[6]:.4f}, at k = 12 it is {over[12]:.4f} (rotation keeps turning)",
    ]


# ---------------- QFT ----------------
def qft_ops(n):
    """H + controlled phases + final swaps; maps |j> to (1/sqrt N) sum_k e^{2 pi i jk/N} |k> (qsim order)."""
    ops = []
    for j in reversed(range(n)):
        ops.append(sv.h(j))
        for k in reversed(range(j)):
            ops.append(sv.cp(np.pi / 2 ** (j - k), k, j))
    ops += [sv.swap(i, n - 1 - i) for i in range(n // 2)]
    return ops


def dft(n_items):
    j, k = np.meshgrid(np.arange(n_items), np.arange(n_items), indexing="ij")
    return np.exp(2j * np.pi * j * k / n_items) / np.sqrt(n_items)


@check("T25.2", "The QFT matrix F_jk = e^{2 pi i jk/N}/sqrt(N) is unitary and is built by O(n^2) gates")
def qft_unitary():
    worst_unitary = max(float(np.max(np.abs(dft(2 ** n).conj().T @ dft(2 ** n) - np.eye(2 ** n))))
                        for n in range(1, 9))
    assert worst_unitary < 1e-10
    worst_circuit = 0.0
    rows = []
    for n in range(1, 6):
        ops = list(sv.flatten(qft_ops(n)))
        u = sv.unitary(n, ops)
        worst_circuit = max(worst_circuit, float(np.max(np.abs(u - dft(2 ** n)))))
        n_h = sum(1 for g, _, c in ops if not c and np.allclose(g, sv.H))
        n_cp = sum(1 for g, _, c in ops if c and not np.allclose(g, sv.X))
        n_swaps = n // 2
        assert n_h == n and n_cp == n * (n - 1) // 2
        rows.append(f"n = {n}: {n_h} H + {n_cp} controlled phases + {n_swaps} swaps "
                    f"= {n_h + n_cp + n_swaps} gates (n(n+1)/2 + floor(n/2)); FFT on 2^n entries ~ n 2^n = {n * 2 ** n}")
    assert worst_circuit < 1e-10
    return [
        "F^dagger F = I for N = 2 .. 256 (max error < 1e-10): True",
        "qsim circuit (H, CP, SWAP) equals F for n = 1 .. 5 (max error < 1e-10): True",
    ] + rows


# ---------------- phase estimation ----------------
def inverse_ops(ops):
    return [(g.conj().T, t, c) for g, t, c in reversed(list(sv.flatten(ops)))]


def qpe_distribution(phi, t):
    """t counting qubits (q0..q[t-1]), target q[t] = |1>, an eigenstate of P(2 pi phi) with eigenvalue e^{2 pi i phi}."""
    ops = [sv.x(t)] + [sv.h(j) for j in range(t)]
    ops += [sv.cp(2 * np.pi * phi * 2 ** j, j, t) for j in range(t)]     # controlled-U^(2^j)
    ops += inverse_ops(qft_ops(t))
    state = sv.run(t + 1, ops).reshape(2, 2 ** t)                        # axes (target, counting)
    return np.sum(np.abs(state) ** 2, axis=0)


def qpe_formula(phi, t, m):
    big_t = 2 ** t
    k = np.arange(big_t)
    return float(abs(np.sum(np.exp(2j * np.pi * k * (phi - m / big_t)))) ** 2 / big_t ** 2)


@check("T25.3", "Phase estimation: exact when phi = m/2^t; otherwise the nearest m has P >= 4/pi^2")
def phase_estimation():
    rows, worst, worst_best = [], 0.0, 1.0
    for t in (3, 4, 5, 6):
        for phi in (0.125, 1 / 3, 0.3, 0.7071, 0.5 + 1 / 2 ** (t + 1)):
            dist = qpe_distribution(phi, t)
            worst = max(worst, max(abs(dist[m] - qpe_formula(phi, t, m)) for m in range(2 ** t)))
            best = int(np.argmax(dist))
            worst_best = min(worst_best, float(dist[best]))
            if t == 3 and phi != 0.5 + 1 / 16:
                rows.append(f"t = 3, phi = {phi:.4f}: most likely m = {best} (m/8 = {best / 8:.4f}), "
                            f"P = {dist[best]:.4f}")
    assert worst < 1e-10 and worst_best >= 4 / math.pi ** 2 - 1e-12
    mid = qpe_distribution(0.5625, 3)
    assert abs(mid[4] - mid[5]) < TOL
    rows.append(f"t = 3, phi = 0.5625 (halfway between 4/8 and 5/8): P(4) = P(5) = {mid[4]:.4f}")
    return rows + [
        "simulated distribution equals |(1/T) sum_k e^{2 pi i k (phi - m/T)}|^2 for t = 3..6 (max error < 1e-10): True",
        f"smallest P(most likely m) over all cases = {worst_best:.4f} >= 4/pi^2 = {4 / math.pi ** 2:.4f}: True",
    ]


# ---------------- Shor: factoring -> order finding ----------------
def order(a, n):
    r, y = 1, a % n
    while y != 1:
        y = y * a % n
        r += 1
    return r


def split(a, n):
    """Shor's classical post-processing: returns a nontrivial factor of n from the order of a, or None."""
    g = math.gcd(a, n)
    if g > 1:
        return g
    r = order(a, n)
    if r % 2 or pow(a, r // 2, n) == n - 1:
        return None
    f = math.gcd(pow(a, r // 2, n) - 1, n)
    return f if 1 < f < n else None


def order_finding_distribution(a, n, t):
    """Exact statevector of the order-finding circuit: (1/sqrt T) sum_k |k>|a^k mod n>, then inverse QFT."""
    big_t = 2 ** t
    vals = [pow(a, k, n) for k in range(big_t)]
    probs = np.zeros(big_t)
    for y in sorted(set(vals)):
        col = np.array([1.0 if v == y else 0.0 for v in vals]) / np.sqrt(big_t)
        probs += np.abs(np.fft.fft(col, norm="ortho")) ** 2     # inverse QFT = conjugate DFT (sign e^{-2 pi i})
    return probs


def recovered_order(m, t, a, n):
    if m == 0:
        return None
    r = Fraction(m, 2 ** t).limit_denominator(n).denominator
    return r if pow(a, r, n) == 1 else None


@check("T25.4", "Shor's reduction: an even order r with a^(r/2) != -1 (mod N) yields gcd(a^(r/2) - 1, N)")
def shor_reduction():
    rows = []
    for n in (15, 21, 33, 35, 91):
        coprime = [a for a in range(2, n) if math.gcd(a, n) == 1]
        good = [a for a in coprime if split(a, n)]
        frac = len(good) / len(coprime)
        assert frac >= 0.5
        a = good[0]
        r = order(a, n)
        f = split(a, n)
        rows.append(f"N = {n}: {len(good)}/{len(coprime)} = {frac:.4f} of the coprime a in [2, N-1] succeed; "
                    f"e.g. a = {a}, r = {r}, gcd({a}^{r // 2} - 1, {n}) = {f}, {n} = {f} x {n // f}")
    dist15 = order_finding_distribution(7, 15, 8)
    peaks = {m: round(float(p), 4) for m, p in enumerate(dist15) if p > 1e-9}
    p_ok15 = sum(p for m, p in enumerate(dist15) if recovered_order(m, 8, 7, 15) == 4)
    dist21 = order_finding_distribution(2, 21, 9)
    p_ok21 = sum(p for m, p in enumerate(dist21) if recovered_order(m, 9, 2, 21) == 6)
    m21 = int(np.argmax(dist21[300:])) + 300
    cf = Fraction(m21, 512).limit_denominator(21)
    assert peaks == {0: 0.25, 64: 0.25, 128: 0.25, 192: 0.25} and p_ok15 > 0.49 and p_ok21 > 0.3
    return rows + [
        f"order finding, N = 15, a = 7, t = 8: outcomes {peaks}; one run recovers r = 4 with P = {p_ok15:.4f}",
        f"N = 21, a = 2, t = 9: a likely outcome m = {m21}, {m21}/512 -> continued fraction {cf} -> r = "
        f"{cf.denominator}; one run recovers r = 6 with P = {p_ok21:.4f}",
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
