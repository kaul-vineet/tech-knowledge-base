"""Independent numpy check for lab 10 (no quantum SDK). Run: python crosscheck_numpy.py

Same experiment as param_lab.py: RY(theta)|0>, sweep 21 angles, exact <Z> and <X>, seeded shot
estimates of <Z>, then a least-squares fit of a*cos(theta) + b*sin(theta) + c.
numpy's RNG is not Qiskit's, so sampled numbers differ from the SDK run; the fit tolerance does not.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from qsim import statevector as sv  # noqa: E402

THETAS = np.linspace(0, 2 * np.pi, 21)
Z = np.diag([1.0, -1.0])
X = np.array([[0.0, 1.0], [1.0, 0.0]])


def state(theta, gate=sv.ry):
    return gate(theta) @ np.array([1, 0], dtype=complex)


def expectation(op, psi):
    return float(np.real(psi.conj() @ op @ psi))


def exact(gate=sv.ry, thetas=THETAS):
    return (np.array([expectation(Z, state(t, gate)) for t in thetas]),
            np.array([expectation(X, state(t, gate)) for t in thetas]))


def sampled_z(thetas=THETAS, shots=400, seed=7, gate=sv.ry):
    rng = np.random.default_rng(seed)
    p1 = np.array([abs(state(t, gate)[1]) ** 2 for t in thetas])
    ones = rng.binomial(shots, np.clip(p1, 0, 1))
    return (shots - 2 * ones) / shots                  # <Z> = (n0 - n1) / shots


def fit_cos_sin(thetas, values):
    a = np.column_stack([np.cos(thetas), np.sin(thetas), np.ones_like(thetas)])
    coef, *_ = np.linalg.lstsq(a, values, rcond=None)
    return [round(float(c), 3) + 0.0 for c in coef]   # + 0.0 turns -0.0 into 0.0


if __name__ == "__main__":
    z, x = exact()
    print("exact <Z> at theta = 0, pi/2, pi:", np.round(z[[0, 5, 10]], 4).tolist())
    print("fit exact <Z> [a, b, c]:", fit_cos_sin(THETAS, z))
    print("fit exact <X> [a, b, c]:", fit_cos_sin(THETAS, x))
    print("fit sampled <Z>, 400 shots, numpy seed 7:", fit_cos_sin(THETAS, sampled_z()))
