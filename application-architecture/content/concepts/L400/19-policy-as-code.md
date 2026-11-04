**Concept: Policy as code: a decision point, RBAC vs ABAC, policy tests and decision logs**

## Why it matters
Who may borrow, return, view or waive what? In most services the answer is scattered across handlers as
`if user.role == ...`. Nobody can review them in one place, test them, or answer an auditor's "why was this
allowed?". Library Loans now has rules that depend on attributes: own
loans only, same library, at most 5 active loans, no suspended accounts, waivers above 20.00 need a manager.
In the lab a new librarian rule shipped without the library check, and a librarian of lib01 could view
lib00's loans. Every unit test passed; one requirement case in the policy tests failed.

## Mental model
Separate the question from the place where it is asked. The service is the policy enforcement point (PEP):
it builds an input document and asks. The decision point (PDP) evaluates a policy file and answers with a
decision plus the rules that matched. Every answer is logged.

```
handler (PEP) ── input {action, subject, resource} ──► PDP: loans.rego ──► {allowed, deny reasons, matched}
   │ trusted attributes only (token, database)              │ default deny, deny overrides allow
   └── 403 or proceed                                       └──► decision log (JSON line, email erased)
CI: requirement cases 14/14 · every allow/deny rule covered · every handler calls authorize() first
```

## Design space
- **Inline checks.** Fast to write; the rules spread, drift and cannot be tested or audited as a whole.
- **RBAC** (NIST model, INCITS 359): users get roles, roles get permissions. Simple to administer and audit,
  but blind to attributes: "own loans", "same library" and "loan limit" need new roles or code outside the model.
- **ABAC** (NIST SP 800-162): rules over attributes of subject, resource, action and environment. Expressive;
  the price is that attributes must be correct and the rules need tests.
- **Where the PDP runs.** As a library in the process (the lab's `rego_lite.py`, or OPA's Go SDK or Wasm), as a
  sidecar or daemon over HTTP (OPA's REST API), or as a central service. Closer means faster and more
  available; central means one place to update and observe.
- **Combining rules.** Default deny, then deny-overrides: any deny rule beats every allow rule. Order-free rules
  review more easily.

## How to decide
Criteria: how many rules depend on attributes, who changes the rules (developers or a security team), audit
needs, latency budget per request, and the cost of a wrong allow versus a wrong deny.

Worked example (lab, 14 requirement cases in `policy/cases.json`):

| Option | Cases decided correctly | Notes |
|---|---|---|
| RBAC role table | 7 of 14 | misses own-loan, same-library, loan-limit, suspension and waiver-size rules |
| ABAC policy, first version | 13 of 14 | librarian rule without `input.subject.tenant == input.resource.tenant` |
| ABAC policy, fixed | 14 of 14 | the same file runs on OPA 1.21.4 in CI (`opa test policy/`) |

Each decision is one JSON line: decision id, policy revision (a hash of the file), the input with
`/input/subject/email` erased, the result and the matched rules (for example `allow@12`). The rule-coverage
gate requires every allow and deny rule to be the reason for at least one case, the same idea as
`opa test --coverage`. The learning engine took 290-1,145 µs per decision on this shared host because it
re-parses expressions each time; OPA compiles the policy once.

## Failure modes at scale
- **Wrong attributes.** A PDP is only as good as its input. If `tenant` comes from the request body, any
  caller can claim any library. Build the input from the verified token and the database.
- **Policy drift between services.** Copies of the policy diverge. Ship versioned bundles; log the revision.
- **Decision logs as a data leak.** Inputs contain personal data. Mask fields before writing (OPA:
  `system.log.mask`), and set retention.
- **Latency and availability.** A remote PDP on every request adds a network hop and a dependency; cache
  decisions carefully, or run the PDP next to the service.
- **Lists.** "Which loans may I see?" cannot be asked per row at scale; push the filter into the query.

## Common mistakes
- Writing tests only for the allow paths. Most incidents are wrong allows; test the denies.
- Letting handlers keep "just one" rule inline. The PEP-coverage gate checks that every public handler calls
  `authorize()` first.
- Treating the decision log as debugging output instead of an audit record with a schema and a retention period.
