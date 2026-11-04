# ADR-022-1: Outbox + idempotent consumers instead of a distributed transaction

## Status
Accepted (capstone, 2026-10-28). Fitness functions: "outbox delivered", "exactly-once effects" in `run_capstone.py`.

## Context
Each service must change its own data and tell others about it. Writing to the database and publishing to the bus
are two systems: a crash between them loses or invents an event. Two-phase commit across the database and the bus
is not available here and would block on the coordinator (L300 #14 trade-offs).

## Decision
Every saga step and compensation writes its state change and its event in one local transaction (`OutboxDB.transact`);
an event is written only if the state actually changed. A relay publishes unsent rows and then marks them sent
(at-least-once). Consumers record processed event ids together with their effect (`IdempotentConsumer`).

## Consequences
- Duplicates are normal: the campaign's consumers absorbed 586 duplicate deliveries across 27 runs; effects stayed
  exactly once (tryIt 1: without dedupe, 2 emails per event and 14 revenue mismatches).
- Events are delayed until the relay's next tick; consumers must tolerate lag.
- Every new consumer must be idempotent; `test_m1_outbox.py` and the scorecard keep that true.
