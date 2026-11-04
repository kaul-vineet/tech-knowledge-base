# 1. Idempotent chunk attempts with per-attempt fencing tokens

## Status
Accepted (2026-10-30). Guarded by `tests/test_fitness.py::Fitness::test_exact_shots_for_every_job_under_injected_failures`
and `tests/test_failure_lab.py`.

## Context
A job's shots are split into 1000-shot chunks. A worker holds a 10 s lease per chunk attempt; when the lease runs out
the chunk is redelivered (at-least-once, distributed-systems L200 #8). The slow-clean backend runs 15% of chunks 5x
longer (15 s), so the original attempt is still running when the redelivery starts. Both report. The shipped ledger
merges every report: in the seeded load test 14 of 240 jobs returned more shots than requested (604,000 vs 590,000),
and the 2-chunk failure-lab job returned 4000 of 2000 shots. Error bars computed from the inflated N are too narrow.

## Decision
- Each chunk attempt is granted a lease with a fencing token from one counter that only grows (L200 #7).
- Each chunk's result slot is a `FencedStorage` (reused from L200 #7): a write replaces the value; a write with a token
  lower than the highest seen is rejected. One chunk therefore contributes exactly its shots.
- Chunk seeds depend on (request seed, chunk index, calibration version) - never on the attempt - so duplicate attempts
  produce identical counts and it does not matter which one wins (quantum L400 #17).
- Retries are per chunk: a transient rejection re-runs only the failed chunk.

## Consequences
- Shot totals are exact for 240/240 jobs with 15 lease expiries, 4 breaker openings and 405 attempts in the load test.
- Duplicate executions still cost backend time (2 rejected commits in the load test): fencing fixes correctness, not
  waste. Lease renewal (heartbeats) would cut the waste; with a 20 s lease the run had 0 expiries (try_it) but a lost
  attempt would wait 20 s before redelivery.
- Tokens must come from one monotonic source; two coordinators with separate counters would break the guarantee.
