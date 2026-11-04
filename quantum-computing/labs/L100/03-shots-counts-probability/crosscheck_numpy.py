"""Independent numpy cross-check for lab 03 (no quantum SDK needed).

1. Exact probabilities of H|0> from the statevector.
2. Shot noise: sampling N times from those probabilities with a seeded numpy RNG,
   to show the spread shrinks like 1/sqrt(N) and that a seed makes runs identical.
"""
import numpy as np

H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)


def exact_probabilities():
    state = H @ np.array([1, 0], dtype=complex)
    p = np.abs(state) ** 2
    return {"0": round(float(p[0]), 12), "1": round(float(p[1]), 12)}


def sample(shots, seed=None):
    """Classical stand-in for a sampler: draw `shots` outcomes from the exact distribution."""
    rng = np.random.default_rng(seed)
    ones = int(rng.binomial(shots, exact_probabilities()["1"]))
    return {"0": shots - ones, "1": ones}


def standard_error(shots, p=0.5):
    """Expected spread of an estimated probability after `shots` samples."""
    return float(np.sqrt(p * (1 - p) / shots))


if __name__ == "__main__":
    print("exact:", exact_probabilities())
    for shots in (10, 100, 1000, 10000):
        c = sample(shots, seed=42)
        print(f"shots={shots:<6d} counts={c}  P('1')~{c['1'] / shots:.3f}  +/- {standard_error(shots):.3f}")
    print("seed 2024 twice:", sample(100, seed=2024), sample(100, seed=2024))
