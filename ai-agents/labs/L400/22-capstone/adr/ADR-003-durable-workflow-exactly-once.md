# ADR-003: A durable SQLite workflow with approval deadlines and idempotent effects

## Status
Accepted (2026-10-28). Fitness: `test_m4_durable.py`.

## Context
A triage can wait for the incident lead (rollbacks) and the process can die after a page was sent. Lesson 18's crash sweep found 0 duplicate effects with checkpoints + idempotency keys, and 1-4 duplicates without them.

## Decision
We will checkpoint each step (facts, retrieve, propose, decide, approval, effects) in SQLite, send every effect with the key `"<incident>:<action>"`, and expire rollback approvals after 4 hours (late clicks are ignored).

## Consequences
- In the seeded run the process was killed right after INC-4's page; the restart replayed the page (Idempotent-Replayed) and sent 11 effects in total, none twice.
- One SQLite writer per triage host; a Temporal deployment (lesson 18 equivalent) is the next step for several hosts.
