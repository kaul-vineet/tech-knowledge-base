"""tryIt experiments for lesson 10 (run: python try_it.py)."""
import numpy as np

import warmup as wu

# 1. Open EMPTY instead of with 30 tickets (backlog=0). Predict: which way does the no-deletion bias go now?
for backlog in (30, 0):
    m, h = wu.ci([wu.waits(1_000, seed, backlog=backlog).mean() for seed in range(101, 141)])
    print(f"backlog {backlog:2d}, no deletion: {m:.2f} +/- {h:.2f} min (true {wu.TRUE_WQ:.1f})")

# 2. Repeat Welch with three NEW sets of 20 replications. Predict: does the proposed warm-up stay near 169?
props = [wu.warmup_point(wu.welch(np.array([wu.waits(5_000, 1000 * k + s) for s in range(20)]), 50))[0]
         for k in (1, 2, 3)]
print(f"proposed warm-up for three new seed sets: {props}")
runs = [wu.waits(5_000, seed) for seed in range(201, 281)]
for d in (169, max(props)):
    m, h = wu.ci([r[d:].mean() for r in runs])
    print(f"80 replications, delete first {d}: {m:.2f} +/- {h:.2f} min")
