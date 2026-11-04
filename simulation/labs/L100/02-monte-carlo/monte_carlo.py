"""L100 Monte Carlo: how long will a 3-task release take, and how sure are we?

Tasks run one after another; each duration is uncertain (triangular: min, most likely, max days).
We sample many possible projects, then report the mean, a 95% confidence interval and P(done <= 20 days).

python monte_carlo.py
"""
import numpy as np

TASKS = {"design": (2, 4, 8), "build": (5, 8, 14), "test": (2, 3, 6)}  # (min, mode, max) days
DEADLINE = 20.0


def sample_totals(n, seed):
    rng = np.random.default_rng(seed)  # seeded generator: same seed -> same samples -> same answer
    totals = np.zeros(n)
    for low, mode, high in TASKS.values():
        totals += rng.triangular(low, mode, high, size=n)  # random sampling of each uncertain input
    return totals


def summarise(totals):
    n = len(totals)
    mean = totals.mean()
    half_width = 1.96 * totals.std(ddof=1) / np.sqrt(n)  # 95% CI half-width shrinks like 1/sqrt(N)
    return mean, half_width, (totals <= DEADLINE).mean()


def exact_mean():
    return sum((a + b + c) / 3 for a, b, c in TASKS.values())  # mean of a triangular = (min+mode+max)/3


def main(seed=42):
    print(f"exact mean (from formula): {exact_mean():.3f} days")
    print("       N    mean   95% CI half-width   P(<= 20 days)")
    for n in (100, 1_000, 10_000, 100_000):  # convergence: 100x more samples -> ~10x narrower CI
        mean, hw, p = summarise(sample_totals(n, seed))
        print(f"{n:>8} {mean:7.3f}   +/- {hw:.3f}            {p:.3f}")
    totals = sample_totals(100_000, seed)
    print("P50 / P90 completion (days):", np.round(np.percentile(totals, [50, 90]), 2))


if __name__ == "__main__":
    main()
