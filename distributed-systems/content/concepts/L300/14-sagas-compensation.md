## Why it matters
Placing an order touches several services that each own their data: orders, payments, shipping. There is no transaction that spans their databases, and two-phase commit across independent teams and vendors is rarely an option. When the third step fails, the first two have already happened. Without a plan, customers pay for parcels that never ship.

## Mental model
A saga is a list of local transactions T1..Tn, each with a compensating action C1..Cn. Either all T's complete, or the completed ones are undone in reverse order: T1, T2, (T3 fails), C2, C1. A compensation is a semantic undo, such as a refund, not a rollback; other readers may have seen the intermediate state.

```
create order --> charge 10 --> ship: FAIL (no courier slot)
                     |
cancel order <-- refund 10 <---+        saga log: ... ship failed, charge compensated, create compensated
```

## How it works
1. **Orchestration.** One component calls each service in order and decides what happens next. The flow lives in one place and is easy to read and test. → see lab step 1
2. **Fault injection.** Shipping refuses some orders (seeded). The lesson orchestrator records the failure and stops, leaving a charge without a shipment. → see lab step 2
3. **Saga log.** Every step is a JSON line: started, done, failed, compensating, compensated. A new orchestrator can rebuild every saga's state from the log alone after a crash. → see lab steps 3 and 6
4. **Compensate in reverse, idempotently.** Undo completed steps newest first. Each compensation must be safe to run twice (one refund per saga id) and safe if its step never ran, because recovery cannot always know. → see lab step 6
5. **Choreography.** No coordinator: each service reacts to an event and emits the next (PaymentCharged, ShippingFailed, PaymentRefunded). Fewer central parts, but the flow is spread across services, and an at-least-once bus delivers duplicates, so every handler must be an idempotent consumer. → see lab step 4

Worked example (lab output, seed 14): with 30% of shipments failing, o1, o5 and o6 fail; the audit reports "o1: FAILED, shipped=False, money kept=10 of 10" and the same for 50 and 60. With compensation, o1's log ends with charge compensated, create compensated and saga compensated, and the audit is clean. If the orchestrator dies right after the refund call, recovery runs the refund again: refunds [-10, -10] with a plain refund, [-10] with an idempotent one.

## Failure modes
- **Missing compensation:** money or stock stays reserved. Seen as audit mismatches, or customer tickets weeks later.
- **Double compensation:** a refund retried after a crash or a duplicated event. Seen as negative balances.
- **Stuck sagas:** a crash between steps with nothing that resumes them. Alert on sagas with no final log entry older than N minutes.
- **Dirty reads:** other code sees the PENDING order or the temporary charge. Sagas give no isolation; use explicit states such as PENDING.
- **A compensation that keeps failing:** retry, then escalate to a person; never drop it.

## Common mistakes
- Putting an irreversible step (shipping, sending an email) before steps that can still fail.
- Logging "done" before the call instead of after, so recovery skips work that never happened.
- Writing compensations as "restore the old value" instead of a semantic undo.
