**Concept: Aggregates and invariants (DDD)**

## Why it matters
"A member may have at most three loans" sounds simple until two requests for the same member arrive
together. Each one counts two loans, each one adds a third, and the member ends up with four. Rules
belong in one place, one transaction, one version of the data.

## Mental model
An aggregate is a sealed envelope: the member and their loans travel together. Only the root opens it;
the repository files the whole envelope or nothing.

```
          ┌──── Member aggregate (one transaction) ────┐
borrow ──►│ Member (root) ── Loan b1 ── Loan b2 ...     │──► SqliteMemberRepository
          │ invariants: ≤ max_loans, no book twice      │    load / save WHOLE, version check
          └─────────────────────────────────────────────┘
other member's rule ──► database: unique index on active book_id
```

## How it works
1. **The root guards the invariants.** `Member.borrow` checks both rules before any state changes; loans
   are frozen and exposed as a tuple → see lab step 1
2. **One repository per aggregate.** There is no `LoanRepository`: loans are loaded and saved only as
   part of their member, in one SQLite transaction → see lab step 3
3. **Optimistic concurrency.** `save` updates the row only `WHERE version = ?`; a stale copy gets
   `ConcurrencyConflict` instead of overwriting newer data → see lab step 4
4. **Rules across aggregates live elsewhere.** "One active loan per book" spans two members, so a
   partial unique index enforces it, not `Member` → see lab step 2

**Worked example** (`research/L200_concept_examples.py`): two copies of m1 are loaded at version 1. Copy A
borrows b3 and saves, so the stored version becomes 2. Copy B borrows b4, and its save fails with
"member m1 changed since version 1". Without the check, B overwrites A and b3 is silently lost.

## Trade-offs
| Use it when | Avoid it when |
|---|---|
| Rules connect several objects (limits, totals, no duplicates) | Data is mostly read or edited field by field |
| Concurrent updates to the same entity are likely | One big aggregate would lock unrelated changes together |
| You want unit tests of the rules with no database | A database constraint alone already states the rule |

## Common mistakes
- Exposing a mutable list (`member.loans.append(...)`), which bypasses the root.
- Building one huge aggregate (library → all members → all loans). Keep aggregates small and reference
  others by id.
- Saving parts of an aggregate from different repositories in separate transactions.
