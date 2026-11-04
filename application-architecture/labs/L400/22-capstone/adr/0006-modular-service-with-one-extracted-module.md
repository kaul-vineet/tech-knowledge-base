# ADR 0006: Keep Library Loans a modular service and extract only the fines module

## Status

Accepted (2026-10-28).

## Context

The capstone evolves Library Loans into a production-ready system. Splitting every module into a service
would multiply deployments, contracts and failure modes for a team that ships one product. Fines change for
reasons of their own (pricing rules per library) and were the module with a clear seam (`FinesPort`).
Lesson 17 measured the risk of a big-bang switch: 108 of 2,000 members would have been charged a different fine.

## Decision

1. Library Loans stays one deployable service with modules (lessons 3 and 7); fines is the only module
   extracted, behind the strangler facade, with branch by abstraction (`FinesPort`).
2. The capstone runs the facade in shadow mode on 2,000 seeded requests and switches it to `service` only
   when `cutover_decision()` reports mismatch rate <= 0.1 % and 0 candidate errors.
3. The capstone code never imports the monolith's fine code (scorecard criterion "no new legacy callers").

## Consequences

- One network hop and one contract more (fines), not five.
- Shadow mode doubles fine computations until the cut-over; the facade is transitional code.
- Extracting the next module reuses the same facade, parallel run and ratchet.
