# 1. Compare solvers at an equal sample budget over fixed seeds, and default to the classical baseline

## Status
Accepted (2026-10-28). Guarded by `test_fitness.py`.

## Context
We must decide whether the optimisation service should offer QAOA for MaxCut and when. One "sample" is one candidate
bitstring evaluated (a classical flip evaluation or one quantum shot). The shipped `bench_lab.compare()` gave QAOA 4× the
budget and its best of 10 seeds while the baselines ran once at a quarter budget; it reported "QAOA wins" at n = 12.
The fair harness (`solution_fair.py`: same 200-sample budget, the same 10 seeds, medians, `used <= budget` enforced)
measured on 3-regular graphs:

| n | greedy median / success | annealing | QAOA p=1 (noiseless simulator) | code's winner |
|---|---|---|---|---|
| 8 | 1.0 / 1.0 | 1.0 / 1.0 | 1.0 / 1.0 | annealing (fewest samples) |
| 12 | 0.9333 / 0.4 | 0.9333 / 0.3 | 0.9667 / 0.5 | qaoa |
| 16 | 1.0 / 0.9 | 1.0 / 0.8 | 1.0 / 0.6 | greedy |

On five other 12-node graphs QAOA won 1 of 5 (`try_it.py`). Exact enumeration of n = 12 needs only 4096 evaluations.
QAOA's simulator time grows as 2^n (1.69 s per run at n = 16 vs 0.001 s for greedy).

## Decision
All solver comparisons go through the fair harness: one budget, one seed list (≥ 10 seeds), medians and success rates,
and a `BudgetViolation` for any run that over-spends. The winner is chosen by code: median ratio, then success rate,
then samples to the best cut; ties go to the classical baseline. For n ≤ 20, the service solves exactly; QAOA stays a
research option until it wins on more than single instances, under noise, and on wall time including queueing.

## Consequences
- Benchmark claims become reproducible and comparable; a cherry-picked configuration fails the fitness test.
- A sample budget ignores wall time and noise; both are added in the capstone (lessons 12, 13, 17).
- 10 seeds still give wide intervals (success 0.3 vs 0.5 is not significant); more seeds cost linear time.
