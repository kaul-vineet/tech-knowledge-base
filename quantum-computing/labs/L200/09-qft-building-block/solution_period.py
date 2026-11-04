"""Build-task solution for lab 09: use the QFT to read the period of a periodic state.

Run: python solution_period.py
A state with period r over N = 2**n basis states turns into peaks at multiples of N/r after the QFT,
so the spacing of the peaks gives r. The numpy part runs anywhere; period_qiskit needs qiskit.
"""
import math
import sys
from pathlib import Path

import numpy as np

import crosscheck_numpy as cc

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from qsim import statevector as sv  # noqa: E402


def periodic_state(n, period, offset=0):
    """Equal superposition of |offset>, |offset + period>, ... (period must divide 2**n)."""
    v = np.zeros(2 ** n, dtype=complex)
    v[offset::period] = 1
    return v / np.linalg.norm(v)


def period_from_probs(probs, n):
    peaks = [int(k, 2) for k, p in probs.items() if p > 1e-9]
    spacing = math.gcd(2 ** n, *peaks)                      # peaks sit at multiples of N/r
    return 2 ** n // spacing


def period_numpy(n, period, offset=0):
    probs = sv.probabilities(sv.run(n, cc.qft_ops(n), periodic_state(n, period, offset)))
    return period_from_probs(probs, n), probs


def period_qiskit(n, period, offset=0):
    from qiskit.quantum_info import Statevector

    import qft_lab
    state = Statevector(periodic_state(n, period, offset)).evolve(qft_lab.qft_circuit(n))
    probs = {k: float(v) for k, v in state.probabilities_dict().items()}
    return period_from_probs(probs, n), probs


if __name__ == "__main__":
    for period, offset in ((2, 0), (2, 1), (4, 0), (4, 3)):
        found, probs = period_numpy(3, period, offset)
        print(f"period {period} offset {offset}: QFT probabilities {probs} -> period {found}")
