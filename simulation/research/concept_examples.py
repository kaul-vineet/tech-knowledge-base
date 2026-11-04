"""Computes every number quoted in content/concepts/*.md and documentation/CONCEPTS-PRIMER.md.

python research/concept_examples.py   (from the simulation/ folder; ~15 s)
"""
import math
import sys
from pathlib import Path

LABS = Path(__file__).resolve().parent.parent / "labs/L100"
for lab in ("02-monte-carlo", "03-discrete-event-queue", "04-time-stepped-physics", "05-agent-based-schelling", "06-verification-validation"):
    sys.path.insert(0, str(LABS / lab))

import numpy as np  # noqa: E402

import des_queue  # noqa: E402
import falling  # noqa: E402
import monte_carlo  # noqa: E402
import schelling  # noqa: E402
import vv  # noqa: E402

print("01 default_rng(42) first 3:", np.random.default_rng(42).random(3).round(6).tolist())

print("02 exact mean:", round(monte_carlo.exact_mean(), 3), "| sum of modes:", sum(m for _, m, _ in monte_carlo.TASKS.values()))
for n in (100, 1_000, 10_000, 100_000):
    m, hw, p = monte_carlo.summarise(monte_carlo.sample_totals(n, 42))
    print(f"   N={n}: mean {m:.3f} half-width {hw:.3f} P(<=20) {p:.3f}")
print("   P50/P90:", np.round(np.percentile(monte_carlo.sample_totals(100_000, 42), [50, 90]), 2).tolist())

waits, _ = des_queue.simulate(200_000, 1)
print(f"03 Wq formula {des_queue.mm1_wq():.3f} | simulated {sum(waits) / len(waits):.3f} | lam 0.88 formula {des_queue.mm1_wq(0.88):.2f}")

print(f"04 exact height at 3 s {falling.H0 - 0.5 * falling.G * 9:.1f} m | Euler global error g*dt*t/2: dt=0.1 -> {falling.G * 0.1 * 3 / 2:.3f}, dt=0.01 -> {falling.G * 0.01 * 3 / 2:.4f}")
print(f"   terminal velocity {falling.terminal_velocity():.2f} m/s | impact {abs(falling.time_to_ground(falling.step_rk4, 0.001, True)[1]):.2f} m/s")

_, h = schelling.run(seed=42)
print(f"05 % similar {h[0][0]:.1f} -> {h[-1][0]:.1f} in {len(h) - 1} steps | seeds 1-5:", [round(float(schelling.run(seed=k)[1][-1][0]), 1) for k in range(1, 6)])

print("06 next_wait(0,3,1) =", vv.next_wait(0, 3, 1), "| next_wait(2,1,5) =", vv.next_wait(2, 1, 5))
m, half = vv.replicate(0.8)
print(f"   replications lam=0.8: {m:.3f} +/- {half:.3f} (formula {vv.formula(0.8):.3f}) | formula lam 0.5 / 0.9: {vv.formula(0.5):.1f} / {vv.formula(0.9):.1f}")
print("   t(0.975, 9) used:", vv.T_975[9], "| 1.96 normal quantile check:", round(math.erf(1.96 / math.sqrt(2)), 4))
