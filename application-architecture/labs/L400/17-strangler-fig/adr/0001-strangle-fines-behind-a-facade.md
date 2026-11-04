# ADR 0001: Extract the fines module behind a strangler facade with a parallel run

## Status

Accepted (2026-10-28).

## Context

The fines rule lives inside the Library Loans monolith (`legacy_monolith.calculate_fine`) and two callers use it
directly. We want to own and deploy fines independently. The rule has quirks (2 grace days, students pay half,
cap 10.00, cents rounded half-up) that nobody fully documented. Constraint: no member may be charged a different
fine because of the migration (budget: mismatch rate <= 0.1 % over >= 1,000 compared requests, 0 candidate errors).

Measured on 2,000 seeded requests (`failure_lab.py`): switching all traffic at once (big bang) would have charged
108 members (5.4 %) a different fine. The parallel run found the same 108 differences while every member still got
the legacy answer. The cause was rounding: the new service used `round()` (half to even), the monolith half-up.

## Decision

1. Callers depend on `FinesPort` (branch by abstraction); only the `LegacyFines` adapter imports the monolith.
2. A facade routes `legacy -> shadow (parallel run) -> canary % -> service`. In shadow mode the legacy answer is
   returned and every difference is written to `out/mismatches.jsonl`.
3. Cut over only when `cutover_decision()` says ready (criteria above). Canary buckets are sticky per member.
4. Fitness function `fitness_legacy.py`: no new code may import `legacy_monolith`; `legacy_callers.json` is a
   ratchet that may only shrink.

## Consequences

- Transitional code (facade, adapter, comparison) must be deleted after the cut-over; it is tracked by the ratchet.
- Shadow mode doubles the fine work and, over HTTP, added about 1.5-2 ms per call here.
- Read-only operations are safe to compare; operations that write would need idempotent or dual writes.
- The monolith's two remaining callers (`strangler.py`, `monolith_reports.py`) must migrate before the legacy
  function can be removed.
