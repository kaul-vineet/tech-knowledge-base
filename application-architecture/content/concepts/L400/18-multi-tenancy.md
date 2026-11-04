**Concept: Multi-tenancy: shared schema, schema per tenant, database per tenant**

## Why it matters
Library Loans becomes a hosted service for many libraries. Each library is a tenant: its members, loans and
fines must be invisible to every other library, and a large library's nightly import must not freeze the
small ones. The layout of the data decides how hard each of those promises is to keep. In the lab, one new
report query that forgot `WHERE tenant_id` returned 700 rows to library lib00, of which 686 belonged to other
libraries. With a different layout the same bug leaked nothing. Tenancy is a design decision, not a
column you add later.

## Mental model
Isolation is enforced somewhere: by a WHERE clause, by a table or schema name, or by a separate database.
The further out the boundary, the stronger the isolation and the more copies you operate.

```
shared schema        one table, tenant_id on every row      isolation = every query's WHERE clause
schema per tenant    one table (schema) per tenant           isolation = the name you pick
database per tenant  one database (here: SQLite file) each   isolation = the connection you open
guards: static gate (no SQL without "WHERE tenant_id = ?")  +  TenantGuard (statement carries THIS tenant's id)
```

## Design space
- **Shared schema.** Cheapest to run and migrate (one DDL statement), easy cross-tenant analytics for the
  operator, but every query is a potential leak and all tenants share locks and indexes. Put `tenant_id`
  first in every index.
- **Schema per tenant.** Names separate the data, so a forgotten filter cannot cross tenants, but migrations
  fan out per tenant and catalogs grow. SQLite has no `CREATE SCHEMA`; `ATTACH` gives a schema name per file but
  allows 10 attached databases by default (125 at most).
- **Database per tenant.** Strongest isolation, per-tenant backup, restore and placement, no shared write
  locks. You operate N databases: connection pools, migrations and monitoring multiply.
- **Hybrid tiers.** Most tenants shared; large or regulated tenants on their own database. This works only if
  the code is identical on both, which tenant-scoped statements make possible.
PostgreSQL adds another guard: row-level security (`FORCE ROW LEVEL SECURITY` filters even the table owner).

## How to decide
Criteria: blast radius of one bug (isolation), noisy-neighbour tolerance, migration and operations effort,
tenant count and size distribution, and compliance needs such as per-tenant restore or data residency.

Worked example (lab, 50 libraries x 40 loans, SQLite files):

| Layout | Leaked rows, one missing filter | Neighbour writes blocked during a bulk import | DDL statements / files for one new column |
|---|---|---|---|
| shared schema | 686 of 700 | 20 of 20 | 1 / 1 |
| schema per tenant | 0 | 20 of 20 | 50 / 1 |
| database per tenant | 0 | 0 of 20 | 50 / 50 |

The guard flagged the missing filter in all three layouts, including the two where it caused no leak, so the
bug is found before a layout change exposes it. SQLite allows one writer per file: while lib01's import held
the write lock, all 20 of lib02's borrow attempts failed with "database is locked" in the shared file, and
none failed with separate files. The lab's decision (ADR 0002): shared schema with both guards for the many
small libraries; database per tenant as a tier for the few that need write isolation or their own restore.

## Failure modes at scale
- **One missing filter = total leak** in a shared table. Signal: guard violations or the static gate in CI;
  in production, audit queries comparing returned tenant ids with the caller's.
- **Noisy neighbour.** Long transactions, table scans or bulk imports of one tenant raise everyone's latency.
  Signal: per-tenant p99 and lock waits; fix with short batches, quotas, or moving the tenant.
- **Migration fan-out.** 5,000 tenant databases mean 5,000 migrations that can half-fail. Signal: per-tenant
  schema versions that differ; track them and make migrations idempotent (lesson 20).
- **Hot tenant** outgrows the shared database: one tenant dominates rows or writes.

## Common mistakes
- Trusting a tenant id from the request body instead of from the authenticated token (lesson 10).
- Filtering by tenant in some queries and relying on "the UI only shows our ids" for the rest.
- A guard that only checks for the word `tenant_id`: `tenant_id = 'lib01'` hard-coded in lib00's session still
  leaks. The lab's guard requires the current tenant's own id.
