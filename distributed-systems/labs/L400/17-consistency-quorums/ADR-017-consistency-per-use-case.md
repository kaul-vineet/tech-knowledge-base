# ADR-017: Pick the consistency setting per use case, from measured evidence

## Status
Accepted (lab 17, 2026-10-28). Fitness function: `test_fitness.py`.

## Context
One replicated key-value store (N = 3: zones A and B in one region, zone C in another) serves three use cases with
different needs. PACELC (Abadi, 2012): during a partition we trade availability against consistency; else we trade
latency against consistency. `python quorum.py` / `solution_quorum.py` measured, seed 17, 10 s simulated:

| Setting | read p99 | write p99 | stale reads | inversions | linearizable | answers with region C down |
|---|---|---|---|---|---|---|
| R=1 W=1 | 60.5 ms | 34.0 ms | 16.74% | 902 | no | 100% |
| R=2 W=2 | 65.9 ms | 68.3 ms | 0% | 2 | no | 100% |
| R=3 W=1 | 135.3 ms | 12.1 ms | 0% | 0 | yes | 0% |
| R=2 W=2 + read write-back | 124.5 ms | 67.5 ms | 0% | 0 | yes | 100% |

R + W > N removed stale reads of finished writes but not new-then-old inversions (2 of ~2,100 reads).

## Decision
- Cart badge: R=1 W=1 (stale counts are acceptable; fastest writes).
- Feature flags: R=2 W=2 (no stale reads, writer sees its own change).
- Lock owner / config: R=2 W=2 **with read write-back** (ABD-style): linearizable and still available with region C down.

## Consequences
- Config reads pay a second round trip when replicas disagree: read p99 65.9 -> 124.5 ms (p50 unchanged, 12.5 -> 12.7 ms).
- During a partition that leaves fewer than 2 replicas reachable, config reads and writes fail (PC/EC); the cart keeps answering (PA/EL).
- `test_fitness.py` fails the build if the config setting stops being linearizable on seeds 11-20, its read p99 exceeds
  150 ms, or it stops answering with region C down. Re-measure when replica placement or the latency budget changes.
