"""tryIt experiments for lesson 9 (run: python try_it.py)."""
from functools import partial

import numpy as np

import adaptive_ode as ode

# 1. Loosen the tolerance on rabbits/foxes. Predict: fewer steps - but what happens to the conserved quantity?
v = lambda z: z[0] - 3 * np.log(z[0]) + z[1] - 1.5 * np.log(z[1])
for rtol in (1e-3, 1e-6, 1e-9):
    ts, ys, _ = ode.solve(ode.lotka_volterra, 0, [10.0, 5.0], 15, rtol=rtol)
    print(f"rabbits/foxes rtol={rtol:.0e}: {len(ts) - 1:4d} steps, invariant drift {abs(v(ys[-1]) - v(ys[0])):.1e}")

# 2. Make the RC filter 10x stiffer (tau 1 ms -> 0.1 ms). Predict the explicit solver's step count.
for tau in (1e-3, 1e-4):
    ts, ys, _ = ode.solve(partial(ode.rc_filter, tau=tau), 0, [0.0], 10, rtol=1e-3, atol=1e-9)
    print(f"RC tau={tau:.0e} s: explicit RK45 {len(ts) - 1:6d} steps, v(10)={ys[-1, 0]:.5f}")
