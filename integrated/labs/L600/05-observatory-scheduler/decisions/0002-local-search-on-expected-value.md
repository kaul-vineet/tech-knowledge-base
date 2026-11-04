# 2. Local search over request order, maximising expected value

## Status
Accepted (2026-10-30)

## Context
Eleven requests, 64 ten-minute dark slots, seven feasible targets competing for the early evening (Vega and Altair set,
Deneb's window closes) and for the late night (Capella, Aldebaran, Betelgeuse, Sirius). Options measured here:
- Greedy dispatcher (highest priority feasible now): expected value 8.209, plan Deneb, Aldebaran, Capella, Betelgeuse.
- Local search on the request order with an earliest-fit decoder, objective = sum of priority x P(block completes):
  10.534 (Vega, Deneb, Aldebaran, Betelgeuse, Sirius); 3000 moves, about 2 s; the same plan for seeds 1, 2, 3, 2026.
- An exact ILP / CP-SAT model: not used - it needs a solver dependency, and at this size the heuristic already
  reaches a plan we can check; recorded as a scaling path.

## Decision
Use the seeded local search, started from the greedy order (so it can never end below the baseline), with plateau
moves allowed. The objective is the weather-aware expectation, not the nominal sum of priorities.

## Consequences
- Long blocks are honestly penalised: Betelgeuse's 180-min block completes with p = 0.416, a 60-min block with 0.679.
- Fitness FF2 keeps the margin true: >= 15 % over greedy across 1000 weather runs with a paired CI excluding 0.
- No optimality certificate; when constraints tighten (airmass <= 1.5) both methods find the same plan.
