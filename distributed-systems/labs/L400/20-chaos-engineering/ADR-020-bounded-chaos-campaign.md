# ADR-020: Chaos experiments run as a bounded, automated campaign: 10% cohort, control group, abort on first harm

## Status
Accepted (lab 20, 2026-10-28). Fitness function: `test_fitness.py`.

## Context
We want evidence that the order saga (L300 #14) and the replicated log (L300 #12) survive real-world faults
(courier API outage, orchestrator crash, node crashes, a fast rolling restart). An experiment that refutes its
hypothesis has, by definition, hurt someone. Options measured with `chaos.py` / `solution_chaos.py`, seed 14, 60 orders:

| Option | Evidence | Verdict |
|---|---|---|
| Fault every order, no control group, no abort (lesson harness) | shipping outage vs the L300 lesson saga: 60 customers hurt (paid, not shipped, not refunded) | reject |
| Bounded: 10% stable cohort, rest = control group, abort after 1 harmed order | same finding (hypothesis refuted), 1 customer hurt, control group 0 harmed | adopt |
| Manual game days only | finds what people think of; random node crashes found nothing in 20/20 Raft runs, a 0-4 tick rolling restart found the lost-commit bug in 1/20 | keep as a complement, not the gate |

## Decision
Every experiment names its steady-state metric (harmed orders = 0; Raft: lost committed entries = 0, no-leader gap
<= 40 ticks) and a hypothesis, injects faults into a stable 10% cohort only, compares with the control group, and
stops injecting after the first harmed order. Raft faults touch one node at a time (a minority). The campaign runs
seeded in CI against the hardened services; findings go to the owning team before any wider run.

## Consequences
- Small cohorts need more runs to find rare weaknesses (the rolling-restart bug shows in 1 of 20 seeds).
- A fixed abort threshold of 1 suits money-moving flows; read-only flows can use a larger cohort.
- `test_fitness.py` fails the build if an experiment exceeds the 10% blast radius or hurts more than one customer,
  or if the hardened saga/Raft stop holding any hypothesis on seeds 14-16.
