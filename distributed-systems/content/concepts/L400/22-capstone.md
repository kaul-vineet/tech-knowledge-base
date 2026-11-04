## Overview
The capstone is one order pipeline that uses almost every mechanism in this topic at once, then attacks itself and proves, with code, that customers were not harmed. It runs on simulated ticks with seeded faults, so every run is identical and every claim is a test. Deterministic checks decide pass/fail; a local model may explain the results, and code checks each claim it makes.

## Architecture walkthrough
```
client --key, traceparent--> gateway (bounded queue, 503 + Retry-After) --> workers
   --> saga orchestrator: create -> charge -> ship | compensate in reverse | recover()
   --> per service: state change + event in ONE outbox transaction
   --> relay (publish, then mark sent) --> at-least-once bus --> idempotent consumers
gateway bound <-- committed config <-- Raft (3 replicas) <-- operator, versioned, retried
```
1. **Admission**: the gateway queue is bounded; when full it sheds with 503 and Retry-After. Clients retry with jitter and keep the order's idempotency key, so a retry after a lost acknowledgement never creates a second order.
2. **Workflow**: the orchestrated saga charges before it ships and compensates in reverse on failure; after a crash, `recover()` finishes every saga from its log and compensates the in-doubt step.
3. **Events**: each step writes its state change and its event together (outbox). An event is written only if the state really changed, so a re-run idempotent refund does not publish a second "refunded". The relay is at-least-once; consumers record processed event ids with their effect.
4. **Observability**: a W3C trace starts at the client, and each step's span id travels inside the event, so consumer spans join the same trace.
5. **Configuration**: the queue bound is a versioned entry committed through Raft; the pipeline applies only committed, newer versions.
6. **Proof**: a campaign runs nine experiments (each fault alone, then all at once) on three seeds; order-level faults hit a stable 10% cohort. `run_capstone.py` prints a JSON-lines scorecard of ten criteria.

Real run: all 27 experiments held; the scorecard reads 10/10. Consumers absorbed 586 duplicate deliveries without a second email or booking. The fake model's explanation contained two wrong claims (relay-crash "not held", 3 harmed orders in the burst) and a release verdict; code flagged both claims and ignored the verdict. While building, the leader-crash experiment failed "config via Raft" because the run ended before the re-proposed change committed; waiting for the commit fixed it.

## How it ties L100-L400
- **L100**: timeouts and retries with jitter (client retries), idempotency keys (one order per key).
- **L200**: at-least-once delivery and idempotent consumers; rate limiting's Retry-After.
- **L300**: Raft with the election restriction (config), partitions and checkers, sagas with recovery, trace propagation, bounded queues.
- **L400**: consistency per use case (config is linearizable and versioned; emails are effectively-once), CRDT thinking for merges, multi-region trade-offs in the ADRs, bounded chaos with control groups, and invariants checked by code over the system's own data.

Each ADR in `adr/` records one decision with the numbers that justified it; each scorecard criterion is the fitness function that keeps it true.
