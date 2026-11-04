# ADR 0003: Authorization rules as an ABAC policy file, evaluated by a decision point, with decision logs

## Status

Accepted (2026-10-28).

## Context

Authorization rules for Library Loans (own loans only, same library, loan limit 5, suspended accounts,
fine waivers above 20.00 need a manager) were growing as if-statements inside handlers. We need the rules
reviewable in one place, testable without the service, and auditable per decision. Constraints: 14 of 14
requirement cases (`policy/cases.json`) decided correctly; every public handler enforces a decision;
every allow/deny rule covered by at least one case; no email addresses in decision logs.

Measured (`app.py`): a role table (RBAC) decides 7 of 14 cases correctly: it cannot see whose loan, which
library, how many loans or how large the fine. The ABAC policy decides 14 of 14 once the librarian rule
checks the library (`failure_lab.py`: the first version allowed a librarian of lib01 to view lib00's loans,
and only the policy test caught it).

## Decision

1. Rules live in `policy/loans.rego` (Rego v1 syntax). Deny rules override allow rules.
2. Handlers are policy enforcement points: `authorize()` first, no rules in handler code (gate `pep-coverage`).
3. `policy/cases.json` is the requirement table; CI runs it with `rego_lite.py` and with OPA 1.21.4
   (`opa test policy/`, `opa_parity.py`). Gates: policy tests 14/14, rule coverage 100 %.
4. Every decision is logged as one JSON line (decision id, policy revision, input with `/input/subject/email`
   erased, result, matched rules).

## Consequences

- The policy is a deployable artifact: its revision hash is logged, so a decision can be replayed later.
- `rego_lite.py` is a learning subset (about 320-420 us per decision here because it re-parses expressions);
  production would run OPA as a library or sidecar, which compiles the policy once.
- Attributes must be supplied by the caller (tenant, active loans, amount); wrong attributes give wrong
  decisions, so the PEP builds the input from trusted sources (the token and the database), never from the request body.
