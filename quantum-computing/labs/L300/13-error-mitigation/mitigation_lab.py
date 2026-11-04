"""Lab 13 - error mitigation: readout calibration-matrix inverse and zero-noise extrapolation (ZNE).

Run:  python mitigation_lab.py        (numpy only; density-matrix simulator in labs/_shared/qsim)
SDK path (Mitiq 1.1.0 + Cirq): python mitiq_zne.py   (runs in CI job l300-extras, not yet observed)
"""
import functools
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from qsim import density as dm  # noqa: E402
from qsim import statevector as sv  # noqa: E402

READOUT = {"p01": 0.03, "p10": 0.06}           # P(read 1 | 0), P(read 0 | 1): illustrative values
GATE = {"p1": 0.003, "p2": 0.03}               # depolarizing after 1q gates / after each CX


# ---------- A. readout-error mitigation ----------
def true_bell():
    return dm.probabilities(dm.pure(sv.run(2, [sv.h(0), sv.cx(0, 1)])))


def measure(p_true, shots, rng, n=2):
    a = dm.readout_matrix(READOUT["p01"], READOUT["p10"], n)     # the device's real (unknown) flips
    c = dm.sample(a @ p_true, shots, rng)
    return np.array([c.get(dm.label(i, n), 0) for i in range(2 ** n)]) / shots


def calibrate(shots, rng, n=2):
    """Prepare each basis state, measure it: column j = observed distribution when |j> was prepared."""
    return np.column_stack([measure(np.eye(2 ** n)[j], shots, rng, n) for j in range(2 ** n)])


def mitigate(p_noisy, m_est):
    """Plain inverse: unbiased on average, but the result is a QUASI-probability (can go negative)."""
    return np.linalg.solve(m_est, p_noisy)


# ---------- B. zero-noise extrapolation ----------
def mirror_ops(n=3):
    ghz = [sv.h(0)] + [sv.cx(i, i + 1) for i in range(n - 1)]
    return ghz + [sv.cx(i, i + 1) for i in reversed(range(n - 1))] + [sv.h(0)]   # U then U^-1: ideal |000>


def folded(ops, scale):
    """Local unitary folding of every CX: G -> G (G^-1 G)^k, scale = 2k + 1 (CX is its own inverse)."""
    out = []
    for op in ops:
        out += [op] * (scale if op[2] else 1)
    return out


@functools.lru_cache(maxsize=None)
def exact_value(scale, n=3):
    steps = []
    for op in folded(mirror_ops(n), scale):
        qubits = tuple(op[2]) + (op[1],)
        steps += [op, ("depol", GATE["p2"] if len(qubits) == 2 else GATE["p1"], qubits)]
    return dm.probabilities(dm.run(n, steps))[0]          # observable: P(000), ideal 1.0


def noisy_value(scale, n=3, shots=None, rng=None):
    p0 = exact_value(scale, n)
    return p0 if shots is None else rng.binomial(shots, p0) / shots   # shot noise on top of gate noise


def richardson(scales, values):
    """Exact polynomial through all points, evaluated at 0 (Lagrange form)."""
    return sum(v * np.prod([s2 / (s2 - s) for s2 in scales if s2 != s]) for s, v in zip(scales, values))


def linear(scales, values):
    slope, intercept = np.polyfit(scales, values, 1)
    return intercept


def tvd(p, q):
    return round(float(0.5 * np.abs(np.asarray(p) - np.asarray(q)).sum()), 4)   # total variation distance


if __name__ == "__main__":
    rng = np.random.default_rng(11)
    for cal_shots, shots in ((4000, 4000), (100, 200)):            # healthy budget, then the fault: too few shots
        m_est = calibrate(cal_shots, rng)
        p_noisy = measure(true_bell(), shots, rng)
        quasi = mitigate(p_noisy, m_est)
        print(json.dumps({"cal_shots": cal_shots, "shots": shots, "raw": np.round(p_noisy, 4).tolist(),
                          "mitigated": np.round(quasi, 4).tolist(), "min": round(float(quasi.min()), 4),
                          "tvd_raw": tvd(p_noisy, true_bell()), "tvd_mitigated": tvd(quasi, true_bell())}))
        try:
            rng.choice(4, p=quasi)                                   # downstream code expects real probabilities
        except ValueError as e:
            print("  downstream sampling failed:", e)
    scales = [1, 3, 5]
    values = [noisy_value(s) for s in scales]
    for s, v in zip(scales, values):
        print(json.dumps({"scale": s, "cx_count": 4 * s, "P000": round(float(v), 4)}))
    print("ideal 1.0 | raw", round(float(values[0]), 4), "| linear ZNE", round(float(linear(scales, values)), 4),
          "| Richardson ZNE", round(float(richardson(scales, values)), 4))
