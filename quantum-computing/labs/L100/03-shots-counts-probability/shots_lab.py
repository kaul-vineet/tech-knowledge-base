"""Lab 03 - shots, counts and probability: why results vary and how a seed makes them repeatable.

Run:  python shots_lab.py
"""
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler   # Qiskit's reference sampler; Aer's SamplerV2 is an equivalent


def coin_circuit():
    """One qubit in equal superposition: ideal P('0') = P('1') = 0.5."""
    qc = QuantumCircuit(1)
    qc.h(0)
    qc.measure_all()
    return qc


def sample(shots, seed=None):
    """Run `shots` repetitions. seed=None -> new random stream each call."""
    sampler = StatevectorSampler(seed=seed)    # seed: replays the same random draws; does not make them more accurate
    result = sampler.run([coin_circuit()], shots=shots).result()   # shot noise: each shot is one random draw
    counts = result[0].data.meas.get_counts()
    return {"0": counts.get("0", 0), "1": counts.get("1", 0)}


def text_histogram(counts, width=40):
    """Tiny terminal histogram: one '#' per (total/width) shots."""
    total = sum(counts.values())
    return "\n".join(f"{k} | {'#' * round(width * v / total):<{width}} {v}" for k, v in sorted(counts.items()))


if __name__ == "__main__":
    for shots in (10, 100, 1000, 10000):
        c = sample(shots, seed=42)
        # estimate = count / shots; its standard error shrinks like 1/sqrt(shots)
        print(f"shots={shots:<6d} counts={c}  estimated P('1')={c['1'] / shots:.3f}")
    print("\nunseeded, run 1:", sample(100))     # these two usually differ
    print("unseeded, run 2:", sample(100))
    print("seeded 2024, run 1:", sample(100, seed=2024))  # these two are identical
    print("seeded 2024, run 2:", sample(100, seed=2024))
    print("\n" + text_histogram(sample(1000, seed=42)))
