# 2. Scheduler: fidelity floor first, then a queue-time target, then best estimated fidelity

## Status
Accepted (2026-10-30). Guarded by `tests/test_fitness.py::Fitness::test_p95_queue_time_under_budget` and
`tests/test_milestones.py::M2BackendsAndScheduler`.

## Context
Clients state a minimum estimated fidelity (0.75 or 0.85). Backends differ: fast-noisy (4 slots, 1 s per chunk),
slow-clean (2 slots, 3 s, slow tail) and flaky-mid (3 slots, 25% start rejections, a 40 s outage). The p95 queue-time
budget is 30 s. Three policies were run on the same seeded 240-job workload (`python try_it/try_it.py`):

| Policy | p95 queue | mean estimated fidelity | jobs below their floor |
|---|---|---|---|
| best-fidelity (always the cleanest backend) | 1163.38 s | 0.9078 | 0 |
| fastest (lowest wait estimate) | 0.0 s | 0.8522 | 46 |
| floor + 15 s wait target + best fidelity | 18.38 s | 0.8852 | 0 |

## Decision
Filter healthy backends (circuit breaker not open) by the client's fidelity floor; among those whose wait estimate
((queued + running + backing-off chunks) / slots x expected latency) is at most 15 s - half the budget, as headroom
(application-architecture L400 #21) - pick the highest estimated fidelity; otherwise the shortest wait that meets the
floor; if nothing meets the floor, the highest fidelity.

## Consequences
- p95 18.38 s within the 30 s budget, no floor violations, mean estimated fidelity 0.8852 (0.0226 below best-fidelity).
- The wait estimate is a model: slow tails and outages make it optimistic (max queue time observed 38.5 s).
- Fidelity is the cheap product estimate, not a measured fidelity; a drifted calibration changes it at once.
