# 1. Gate every workload on a resource estimate with an error-budget-derived code distance

## Status
Accepted (2026-10-28). Guarded by `test_fitness.py`.

## Context
The optimisation service must say, before running anything, whether a request can be simulated, tried on a noisy
device, or would need a fault-tolerant machine that does not exist yet. The shipped estimator used one fixed code
distance (d = 3, "17 physical qubits per logical qubit"): it reported RSA-2048 as fault-tolerant-feasible with 111,420
physical qubits and 1.8 h, while its own logical failure probability was 1.0.
With d chosen from a 1 % failure budget (`solution_distance.py`; p = 1e-3, 1 µs cycles, data blocks only):

| Workload | Logical qubits | T-count | d | Physical (lower bound) | Runtime | Class |
|---|---|---|---|---|---|---|
| QAOA n=20 p=1 | 20 | 2,350 | 9 | 3,240 | 2.2 ms | simulate |
| QAOA n=100 p=1 | 100 | 13,500 | 9 | 16,200 | 2.6 ms | nisq-candidate |
| QAOA n=100 p=4 | 100 | 60,000 | 11 | 24,200 | 13.8 ms | fault-tolerant-feasible |
| QAOA n=1000 p=10 | 1000 | 1,850,000 | 15 | 450,000 | 57 ms | fault-tolerant-feasible |
| RSA-1024 | 3,093 | 2.29e9 | 25 | 3,866,250 | 3.7 h | infeasible |
| RSA-2048 | 6,190 | 1.84e10 | 27 | 9,025,020 | 16.1 h | infeasible |

For context: Gidney & Ekerå (2019) estimated 20 million noisy qubits and 8 hours for RSA-2048 including factories and
routing; Gidney (2025) estimated under a million qubits and under a week with newer techniques. Our data-only model sits
between them in qubits, so it is a planning bound, not a forecast.

## Decision
Every request gets a resource estimate first. The code distance is the smallest odd d meeting the failure budget;
above the 1 % threshold the estimator refuses. Thresholds: simulate if ≤ 30 logical qubits; NISQ candidate if
(1 − 1e-3)^CX ≥ 0.5; fault-tolerant-feasible if ≤ 1,000,000 physical qubits and ≤ 1 day; otherwise infeasible.
The Microsoft QDK resource estimator (`estimate_qdk.py`) is the cross-check in CI because it models factories.

## Consequences
- No estimate can claim feasibility with a failure probability above the budget (fitness test).
- The model omits magic-state factories, routing and decoding: real counts are higher; QDK in CI shows how much.
- Thresholds are policy, not physics; changing them changes the pinned decision table and needs a new ADR.
