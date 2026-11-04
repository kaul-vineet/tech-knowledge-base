"""Milestone 1 - Shor's order finding for tiny N on the quantum topic's numpy statevector simulator (qsim).

Registers (qsim = Qiskit bit order): counting qubits 0..t-1 (t = 2 * ceil(log2 N)), work qubits t..t+n-1 starting in |1>.
Controlled-U^(2^j) maps |y> -> |a^(2^j) y mod N>. Like every small textbook demo it is applied as a permutation of
basis states (a COMPILED oracle that already uses the answer a^(2^j) mod N). For N = 15, a = 7 the same oracle is also
built from CX/CCX gates and checked against the permutation. Nothing here says anything about RSA-2048: see estimates.py.
"""
import math
from fractions import Fraction

import numpy as np

import _kb  # noqa: F401  (puts the quantum labs on sys.path)
import theorems as l25  # quantum L500 #25: order(), split(), qft_ops(), inverse_ops(), order_finding_distribution()
from qsim import statevector as sv

SEED, SHOTS = 2026, 200


def controlled_mult(state, ctrl, t, n, mult, modulus):
    """Permutation oracle: where qubit ctrl = 1 and the work value y < N, replace y by mult * y mod N."""
    idx = np.arange(len(state))
    y = (idx >> t) & ((1 << n) - 1)
    on = (((idx >> ctrl) & 1) == 1) & (y < modulus)
    dest = idx.copy()
    dest[on] = (idx[on] & ~(((1 << n) - 1) << t)) | (((mult * y[on]) % modulus) << t)
    out = np.zeros_like(state)
    out[dest] = state
    return out


def gate_level_ops_15_7(t):
    """CX/CCX version of controlled-U^(2^j) for N = 15, a = 7 (work qubits t..t+3). 7^4 = 1 mod 15, so j >= 2 adds
    no gates - which only works because we already know the period (Smolin, Smith & Vargo 2013)."""
    w = [t + k for k in range(4)]

    def cswap(c, a, b):
        return [sv.cx(b, a), (sv.X, b, (c, a)), sv.cx(b, a)]

    ops = []
    for j in range(t):
        m = pow(7, 2 ** j, 15)
        if m == 7:                                          # x8 (rotate right 1 bit), then flip all: -8y = 7y mod 15
            ops += cswap(j, w[0], w[1]) + cswap(j, w[1], w[2]) + cswap(j, w[2], w[3]) + [sv.cx(j, q) for q in w]
        elif m == 4:                                        # x4: rotate bits by 2
            ops += cswap(j, w[1], w[3]) + cswap(j, w[0], w[2])
    return ops


def counts(ops):
    flat = list(sv.flatten(ops))
    return {"cx": sum(1 for g, _, c in flat if len(c) == 1 and np.allclose(g, sv.X)),
            "ccx": sum(1 for g, _, c in flat if len(c) == 2)}


def run_order_finding(modulus, a, gate_level=False):
    n = math.ceil(math.log2(modulus))
    t = 2 * n
    zero = np.zeros(2 ** (t + n), dtype=complex)
    zero[0] = 1                         # explicit |0...0>: sv.run(n, ops) without a state builds np.eye(2**n) (16 GiB at 15 qubits)
    state = sv.run(t + n, [sv.x(t)] + [sv.h(j) for j in range(t)], zero)
    if gate_level:
        state = sv.run(t + n, gate_level_ops_15_7(t), state)
    else:
        for j in range(t):
            state = controlled_mult(state, j, t, n, pow(a, 2 ** j, modulus), modulus)
    iqft = l25.inverse_ops(l25.qft_ops(t))
    state = sv.run(t + n, iqft, state)
    probs = (np.abs(state) ** 2).reshape(2 ** n, 2 ** t).sum(axis=0)      # marginal of the counting register
    return {"N": modulus, "a": a, "t": t, "n_work": n, "probs": probs, "iqft_ops": iqft}


def recover_factors(m, t, a, modulus):
    """Classical post-processing: continued fraction of m / 2^t -> candidate r -> gcd(a^(r/2) +- 1, N)."""
    if m == 0:
        return None
    r = Fraction(m, 2 ** t).limit_denominator(modulus).denominator
    if pow(a, r, modulus) != 1 or r % 2 or pow(a, r // 2, modulus) == modulus - 1:
        return None
    f = math.gcd(pow(a, r // 2, modulus) - 1, modulus)
    return (f, modulus // f) if 1 < f < modulus else None


def shor(modulus, a, gate_level=False, shots=SHOTS, seed=SEED):
    res = run_order_finding(modulus, a, gate_level)
    t, probs = res["t"], res["probs"]
    p_success = float(sum(p for m, p in enumerate(probs) if recover_factors(m, t, a, modulus)))
    rng = np.random.default_rng(seed)
    sample = rng.choice(len(probs), size=shots, p=probs / probs.sum())
    found = [recover_factors(int(m), t, a, modulus) for m in sample]
    flat = list(sv.flatten(res["iqft_ops"]))
    oracle = counts(gate_level_ops_15_7(t)) if gate_level else {"controlled_mult_permutations": t}
    return {"N": modulus, "a": a, "order_r": l25.order(a, modulus), "qubits": t + res["n_work"],
            "counting_qubits": t, "work_qubits": res["n_work"],
            "gates": {"h": 2 * t, "x": 1, "iqft_cp": sum(1 for g, _, c in flat if len(c) == 1 and not np.allclose(g, sv.X)),
                      "iqft_swap_cx": sum(1 for g, _, c in flat if len(c) == 1 and np.allclose(g, sv.X)), **oracle},
            "oracle": "gate-level CX/CCX (compiled with known period)" if gate_level else "permutation (compiled)",
            "p_success_per_run": round(p_success, 4), "shots": shots,
            "successes": sum(1 for f in found if f), "factors": sorted(next(f for f in found if f)),
            "statevector_bytes": 16 * 2 ** (t + res["n_work"]), "probs": probs,
            "scope": f"toy N = {modulus}; mechanism only - says nothing about when RSA-2048 falls"}


def matches_fft_shortcut(result):
    """Cross-check with quantum L500 #25's closed-form distribution (FFT of the periodic register)."""
    ref = l25.order_finding_distribution(result["a"], result["N"], result["counting_qubits"])
    return bool(np.allclose(result["probs"], ref, atol=1e-9))


def public(result):
    return {k: v for k, v in result.items() if k != "probs"}


if __name__ == "__main__":
    import json
    for modulus, a, gl in ((15, 7, False), (15, 7, True), (21, 2, False)):
        r = shor(modulus, a, gl)
        print(json.dumps({**public(r), "matches_L500_fft": matches_fft_shortcut(r)}))
