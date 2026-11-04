# ADR 0002: Shared schema with an enforced tenant id; database-per-tenant only as a premium tier

## Status

Accepted (2026-10-28).

## Context

Library Loans will host many small libraries (50 in the model, 40 loans each) and a few large ones.
Constraints: no library may ever see another library's loans (0 leaked rows); one schema change must not cost
a migration per tenant for the small libraries; a large library's bulk import must not block other libraries
for regulated or very busy customers.

Measured by `app.py` (50 libraries, SQLite files):

| Layout | Leaked rows with one missing filter | Neighbour writes blocked during a bulk import | DDL statements / files for one column |
|---|---|---|---|
| shared schema | 686 of 700 | 20 of 20 | 1 / 1 |
| schema per tenant (table per tenant) | 0 (guard still flags the query) | 20 of 20 | 50 / 1 |
| database per tenant | 0 (guard still flags the query) | 0 of 20 | 50 / 50 |

## Decision

1. Default: shared schema with `tenant_id` on every row and as the first column of every index.
2. Isolation is enforced twice: the static fitness function `fitness_tenant.py` (no SQL on a tenant table
   without `WHERE tenant_id = ?`) and the runtime `TenantGuard` (every statement must carry the current tenant's id).
3. A tenant that needs write isolation or per-tenant restore moves to a database-per-tenant tier; the same
   repository code runs on both because every statement is already tenant-scoped.

## Consequences

- One missed filter would leak everything in the shared table, so the two guards are mandatory in CI.
- SQLite has one writer per file: in the shared file a bulk import blocks every library. Bulk imports must be
  chunked into short transactions (or the tenant moves to its own file).
- Migrations on the premium tier fan out per tenant file; the migration runner must track per-tenant progress.
- A database with row-level security (PostgreSQL `ENABLE`/`FORCE ROW LEVEL SECURITY`) would be a third guard on a server database.
