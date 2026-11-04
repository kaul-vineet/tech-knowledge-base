**Concept: Strangler-fig decomposition: facade, branch by abstraction, parallel run, cut-over**

## Why it matters
The fines rule lives inside the Library Loans monolith. A team wants to own it as a service: new pricing per
library, its own deploys. The tempting plan is a rewrite and a switch-over weekend. In the lab that plan would
have charged 108 of 2,000 members a different fine, because the new code rounded half-cents to even while the
monolith rounded them up. Nobody had written that rule down. Partly understood behaviour is normal in legacy
work, so the question is: how do we move traffic so every difference is found before a member sees it?

## Mental model
A strangler fig grows around a host tree until the tree is no longer needed. In software, a facade sits in
front of the old code; new code grows behind the same facade; traffic moves one slice at a time.

```
callers ──► FinesPort (seam) ──► Facade ──┬─ legacy        (answers)
                                          ├─ shadow:  legacy answers, service compared ─► mismatches.jsonl
                                          ├─ canary:  N % of members (sticky) ─► service
                                          └─ service: legacy code can be deleted
cut-over gate: >= 1,000 comparisons, mismatch rate <= 0.1 %, 0 candidate errors
fitness: no NEW import of legacy_monolith (ratchet: legacy_callers.json may only shrink)
```

## Design space
- **Big-bang replacement.** One switch. Cheapest transitional code, highest risk: every behaviour difference
  reaches users at once, and rollback means another big switch.
- **Facade with routing (strangler).** An HTTP gateway or an in-process router decides per request. It costs
  transitional code that must be removed later; it buys gradual, reversible moves.
- **Branch by abstraction.** Inside the codebase, callers move to an interface (`FinesPort`) first; two
  implementations coexist; a flag picks one. It keeps trunk releasable during a long change.
- **Parallel run (shadow).** Run both, return the legacy answer, record differences. It is safe only for
  operations without side effects, or with idempotent writes, and it doubles the work.
- **Canary.** Route a stable slice of members to the new code. Sticky buckets (a hash of the member id) keep
  one member's experience consistent.
They combine: the lab uses seam, facade, shadow, canary and service in sequence.

## How to decide
Criteria: how well the behaviour is specified, whether the operation has side effects, the cost of a wrong
answer, and how long both versions can live. Evidence comes from replaying real or seeded traffic.

Worked example (lab, 2,000 seeded requests, 30 % students):

| Option | Wrong fines seen by members | Differences found | Cost |
|---|---|---|---|
| Big bang to the new service | 108 (5.4 %) | after the fact | none extra |
| Shadow, then cut over | 0 | 108, logged with inputs | 2x fine work; over HTTP 3-27 s per 2,000 calls on this shared host |
| Shadow with the fixed service | 0 | 0, so `cutover_decision` says ready | same |

The log showed the pattern at once: students at 3, 7, 11 … days late, where half a cent appears. The fix
(`Decimal` with `ROUND_HALF_UP`) made the mismatch rate 0.0 % and the gate opened. The criteria are code, so
"almost ready" cannot be argued: with only 300 comparisons the gate says "only 300 comparisons (< 1000)".

## Failure modes at scale
- **Non-deterministic outputs** (timestamps, ids, ordering) look like mismatches. Compare a cleaned value, the
  way GitHub's Scientist library offers `compare` and `clean`.
- **Side effects in shadow mode.** Shadowing a write sends two emails or charges twice. Shadow reads; dual-write
  writes with idempotency keys.
- **Transitional code that never leaves.** Facades, flags and adapters accumulate. The ratchet fitness function
  fails the build on any new import of the legacy module and shows which callers are left.
- **Latency budget.** Synchronous shadow calls add load and latency. Sample shadow traffic or run the
  candidate asynchronously.
- **Data ownership.** The extracted service needs its data. Until it owns it, the monolith's tables are a
  shared contract (lesson 14) and a migration (lesson 20).

## Common mistakes
- Comparing only status codes or "no exception" instead of the business result. The rounding bug returned
  HTTP 200 every time.
- Letting a candidate exception reach the user. The parallel run must catch it, count it and return the legacy
  answer.
- Cutting over on a calendar date instead of on measured criteria, then leaving the old code "just in case"
  with no ratchet that forces its removal.
