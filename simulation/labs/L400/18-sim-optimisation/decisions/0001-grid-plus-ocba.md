# 1. Optimise the (s, Q) policy with grid search plus an OCBA selection stage on fresh common random numbers

## Status
Accepted (2026-10-28)

## Context
We need the cheapest (s, Q) policy among 81 designs (s 10-50, Q 20-100) for the L200 bike-shop inventory model. Each run simulates 180 days. Budget: 324 runs per optimiser. All optimisers use the same common random numbers, and macro-replication m gets stream offset 1000·m. The indifference zone is δ = 0.10/day. Evidence comes from `optimise.py` and `solution/optimise.py`: 5 macro-replications, scored against `truth.json` (100 reps per design on unused streams). Mean / worst gap per day:
- Search only, report the search mean: grid 0.049 / 0.117, GP-lite + EI 0.277 / 1.085, (μ+λ)-ES 0.052 / 0.145. The reported cost was optimistic by 0.30-0.47/day.
- Search (264 runs) + OCBA stage (60 runs, top 5, fresh streams from index 500): grid 0.042 / 0.088, GP-lite + EI 0.090 / 0.186, (μ+λ)-ES 0.088 / 0.241. Over 12 macro-replications the grid's bias fell from -0.394 to -0.143 (truth.json's own standard error is 0.085, shared by all designs).
- With CRN off, the grid + OCBA gap rose to 0.200 / 0.372. Doubling the ES budget gave 0.008, which is an unfair comparison.

## Decision
Use grid search with equal allocation, keep 60 runs in reserve, and finish with OCBA (Fu, Chen & Shi 2008, Figure 3) on fresh common random numbers. Report the fresh-stream estimate.

## Consequences
- An honest cost estimate and a worst gap within δ on this 2-D problem.
- Grid search does not scale: at 5 parameters × 9 levels there are 59,049 designs. Revisit (surrogate or ES + OCBA) when the number of designs exceeds about budget / 3.
- Fitness function: `test_fitness.py` (every method spends ≤ 324 runs; mean gap ≤ 0.06 and worst gap ≤ 0.10 over 5 macro-reps; |bias| ≤ 0.15 over 12).
