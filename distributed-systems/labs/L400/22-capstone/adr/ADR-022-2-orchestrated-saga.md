# ADR-022-2: An orchestrated saga with a saga log and recover()

## Status
Accepted (capstone, 2026-10-28; reuses L300 #14's hardened orchestrator). Fitness functions: "money invariant",
"no lost orders".

## Context
An order spans orders, payments and shipping. Shipping can fail after the card was charged, and the orchestrator
process can die mid-saga. Choreography spreads the flow over handlers; orchestration keeps it in one place.

## Decision
One orchestrator runs create -> charge -> ship, logs every step, compensates completed steps in reverse order on
failure, and `recover()` finishes every saga without a final log entry, compensating the in-doubt step. Shipping is
last (the pivot step). A supervisor restarts the orchestrator after a crash.

## Consequences
- Courier outages (6 orders per run, 10% cohort) end compensated with revenue 0 and a clean audit.
- The orchestrator is a component to run and keep available; its saga log is the source of truth for recovery.
- Every step and compensation must be idempotent because recovery repeats work.
