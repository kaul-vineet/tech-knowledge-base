"""Lab 12 - noise models: how a Bell / GHZ result degrades, and why an exact-outcome test breaks.

Run:  python noise_lab.py            (numpy only: density-matrix simulator in labs/_shared/qsim)
SDK path (same model in Qiskit Aer): python noise_aer.py   (needs qiskit + qiskit-aer, runs in CI)
Prints JSON lines (one per noise level) so you can grep, plot or diff them.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from qsim import density as dm  # noqa: E402
from qsim import statevector as sv  # noqa: E402

# Seeded "device": depolarizing after 1q gates (p1) and CX (p2), amplitude damping after every gate,
# readout flips p01 = P(read 1 | was 0), p10 = P(read 0 | was 1). Values are illustrative, not a real device.
NOISE = {"p1": 0.002, "p2": 0.02, "damp": 0.01, "p01": 0.02, "p10": 0.04}
IDEAL = {k: 0.0 for k in NOISE}


def ghz_ops(n):
    return [sv.h(0)] + [sv.cx(i, i + 1) for i in range(n - 1)]   # n = 2 is the Bell pair


def noisy_steps(ops, noise):
    """Insert a channel after every gate: this is what a noise model 'attached to gate names' does."""
    steps = []
    for op in ops:
        qubits = tuple(op[2]) + (op[1],)                            # controls..., target
        steps.append(op)
        steps.append(("depol", noise["p2"] if len(qubits) == 2 else noise["p1"], qubits))
        steps += [("damp", noise["damp"], q) for q in qubits]       # T1-like decay toward |0>
    return steps


def measured_probabilities(n, noise):
    rho = dm.run(n, noisy_steps(ghz_ops(n), noise))
    readout = dm.readout_matrix(noise["p01"], noise["p10"], n)    # classical flips at measurement
    return rho, readout @ dm.probabilities(rho)


def metrics(n, noise):
    rho, probs = measured_probabilities(n, noise)
    ideal = sv.run(n, ghz_ops(n))
    return {"n": n, "p2": noise["p2"], "fidelity": round(dm.fidelity(rho, ideal), 4),
            "success": round(float(probs[0] + probs[-1]), 4),       # P(all 0) + P(all 1)
            "p_all0": round(float(probs[0]), 4), "p_all1": round(float(probs[-1]), 4)}


def counts(n, noise, shots=2000, seed=7):
    return dm.sample(measured_probabilities(n, noise)[1], shots, np.random.default_rng(seed))


def bell_check(counts, n=2, shots=None, noise=None):
    """Naive regression test from L100: only all-0 / all-1 may appear. Correct for an ideal simulator."""
    return set(counts) <= {"0" * n, "1" * n}


if __name__ == "__main__":
    print("ideal Bell counts:", counts(2, IDEAL))
    noisy = counts(2, NOISE)
    print("noisy Bell counts:", noisy)
    for n in (2, 3, 4):                                             # observability: one JSON line per run
        for p2 in (0.0, 0.01, 0.02, 0.05, 0.1):
            print(json.dumps(metrics(n, {**NOISE, "p2": p2})))
    print("naive bell_check on ideal counts:", bell_check(counts(2, IDEAL)))
    print("naive bell_check on noisy counts:", bell_check(noisy), "<- the fault: a correct circuit fails")
