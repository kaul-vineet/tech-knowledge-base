# ADR 0004: Schema and API changes use expand/contract, release flags and a guarded contract step

## Status

Accepted (2026-10-28).

## Context

We split `members.name` into `given_name` and `family_name` and add a v2 API shape. Library Loans runs
4 instances behind a load balancer and deploys them one at a time, so old and new code always overlap.
Constraint: zero failed requests during the change; old API consumers keep working until the sunset date.

Measured by `rollout.py` (4 instances, 100 requests per phase, seeded):
- Changing the schema in one step, then deploying: 36 of 100 requests failed (`v1: no such column: name`).
- Expand/contract with a contract step that only checked the backfill: 62 of 700 failed; the column was
  dropped while v2 instances still dual-wrote it.
- Expand/contract with the guarded contract: 0 of 700 failed.

## Decision

1. Every breaking schema change is expand -> deploy dual-writing code -> backfill in batches of 50 ->
   switch reads with a release flag -> deploy code that no longer uses the old column -> contract.
2. `can_contract()` refuses while any instance runs a version that uses the old column, or while rows are
   not backfilled. The old column stays nullable so new code can stop writing it.
3. API v1 stays, rebuilt from the new columns, with `Deprecation` (RFC 9745), `Sunset` (RFC 8594) and a
   `Link rel="deprecation"` header.
4. Flags live in `flags.json` with owner and expiry; the `no-expired-flags` gate fails the build after expiry.
5. Every rollout step appends a JSON line of fitness metrics; `dashboard.py --plan expand_contract` fails
   CI if any step has errors > 0 or expired flags.

## Consequences

- A change takes several deploys instead of one; the plan and its history make progress visible.
- Dual writes and the v1 representation are transitional code with a removal date.
- The guard needs to know the running versions (here the fleet list; in production a deploy API or the
  service registry).
