# ADR-022-4: Shed load at admission with 503 + Retry-After, and make client retries idempotent

## Status
Accepted (capstone, 2026-10-28; reuses L300 #16's bounded admission). Fitness functions: "bounded queue", "one order
and one charge per key".

## Context
A flash sale (20 extra orders in one tick) or lost responses make clients send more than the workers can take. An
unbounded queue turns that into long waits for everyone (L300 #16); blind retries create second orders.

## Decision
The gateway queue is bounded by the committed `max_queue`; when full it answers 503 with Retry-After and the client
retries with jitter. Every order carries an idempotency key; the gateway answers a repeated key from what it already
accepted.

## Consequences
- In the burst runs the bound was reached and p99 queue wait stayed within 6 ticks; no order was lost.
- Without the idempotency check, lost acknowledgements created second orders (tryIt 2: max created 2).
- Clients must implement Retry-After and keep the key across retries.
