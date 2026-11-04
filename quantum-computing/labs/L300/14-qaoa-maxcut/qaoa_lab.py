"""Lab 14 - QAOA on MaxCut (5 nodes, p = 1 and 2) against the brute-force classical optimum.

Run:  python qaoa_lab.py      (numpy only: exact statevector, so every difference comes from the optimizer)
SDK path (Qiskit StatevectorEstimator + scipy COBYLA): python qaoa_qiskit.py   (runs in CI, not yet observed)
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from qsim import statevector as sv  # noqa: E402

EDGES = [(0, 1), (0, 2), (0, 4), (1, 2), (2, 3), (3, 4)]   # the 5-node graph of IBM's QAOA tutorial
N = 5
Z = np.arange(2 ** N)
CUT = sum(((Z >> i) & 1) != ((Z >> j) & 1) for i, j in EDGES).astype(float)   # cut size of every bitstring


def brute_force():
    best = CUT.max()
    return best, [format(int(z), f"0{N}b") for z in Z[CUT == best]]   # classical optimum: 2**5 checks


def qaoa_state(params):
    """params = [gamma_1..gamma_p, beta_1..beta_p]."""
    p = len(params) // 2
    psi = np.full(2 ** N, 2 ** (-N / 2), dtype=complex)           # H on every qubit
    for gamma, beta in zip(params[:p], params[p:]):
        psi = psi * np.exp(-1j * gamma * CUT)                      # cost layer: phase by cut size (diagonal)
        for q in range(N):
            psi = sv.apply(psi, (sv.rx(2 * beta), q, ()))         # mixer layer: RX(2 beta) on every qubit
    return psi


def cost(params):
    return -float(np.abs(qaoa_state(params)) ** 2 @ CUT)           # minimise -<C>


def ratio(params):
    return round(float(-cost(params) / CUT.max()), 4)                      # approximation ratio <C> / optimum


def optimize(x0, lr=0.05, steps=300, h=1e-4):
    """Plain gradient descent with central differences: fast, but it only finds the NEAREST minimum."""
    x = np.array(x0, dtype=float)
    for _ in range(steps):
        x -= lr * np.array([(cost(x + h * e) - cost(x - h * e)) / (2 * h) for e in np.eye(len(x))])
    return x


def landscape(n_gamma=41, n_beta=21):
    gammas, betas = np.linspace(0, np.pi, n_gamma), np.linspace(0, np.pi / 2, n_beta)
    grid = np.array([[cost([g, b]) for b in betas] for g in gammas])
    i, j = np.unravel_index(grid.argmin(), grid.shape)
    return gammas[i], betas[j], grid


def solve(p, seed=0):
    """Naive: one random start in [0, pi)^(2p), then local descent."""
    x0 = np.random.default_rng(seed).uniform(0, np.pi, 2 * p)
    return optimize(x0)


if __name__ == "__main__":
    best, strings = brute_force()
    print(f"brute force: max cut {best:.0f} by {strings}")
    g, b, grid = landscape()
    print(json.dumps({"p": 1, "method": "grid 41x21", "gamma": round(g, 4), "beta": round(b, 4), "ratio": ratio([g, b])}))
    print(json.dumps({"p": 1, "method": "grid + descent", "ratio": ratio(optimize([g, b]))}))
    x = solve(2, seed=0)                                              # the fault: an unlucky (seeded) start
    print(json.dumps({"p": 2, "method": "random start seed 0", "ratio": ratio(x), "params": np.round(x, 3).tolist()}))
    probs = np.abs(qaoa_state(x)) ** 2
    top = int(probs.argmax())
    print(f"most likely bitstring {format(top, '05b')} (cut {CUT[top]:.0f}), P(any optimal cut) = "
          f"{probs[CUT == best].sum():.4f}")
