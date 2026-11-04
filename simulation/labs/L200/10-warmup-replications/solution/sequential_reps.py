"""buildTask solution (lesson 10): keep adding replications until the 95% CI half-width is within 5% of the mean.

Sequential rule from Currie & Cheng (WSC 2016, section 5.2), relative error: stop when half / |mean| <= e / (1 + e).
python solution/sequential_reps.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import warmup as wu  # noqa: E402


def reps_for_precision(rel=0.05, warmup=169, m=5_000, start=10, max_reps=400, first_seed=201):
    means = [wu.waits(m, first_seed + i)[warmup:].mean() for i in range(start)]  # pilot replications
    while True:
        mean, half = wu.ci(means)
        if half / abs(mean) <= rel / (1 + rel) or len(means) >= max_reps:
            return len(means), mean, half
        means.append(wu.waits(m, first_seed + len(means))[warmup:].mean())  # one more independent replication


if __name__ == "__main__":
    n, mean, half = reps_for_precision()
    print(f"stopped after {n} replications: {mean:.2f} +/- {half:.2f} min ({100 * half / mean:.1f}% of the mean)")
