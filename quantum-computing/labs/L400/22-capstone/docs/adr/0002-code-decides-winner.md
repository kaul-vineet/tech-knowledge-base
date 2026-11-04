# 2. The winner is decided by code under one budget; ties go to the classical baseline

## Status
Accepted (2026-10-28). Guarded by `test_fitness.py::test_code_decides_and_ties_go_classical` and milestone M5.

## Context
Lesson 18 showed how unequal budgets and best-seed reporting fabricate a quantum win, and that under a fair 200-sample
budget QAOA won 1 of 6 twelve-node graphs. The service must answer "which solver should I use for this request?".

## Decision
Every solver, quantum or classical, runs through lesson 18's fair harness with the request's budget and seed list.
`decide()` ranks median ratio, then success rate, then samples to the best cut; a tie goes to the classical solver.
A local model may explain the result; its text is checked and can never change the winner.

## Consequences
- Default request (n = 8, 2000 samples, 5 seeds): all solvers reach the optimum 10; annealing wins on samples (13 vs
  greedy 32 vs QAOA 1013).
- A QAOA win, if it ever appears, is reported with the same evidence a classical win needs.
