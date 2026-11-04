# Lab 19 – Policy as code: a decision point, RBAC vs ABAC, policy tests and decision logs

Library Loans' authorization rules move out of the handlers into one **policy file**, `policy/loans.rego` (Rego v1 syntax). `rego_lite.py` is a small **learning-only evaluator** for a subset of Rego (default, `allow if {…}`, `deny contains "…" if {…}`, `==`/`!=`/`<`/`>`/`in`/`not`/`count()`); the same file runs on **OPA 1.21.4** in CI. Handlers are **policy enforcement points** (`authorize()` first); the **decision point** answers `allowed`, the deny reasons and the matched rules, and writes one **decision log** line per decision with the email erased. The requirements are 14 **policy test** cases (`policy/cases.json`). A plain **RBAC** role table is measured against the same cases. The shipped policy has a seeded hole: a new librarian rule forgot the library check.

## Files
| File | Purpose |
|---|---|
| `rego_lite.py` | Rego-subset parser + evaluator, `DecisionPoint` with decision log and masking (lesson code) |
| `policy/loans.rego` | The policy; **seeded fault**: rule R3 (librarians) has no tenant condition |
| `policy/cases.json` | 14 requirement cases (shared by Python tests and OPA tests) |
| `policy/loans_test.rego` | OPA policy tests (`opa test policy/`, CI) |
| `handlers.py` | Policy enforcement points: `authorize()` then work |
| `rbac.py` | Option A: role → actions table |
| `fitness_policy.py` | Fitness gates: policy tests, rule coverage, PEP coverage |
| `opa_parity.py` | CI: OPA and rego_lite give the same decision for every case (skips without `opa`) |
| `app.py` | Cases through the handlers, decision log `out/decisions.jsonl`, RBAC comparison |
| `failure_lab.py` | The cross-library librarian, base vs solution |
| `adr/0003-policy-as-code-abac.md` | Decision record |
| `test_policy.py` / `test_build_task.py` / `solution/loans.rego` | Tests / build task check / solution |
| `try_it.py` | The two tryIt experiments |

## Run
```bash
cd labs/L400/19-policy-as-code
python app.py                    # shipped policy: 13/14 cases
python failure_lab.py
python fitness_policy.py         # exit 1 until you fix policy/loans.rego
python app.py --solution
python -m unittest -v
```

## Expected output (observed 2026-10-28, Python 3.12.15, Linux)
Decisions, revisions and log lines are deterministic; the per-decision time varies (290–1,145 µs on this shared host).
```
$ python app.py
policy policy/loans.rego (revision 58df760cbce4): 13/14 requirement cases
RBAC role table            : 7/14 requirement cases
  WRONG: librarian of another library (expected allowed=False)
decision log: out/decisions.jsonl, 14 lines; first: {"decision_id": "58df760cbce4-000001", "deny": [], "erased": ["/input/subject/email"], "input": {"action": "borrow", "resource": {"active_loans": 2, "member_id": "m1", "tenant": "lib00"}, "subject": {"id": "m1", "roles": ["member"], "tenant": "lib00"}}, "matched": ["allow@12", "allowed@44"], "path": "loans/authz/allowed", "result": true, "revision": "58df760cbce4", "timestamp": "2026-10-28T12:00:00Z"}
in-process decision: 1145 us (varies by host)
$ python app.py --solution
policy solution/loans.rego (revision 2cbda4fd0af3): 14/14 requirement cases
RBAC role table            : 7/14 requirement cases
decision log: out/decisions.jsonl, 14 lines; first: {"decision_id": "2cbda4fd0af3-000001", ... "matched": ["allow@12", "allowed@45"], ...}
in-process decision: 290 us (varies by host)
$ python fitness_policy.py
{"gate": "policy-tests", "ok": false, "value": ["librarian of another library"], "budget": "14/14 pass"}
{"gate": "rule-coverage", "ok": true, "value": [], "budget": "every allow/deny rule"}
{"gate": "pep-coverage", "ok": true, "value": [], "budget": "0 handlers without authorize()"}
$ python opa_parity.py
opa not found: parity check skipped (runs in the CI job 'opa')
```
`allow@12` = the allow rule that starts on line 12. RBAC misses 7 cases: borrowing for someone else, viewing another member's loans, another library (member and librarian), the loan limit, suspension and the 25.00 waiver.

