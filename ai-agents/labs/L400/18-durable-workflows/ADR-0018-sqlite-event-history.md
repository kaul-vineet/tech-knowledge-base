# ADR-0018: Durable refund workflow on an SQLite event history; Temporal when we outgrow one process

## Status
Accepted (2026-10-28). Kept true by `test_fitness_crash_sweep.py`.

## Context
A refund workflow calls a model, waits hours or days for a human, moves money and notifies the customer. Processes get killed. We swept 12 crash points (before/after each of 5 steps, after the model answered, after the payment API answered) with `harness.sweep()`:

| Variant | Crash points with a duplicate refund | Points that re-asked the model |
|---|---|---|
| In-memory loop, no keys (`naive_workflow.py`) | 4 of 12 | 9 of 12 |
| SQLite checkpoints, no Idempotency-Key | 1 of 12 (after the payment answered) | 1 |
| SQLite checkpoints + key `"<workflow>:refund"` + outbox row in the checkpoint transaction | 0 of 12 | 1 |

SQLite commits are atomic even across a crash or power loss (sqlite.org "Atomic Commit"). Temporal gives the same guarantee as a service: activity results are recorded in an event history and reused on replay (docs.temporal.io).

## Decision
We will record every step result in an SQLite `history` table, one transaction per step, and replay it on restart. External effects carry an Idempotency-Key derived from the workflow id and step. Local effects (the notification) are written in the same transaction as the checkpoint (outbox). Approvals are signals stored in the history, with a deadline (build task). When we need several workers, cross-host scheduling or a UI for histories, we will move the same steps to Temporal (`temporal_equivalent.py`).

## Consequences
- A crash between the model's answer and its checkpoint repeats one model call: tokens, not money.
- The external API must honour Idempotency-Key; an API without it needs a reconciliation step.
- One SQLite file means one writer process; this is the scaling limit that would trigger the Temporal move.
