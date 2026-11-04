# 1. Staff each hour from an Erlang C seed, decided by simulation with 95% bounds and repaired on full days

## Status
Accepted (2026-10-28)

## Context
The service level agreement (SLA) is at least 80% of calls answered within 1 minute and at most 5% abandoned, in every hour from 08:00 to 20:00, with as few agent-hours as possible. Handle times are lognormal (cv 0.80) and callers abandon (patience calibrated to 4.5 min). Erlang C ignores both. Measured (`try_it.py`, `run_capstone.py`; full days, 24 replications):
- Flat staffing at the peak need: 300 agent-hours.
- Erlang C per hour: 219 agent-hours. The full day meets the SLA on means (worst-hour abandonment 3.6%), but 2 hours (09:00, 14:00) fail the 95% upper bound on abandonment.
- Simulation, point estimates: 208 agent-hours. The worst hour abandoned 6.4% of calls (it fails).
- Simulation from the Erlang C seed, 95% bounds per hour, full-day repair: 221 agent-hours. The worst hour abandoned 3.6% and every hour's SL lower bound is ≥ 0.872.

## Decision
Use the last option. Start at Erlang C, add agents until the hour passes with 95% bounds (10 CRN replications), remove agents while it still passes, then add one agent to any hour that misses on a full-day simulation (queues carry over).

## Consequences
- +2 agent-hours over Erlang C buys a verified, stated confidence on both constraints, and works when Erlang C's assumptions do not hold (surge re-plan).
- Costs about 120 period simulations per plan. Fine for a daily plan; the surrogate of lesson 19 is the next step if re-plans must be instant.
- Fitness function: `test_fitness.py::test_sla_holds_for_the_recommended_plan`.
