"""Theorem 23.3 (Poisson process -> exponential inter-arrival times).
If counts in disjoint intervals are independent and P(one event in [t, t+dt)) = lam dt + o(dt), then
P(T1 > t) = P(N(t) = 0) = exp(-lam t): inter-arrivals are Exponential(lam), memoryless, and N(t) ~ Poisson(lam t).
Check: build the process from its DEFINITION (independent Bernoulli(lam dt) cells), never drawing an exponential."""
import math

import numpy as np

rng = np.random.default_rng(2303)
LAM, DT, CELLS = 2.0, 1e-3, 5_000_000  # 5,000 time units
events = np.flatnonzero(rng.random(CELLS) < LAM * DT)
gaps = np.diff(events) * DT
print(f"events {events.size} in {CELLS * DT:.0f} time units (expected {LAM * CELLS * DT:.0f})")
print(f"mean gap {gaps.mean():.4f} (theory 1/lam = {1 / LAM:.4f}); var {gaps.var():.4f} (theory 1/lam^2 = {1 / LAM**2:.4f})")
for t in (0.25, 0.5, 1.0):
    print(f"P(T > {t}) observed {np.mean(gaps > t):.4f} theory exp(-lam t) = {math.exp(-LAM * t):.4f}")
cond = np.mean(gaps[gaps > 0.5] > 1.5)
print(f"memoryless: P(T > 1.5 | T > 0.5) = {cond:.4f} vs P(T > 1.0) = {np.mean(gaps > 1.0):.4f}")
counts = np.bincount((events * DT).astype(int), minlength=int(CELLS * DT))
print(f"N(1) per unit interval: mean {counts.mean():.4f} var {counts.var():.4f} (Poisson: both = lam = {LAM})")
print(f"P(N(1) = 0) observed {np.mean(counts == 0):.4f} theory {math.exp(-LAM):.4f}")
assert abs(gaps.mean() - 1 / LAM) < 0.01 and abs(np.mean(gaps > 1.0) - math.exp(-LAM)) < 0.005
assert abs(cond - np.mean(gaps > 1.0)) < 0.01 and abs(counts.var() - LAM) < 0.1
