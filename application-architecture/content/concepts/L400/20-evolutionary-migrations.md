**Concept: Evolutionary architecture: expand/contract migrations, API versions, flags, fitness over time**

## Why it matters
Library Loans runs four instances behind a load balancer and deploys them one at a time, so old and new code
always overlap for a while. Now the team wants to split `members.name` into `given_name` and `family_name` and
offer a v2 API. Changing the schema in one step and then deploying broke 36 of 100 requests in the lab: the old
instances asked for a column that was gone. Systems that must keep running cannot change in one step; they
change through a sequence of states that are each compatible with the code running at that moment.

## Mental model
Parallel change, also called expand and contract: first add the new shape next to the old (expand), move every
reader and writer over (migrate), then remove the old shape (contract). Each step is safe for whatever code is
running, and a fitness function checks every step.

```
schema   name ─────────────────────────────────────────────────────────────┐ (contract: drop)
         given_name, family_name ──(expand)── backfill ──────────────────────────────────►
code     v1 (name) ─► v2 (writes both; reads new when flag on) ─► v3 (new columns only)
API      /v1 {name}  + Deprecation, Sunset, Link ──────────────────────────── (sunset date)
         /v2 {givenName, familyName} ───────────────────────────────────────────────────►
gate     can_contract(): backfill complete AND no running version uses `name`
history  one JSON line of fitness metrics per step ─► dashboard fails CI on errors > 0 or expired flags
```

## Design space
- **Big-bang migration** with downtime or a maintenance window: simple, honest, sometimes acceptable for
  internal tools. Not acceptable when the SLO counts every minute.
- **Expand/contract with dual writes.** The common zero-downtime pattern. Cost: several deploys, transitional
  code and a backfill job.
- **Change data capture / shadow tables** (copy the table, sync changes, swap): for very large tables, at the
  price of extra tooling.
- **API evolution.** Additive, tolerant-reader changes need no version. Breaking changes need a new version or a
  new field next to the old one. Announce removal with `Deprecation` (RFC 9745) and `Sunset` (RFC 8594) headers,
  and keep consumer contracts green (lesson 14).
- **Feature flags** decouple deploy from release. Release toggles are transitional: give them an owner and an
  expiry date and fail the build when they outlive it.

## How to decide
Criteria: can old and new code run at the same time (they always can during a rolling deploy), how many
rows, who consumes the API and how fast they move, and the tolerated error budget during the change.

Worked example (lab, 4 instances, 100 requests per phase, seeded):

| Plan | Failed requests | Where |
|---|---|---|
| Change the schema in one step, then deploy v3 | 36 of 100 | `v1: no such column: name` |
| Expand/contract, contract when the backfill is done | 62 of 700 | 50 while v2 still dual-wrote, 12 during the v3 rollout |
| Expand/contract, guarded contract | 0 of 700 | the guard refused while instances ran v2 |

The second plan looked correct on paper: expand, dual write, backfill, flag. Its contract step asked only "is
the backfill complete?". The right question is "does any running code still use the column?". A second lesson
came from a try-it: when the old column is `NOT NULL`, v3 inserts fail (38 errors). Expand must leave the old
column writable by code that no longer knows about it.

## Failure modes at scale
- **Long backfills.** Millions of rows in one transaction block writers. Batch (the lab uses 50 rows per
  transaction), throttle, and make the job resumable.
- **Readers you do not know about.** Reports, ETL jobs and other teams read the old column. Find them before
  the contract step: query logs, grants, or a period where the column is renamed and monitored.
- **Flag debt.** Toggles multiply and interact. Expiry dates plus a failing gate keep the count small.
- **Version skew in the guard.** The guard must see real running versions (deploy API, service registry),
  not a config file someone forgot to update.
- **Fitness drift.** A single green build says little; the history shows trends. The lab appends one JSON line
  per step and the dashboard judges each one.

## Common mistakes
- Treating the contract step as "cleanup" and running it together with the code change.
- Making the new columns `NOT NULL` during expand, so old code that does not write them fails.
- Removing API v1 on the announced date without checking that its traffic has actually reached zero.
