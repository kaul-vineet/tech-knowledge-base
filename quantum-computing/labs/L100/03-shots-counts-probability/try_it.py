"""Try-it checks for lab 03. Run: python try_it.py

numpy stands in for the sampler locally; the SDK part runs only when qiskit is installed (CI).
Exact counts differ between numpy and StatevectorSampler (different RNGs); the properties checked are the same.
"""
import importlib.util

import crosscheck_numpy as cc

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None


def try1_numpy(shots=2500, seed=42):
    """Try 1: 2500 shots -> standard error 0.01; count of '1' should land within ~2 SE of 1250."""
    c = cc.sample(shots, seed=seed)
    return c, cc.standard_error(shots)


def try2_numpy():
    """Try 2: change the second seeded run from seed 2024 to 2025."""
    return cc.sample(100, seed=2024), cc.sample(100, seed=2025)


if __name__ == "__main__":
    c, se = try1_numpy()
    print(f"try 1  numpy shots=2500 counts={c}  P('1')~{c['1'] / 2500:.4f}  standard error={se:.3f}")
    a, b = try2_numpy()
    print(f"try 2  numpy seed 2024 {a}  seed 2025 {b}  identical={a == b}")
    if HAVE_QISKIT:
        import shots_lab
        c = shots_lab.sample(2500, seed=42)
        print(f"try 1  SDK   shots=2500 counts={c}  P('1')~{c['1'] / 2500:.4f}")
        a, b = shots_lab.sample(100, seed=2024), shots_lab.sample(100, seed=2025)
        print(f"try 2  SDK   seed 2024 {a}  seed 2025 {b}  identical={a == b}")
