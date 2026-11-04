"""tryIt experiments for lesson 10 (run: python try_it.py)."""
import numpy as np

import periods as pr

# 1. Observe around the clock (e.g. three sites or a satellite) instead of one site. Predict: what happens to the alias?
t1 = pr.sample_times()
t3 = np.sort(np.random.default_rng(1).uniform(0, 30, t1.size))  # same number of points, no daily gaps
for name, t in (("one site", t1), ("no daily gaps", t3)):
    f = pr.frequency_grid(t)
    p = pr.lomb_scargle(t, pr.variable_star(t), f)
    alias = p[np.argmin(np.abs(f - (1 / pr.P_VAR - 1)))]
    print(f"{name:<14}: peak power {p.max():.3f}, power at the 1-day alias {alias:.3f}")

# 2. Fewer nights. Predict: how does period precision change with 8 vs 30 nights?
for nights in (8, 30):
    t = pr.sample_times(nights=nights)
    r = pr.analyse(t, pr.variable_star(t))
    print(f"{nights} nights: best period {r['best_period_days']:.4f} d (true {pr.P_VAR}), error {abs(r['best_period_days'] - pr.P_VAR) * 86400:.0f} s")