## failureLab: a librarian of another library
```
$ python failure_lab.py
request: {'action': 'view', 'subject': {'id': 's9', 'tenant': 'lib01', 'roles': ['librarian']}, 'resource': {'tenant': 'lib00', 'member_id': 'm2', 'active_loans': 1}}
base    : allowed=True matched=['allow@27', 'allowed@44']; policy tests failed: ['librarian of another library']
solution: allowed=False matched=[]; policy tests failed: []
```

## Tests (observed 2026-10-28)
```
$ python -m unittest -v
test_all_policy_gates (test_build_task.LibrarianScopeTest.test_all_policy_gates) ... ok
test_librarian_of_another_library_is_denied (test_build_task.LibrarianScopeTest.test_librarian_of_another_library_is_denied) ... ok
test_librarian_of_the_same_library_still_works (test_build_task.LibrarianScopeTest.test_librarian_of_the_same_library_still_works) ... ok
test_handlers_raise_forbidden (test_policy.ComparisonTest.test_handlers_raise_forbidden) ... ok
test_pep_and_rule_coverage_gates (test_policy.ComparisonTest.test_pep_and_rule_coverage_gates) ... ok
test_rbac_cannot_express_attribute_rules (test_policy.ComparisonTest.test_rbac_cannot_express_attribute_rules) ... ok
test_symptom_base_policy_lets_librarians_cross_libraries (test_policy.ComparisonTest.test_symptom_base_policy_lets_librarians_cross_libraries) ... ok
test_log_lines_can_be_collected_in_memory (test_policy.DecisionLogTest.test_log_lines_can_be_collected_in_memory) ... ok
test_one_json_line_per_decision_with_email_erased (test_policy.DecisionLogTest.test_one_json_line_per_decision_with_email_erased) ... ok
test_not_in_and_count (test_policy.EngineTest.test_not_in_and_count) ... ok
test_parses_rules_and_defaults (test_policy.EngineTest.test_parses_rules_and_defaults) ... ok
test_undefined_path_is_false_not_an_error (test_policy.EngineTest.test_undefined_path_is_false_not_an_error) ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.097s

OK
```

## Build task (the hardening change)
Add `input.subject.tenant == input.resource.tenant` to rule R3 in `policy/loans.rego`.
- Solution: `solution/loans.rego`.
- Check (solution by default; YOUR file with `CHECK_MINE=1`):
```
CHECK_MINE=1 python -m unittest -v test_build_task          # Mac mini (zsh)
$env:CHECK_MINE = "1"; python -m unittest -v test_build_task   # Windows (PowerShell)
Remove-Item Env:\CHECK_MINE                                     # Windows: switch back
```
Fail before / pass after (observed 2026-10-28):
```
$ CHECK_MINE=1 python -m unittest test_build_task      # unchanged policy/loans.rego
FAIL: test_all_policy_gates
FAIL: test_librarian_of_another_library_is_denied
FAILED (failures=2)
$ python -m unittest test_build_task                   # solution
OK
```

## OPA (pending-ci)
OPA 1.21.4 (Apache-2.0, CNCF graduated) is the production equivalent. Not run here (no binary in the sandbox).
```
brew install opa                                   # Mac mini (Homebrew formula 1.21.4)
# Windows: download opa_windows_amd64.exe from https://github.com/open-policy-agent/opa/releases
opa test policy/ -v                                # policy/loans_test.rego + policy/cases.json as data
python opa_parity.py solution                      # same decision as rego_lite for all 14 cases
```

## Try it (observed 2026-10-28)
```
$ python try_it.py
[1] new renew() handler -> {'gate': 'pep-coverage', 'ok': False, 'value': ['renew'], 'budget': '0 handlers without authorize()'}
[2] suspended librarian borrows for m2 -> {'allowed': False, 'deny': ['account suspended'], 'matched': ['allow@27', 'deny@34']}
```

## Mac mini and Windows
Same commands inside the venv. The policy and cases are UTF-8 text; `opa` on Windows is a single `.exe`.

## Troubleshooting
| Symptom | Action |
|---|---|
| A rule never matches | rego_lite treats a missing input path as undefined (false), like Rego: check the attribute name in the input. |
| `rule-coverage` lists a rule | No case exercises it: add a requirement case that it decides. |
| A Rego feature fails in rego_lite | It is a learning subset; use OPA (`opa eval`) for anything beyond the listed syntax. |
