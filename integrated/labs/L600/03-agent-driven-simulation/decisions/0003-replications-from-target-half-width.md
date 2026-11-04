# ADR 0003: Replications come from a target CI half-width, inside the budget, never from the agent

## Status
Accepted (2026-10-30)

## Context
The question is whether faster service (mu 1.0 → 1.05 at lam 0.8) cuts the mean wait. Decision makers care about differences of about 0.3 min or more. The agent asked for 3 replications. Measured (seed 13, independent streams, Welch CI):
- 3 replications: 4.28 vs 2.58 min (-40%). The 95% CI of the difference runs from -3.436 to 0.019, and the two arms' CIs overlap. Each arm's CI uses t(0.975, df 2) = 4.303. `warmup.t975` would give 3.85, which is too narrow.
- Sequential rule (pilot 10, then n·(half-width/target)²): 3 → 10 → 47 → 55. Result: 4.04 vs 3.14 min (-22%), difference -0.895 ± 0.293. That is a significant decrease. The M/M/1 steady-state difference, -0.952, lies inside the CI.
- Cost: 220,000 customers of the 300,000 session budget. Target ±0.2 needs 105 replications, which does not fit. The pipeline stops at 10 and reports `budget_limited: true` instead of overspending (`try_it/tighter_target.py`).
- Common random numbers (paired, `try_it/crn.py`): 10 replications give ±0.266. The two arms' correlation is 0.963.

## Decision
The pipeline computes n with `solution/replications.py`: at least N0 = 10 pilot replications, then n = ⌈n·(h/target)²⌉ repeated until it is met (at most 6 rounds). Each extension reserves its cost first. If it does not fit, the pipeline stops with `budget_limited`. "Significant" requires n ≥ 10 and a 95% Welch CI of the difference that excludes 0. The agent's `replications` value is only a floor.

## Consequences
- Conclusions cost what the noise demands (55 per arm here), not what the agent guessed.
- With seed 13, the 3-replication point estimate overstated the gain (-40% vs -22%). Small samples err in magnitude as well as in significance.
- CRN would cut the cost by about 5×, but it needs a paired analysis. We keep independent streams as the default because they make every arm's runs re-usable in other comparisons. CRN is a documented upgrade (tryIt 1).
- Fitness functions: `tests/test_seam_replications.py`, `tests/test_failure_lab.py`, `tests/test_build_task.py`.
