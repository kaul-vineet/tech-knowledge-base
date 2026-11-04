# ADR-019: Orders run single-leader with majority-sync replication, leader in eu

## Status
Accepted (lab 19, 2026-10-28). Supersedes "async replication, leader in ap (first launch region)". Fitness function: `test_fitness.py`.

## Context
Order writes come from us (50%), eu (35%) and ap (15%). Brief: us and eu write p99 <= 350 ms, no acknowledged order
may be lost when a whole region fails (RPO = 0), writes must work again within 5 s (RTO), and two regions must
never accept conflicting writes to the same order or stock row. `python solution_multiregion.py` (seed 19, region
failure at t = 10 s; one-way latencies us-eu 40, eu-ap 70, us-ap 110 ms are assumptions) measured:

| Design | write p99 us / eu / ap | RPO (acked writes lost) | RTO | conflicts |
|---|---|---|---|---|
| async, leader ap (deployed) | 346.0 / 265.3 / 102.3 ms | 16 | 1129 ms | 0 |
| async, leader us | 128.0 / 205.3 / 320.3 ms | 17 | 1142 ms | 0 |
| majority-sync, leader us | 310.9 / 354.9 / 445.8 ms | 0 | 1209 ms | 0 |
| majority-sync, leader eu | 304.6 / 267.8 / 341.7 ms | 0 | 1313 ms | 0 |
| multi-leader | 140.6 / 127.1 / 112.8 ms | 2 | 65 ms | 434 |
| leaderless W=2 | 203.9 / 147.1 / 221.9 ms | 0 | 65 ms | 409 |

## Decision
Single leader, majority-sync replication (commit after the first follower ack, Raft-style), leader placed by
`place_leader()` = lowest traffic-weighted write p99 = **eu** (it sits between the two other regions, so its nearest
follower is close for everyone). Catalogue reads may use local followers (bounded staleness, ap p99 lag 103.6 ms).

## Consequences
- us users pay a cross-Atlantic round trip on every write (p99 304.6 ms vs 128.0 ms with async@us): the price of RPO 0.
- A leader-region loss blocks writes for one election (1313 ms here; 73 writes rejected and retried by clients).
- The us p99 is close to the budget (seeds 19-38: max 339.2 ms); a traffic shift towards ap or a heavier latency
  tail breaks it - `test_fitness.py` re-checks the brief on 10 seeds and that eu is still the best-placed leader.
- Carts and likes are not orders: leaderless + CRDT values (lesson 18) fit them (no failover, conflicts merge).
