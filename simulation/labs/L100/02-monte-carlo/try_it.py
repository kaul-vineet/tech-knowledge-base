"""tryIt experiments for lesson 2 (run: python try_it.py)."""
import numpy as np

import monte_carlo as mc

# 1. Change the seed: small-N answers move, large-N answers agree.
for seed in (42, 7):
    small = mc.summarise(mc.sample_totals(100, seed))
    big = mc.summarise(mc.sample_totals(100_000, seed))
    print(f"seed {seed}: N=100 mean {small[0]:.3f} | N=100000 mean {big[0]:.3f} +/- {big[1]:.3f}")

# 2. Risk change: the 'build' task's worst case grows from 14 to 20 days.
mc.TASKS["build"] = (5, 8, 20)
mean, hw, p = mc.summarise(mc.sample_totals(100_000, 42))
print(f"build max 20 d: mean {mean:.3f} +/- {hw:.3f}, P(<= 20 days) {p:.3f}")

# Bonus: the classic pi estimate with the same recipe.
rng = np.random.default_rng(42)
xy = rng.random((100_000, 2))
inside = (xy ** 2).sum(axis=1) <= 1.0
print(f"pi estimate (N=100000): {4 * inside.mean():.4f} +/- {1.96 * 4 * inside.std(ddof=1) / np.sqrt(len(inside)):.4f}")
