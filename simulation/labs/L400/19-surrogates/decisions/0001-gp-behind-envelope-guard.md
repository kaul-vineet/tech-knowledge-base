# 1. Answer what-ifs with a GP-lite emulator, but only inside its validity envelope

## Status
Accepted (2026-10-28)

## Context
Planners want instant what-ifs on the clinic queue (the L200 lesson 8 DES; 20,000 patients per run is too slow for interactive use). Training design: 30-run Latin hypercube over λ 1.5-2.4/min and μ 0.95-1.10/min. Holdout: 20 fresh runs. The simulation's own noise against the exact Erlang C answer is 0.033 min. Measured by `surrogate.py`, holdout RMSE / max error:
- quadratic polynomial 0.037 / 0.079 (no uncertainty estimate)
- GP-lite 0.042 / 0.103 (95% intervals cover 85%; length-scales 0.4, 0.4; nugget 0.01)
- random Fourier features 0.049 / 0.133 (0.181 RMSE with 10 runs)
Outside the box all three fail. At λ 2.70, μ 0.95 (exact 6.015) they give 1.930, 0.877 and 0.552, and the GP's standard deviation is only 0.178.

## Decision
Use GP-lite as the emulator. `what_if()` answers from the GP only when the point is inside the training box AND the GP's standard deviation is ≤ 0.10. Otherwise it runs the simulation (4 replications) and labels the answer as such.

## Consequences
- In-box answers take milliseconds. Out-of-box answers take seconds but are honest (6.240 against an exact 6.015).
- The guard is a box. In higher dimensions the convex hull is much smaller than the box, so add a distance-to-nearest-run check before adding inputs.
- Fitness function: `test_fitness.py` (holdout RMSE ≤ 0.06, coverage ≥ 80%, in-box what-ifs within 10% of Erlang C, no out-of-box answer from the surrogate).
