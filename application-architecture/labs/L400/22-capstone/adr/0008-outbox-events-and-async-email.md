# ADR 0008: Loan changes publish events through a transactional outbox; emails are sent asynchronously

## Status

Accepted (2026-10-28).

## Context

Other parts of the system (notifications, read models) react to `LoanCreated` and `LoanReturned`.
Publishing inside the request can lose events (crash after commit) or send events for rolled-back changes.
Lesson 21's capacity plan showed that sending the confirmation email inside POST /loans needs 6 instances
instead of 3 (mean service time 75.1 ms instead of 45.2 ms).

## Decision

1. The loan row and its event are written in one transaction (outbox table with `tenant_id`).
2. A relay publishes pending rows in order, at least once; consumers are idempotent by `eventId`
   (stable id `<tenant>-<type>-<loanId>`).
3. Emails are a consumer of these events, with 5 concurrent sender slots (Little's law: 3.6 in flight at peak).

## Consequences

- Delivery is at least once: the scorecard redelivers every event and checks that the projection is unchanged.
- Events arrive later than the HTTP response (eventual consistency); the member portal reads loans directly.
- The outbox table grows; published rows need a retention job.
