**Concept: Capstone: Library Loans, production-ready**

## Overview
The capstone turns the running example into a system you could defend in an architecture review. It does not
add new theory. It wires together decisions from earlier lessons and proves each one with a measured
criterion. `run_capstone.py` runs the whole system on seeded traffic (5 libraries, 600 requests) and prints a
scorecard, one JSON line per criterion. The release verdict is GO only if all 19 criteria pass. Four seeded
faults (a rounding bug in the extracted service, a librarian rule without the library check, a query without
the tenant filter, a consumer that is not idempotent) each turn the verdict to NO-GO. Tests prove that every
fault is caught by exactly the expected criteria.

## Architecture walkthrough
A request enters through the HTTP adapter, which a consumer contract (lesson 14) pins down. `LoansService`
first asks the policy decision point (lesson 19). The policy file is the fixed one from lesson 19, and every
decision is logged with the email erased. Then it runs SQL bound to `:tenant` on the shared schema. A
`TenantGuard` (lesson 18) records any statement without the current library's id. Returning a book asks the
strangler facade for the fine (lesson 17). The facade first shadows the extracted fines service on 2,000
requests and switches to it only when the mismatch rate is zero. The loan row and its event are written in one
transaction to the outbox (lesson 9). A relay publishes the events at least once, and idempotent consumers
apply each one exactly once, even when everything is delivered twice. Each request writes a JSON line with
route, status and duration; the lesson 15 SLIs and burn-rate alerts read them. CI also runs the lesson 21
capacity gate (p99 with one instance down) and checks that all nine ADRs follow the Nygard format.

```
portal ─contract─► HTTP ─► LoansService ─► policy (PEP→PDP, decision log)
                                       ├─► SQL :tenant + TenantGuard ─► loans + outbox ─► relay ─► idempotent consumers
                                       └─► strangler facade ─► fines service (after a clean parallel run)
request log ─► SLOs · contract · fitness gates · capacity · ADR log ─► scorecard ─► GO / NO-GO (code)
                                                                                └─► local model explains (checked)
```

## How it ties L100-L400
- **L100:** layers, module boundaries and the boundary fitness function, API-first, configuration, ADRs.
- **L200:** ports and adapters (the fines port), aggregates, the outbox and idempotent consumers, OIDC
  (the subject the policy sees), the testing pyramid.
- **L300:** contracts, SLOs and burn rates, fitness gates in CI, plus the resilience habit of injecting faults
  on purpose.
- **L400:** the design decisions themselves, each with options, evidence, an ADR and a fitness function that
  keeps it true.

The model boundary is the same as in the LPC1768 guide's capstone. The deterministic core decides. The local
model only explains the scorecard, and its note is rejected when its verdict or numbers differ from the code's.
In the try-it, loosening one threshold (cut-over at 6 % mismatches) lets the buggy fines service through with a
GO. A gate is only as good as the number in it, which is why thresholds live in ADRs and code review.
