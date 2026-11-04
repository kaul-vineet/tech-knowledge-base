"""tryIt experiments for lesson 11 (run: python try_it.py)."""
import numpy as np

import nbody as nb

# 1. Make the time step 10x larger. Predict: which integrator suffers more?
for dt in (0.001, 0.01):
    for name, step in (("Euler", nb.step_euler), ("leapfrog", nb.step_leapfrog)):
        pos, _, drift, _ = nb.run(step, years=12.0, dt=dt)
        print(f"dt={dt:<6} {name:<8}: |dE/E| = {drift:.2e}, Earth-Sun {np.linalg.norm(pos[1] - pos[0]):.4f} au")

# 2. Run forward 1 year, then backward 1 year. Predict: back where Earth started?
for name, step in (("Euler", nb.step_euler), ("leapfrog", nb.step_leapfrog)):
    pos, vel = nb.initial_state()
    p, v = pos, vel
    for dt in [0.001] * 1000 + [-0.001] * 1000:
        p, v = step(p, v, nb.MASSES, dt)
    print(f"{name:<8}: Earth ends {np.linalg.norm(p[1] - pos[1]):.2e} au from its start")
