# ADR 0007: Every request passes policy, then tenant-scoped SQL, and both are checked in CI

## Status

Accepted (2026-10-28).

## Context

Five libraries share one database (lesson 18: shared schema). Authorization rules (lesson 19) and tenant
scoping protect the same thing from two sides: the policy decides who may act on which library's data;
the SQL decides which rows a statement can touch. Either alone fails open on one bug: lesson 19's first
librarian rule allowed cross-library access, and lesson 18's new report leaked 686 of 700 rows.

## Decision

1. Each public `LoansService` method calls `_authorize()` (policy enforcement point) with attributes read
   from trusted sources (the database for `active_loans`, the subject from the token).
2. Every statement binds `:tenant`; `TenantGuard` records any statement without the current tenant id.
3. The outbox relay is a system process and reads all tenants' rows on purpose; it never serves a request.
4. CI gates: policy cases 14/14, no public method without `_authorize`, no loans query without
   `WHERE tenant_id`, 0 guard violations, 0 rows of another library in cross-library probes, no email in decision logs.

## Consequences

- Two independent guards: a seeded fault in either one turns the scorecard NO-GO (tests prove both).
- Policy input building is code that must be reviewed like the policy itself.
- A server database would add row-level security as a third guard.
