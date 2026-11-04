# 1. Batched jobs with a structural transpile cache for the variational loop

## Status
Accepted (2026-10-28). Guarded by `test_fitness.py`.

## Context
The optimisation service runs a multi-start SPSA loop: 4 starts × 2 circuits per iteration × 30 iterations = 240 circuits
of ONE parameterised QAOA template. Every job on a shared device waits in a queue (modelled 2 s); a transpile costs 0.5 s.
Measured on the lab's FakeClock (`python solution_cache_key.py`):

| Design | Modelled wall | Billed | Jobs | Transpiles |
|---|---|---|---|---|
| Sync loop (one job per circuit) | 486.8 s | 4.8 s | 240 | 1 |
| Batched (one job per SPSA step) | 66.8 s | 4.8 s | 30 | 1 |
| Session + batches | 11.7 s | 11.7 s (whole window) | 30 | 1 |

With the naive cache key (bound angles in the key) every design transpiles 240 times: batched rises to 186.3 s.
A session needs a plan that allows sessions, bills its whole window, and expires after the interactive TTL:
with a 70 s classical step its billing grows to 2165.3 s with no wall-time gain (`try_it.py`).

## Decision
Use batched jobs as the default execution mode (`DEFAULT_MODE = "batched"`): one job per optimiser step carrying all
circuits of that step. Key the transpile cache on template structure + target + optimisation level, never on parameter
values. Retry transient job failures up to 4 attempts with exponential backoff; per-circuit seeds make retries idempotent.
Offer session mode only as an opt-in for interactive work where wall time matters and the classical step is far below
the interactive TTL.

## Consequences
- 8× fewer jobs than the sync loop and the lowest billed time; results are identical across modes (same seeds).
- The batch size is bounded by the backend's `max_circuits`; larger steps must be chunked (scaling limit).
- Wall time is still dominated by queueing (30 × 2 s); if queues grow, re-evaluate sessions (try 1: 906.8 s vs 39.7 s).
- `test_fitness.py` fails if the default mode changes, jobs exceed iterations, transpiles exceed 1, wall > 90 s or billed > 5 s.
