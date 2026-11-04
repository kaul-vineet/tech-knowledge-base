# Explain runs — application-architecture (content/explain/01–27.md)

Every output quoted in a "What you see", "See it in numbers", failure-lab or proof block of `content/explain/NN.md`
was produced by the commands below, run on 2026-11-02 in the Linux sandbox (Python 3.12.15, SQLite 3.44.0,
stdlib only; no network installs). `research/explain_checks.py` checks every number in those blocks against this file.

How the runs were made
- Commands were executed one at a time with `PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1`; stdout and stderr are captured
  together (so on a terminal an stderr line can appear before/after a stdout line in a different order than below).
- L100/L200 labs and the L500 checks ran in place (they write nothing, or only to a scratch `.tryit-work` that their
  `try_it.py` removes). The CLI demo of lesson 7 used `--db` pointing outside the lab; lesson 6's "break a relationship"
  edit was applied to a copy of `doc/arch/`, not to the lab.
- L300/L400 labs write `out/*.jsonl` (and lesson 14 rewrites `contracts/*.json`), so they ran in a byte-identical scratch
  copy of `labs/` outside the knowledge base; headings below say "(byte-identical scratch copy …)". Nothing in `labs/`
  was modified.
- Not run here (marked "Expected (not run here)" in the explanations): mermaid-cli / Structurizr rendering (6),
  `agent_assist.py --real` with Ollama (6, 9, 15, 21, 22), Keycloak (10), Testcontainers PostgreSQL (11),
  Pact / Pact Broker (14), Prometheus rules (15), k6 (16), OPA 1.21.4 (19), `serve.py` + curl/Bruno (22).

Differences from the lesson/README text (the explanations quote what I got and say so)
- 03: the first `python -m unittest -v` died before running any test with `FileNotFoundError` from `os.path.abspath`
  (slow storage mount); the immediate re-run passed (`Ran 8 tests … OK`). Both runs are logged.
- 11: timings are far slower than the README (integration mean 4204.89 ms vs 87.60 ms; e2e/unit ratio 20,630 and,
  in try_it, 481,818 ≈ 10^6 vs the README's 17,876 ≈ 10^4); layer order and `pyramid OK` unchanged.
- 12: consistency window p50 16.3 ms (lesson: "about 10 ms").
- 15: build task with CHECK_MINE=1 on the base file reports `FAILED (failures=1, errors=1)` — the lesson says "2 of 3
  fail"; one of the two is an error (`KeyError: 'latency'`).
- 16: N+1 with 0.5 ms round trips took 209.8 ms here (lesson: about 340 ms; minimum 337 × 0.5 = 168.5 ms); the stand-alone
  `load_test.py` printed 80 requests (CLI default 8 users × 10) while the step text says 40 (the CI gate uses 4 × 10 = 40).
- 17: shadow over HTTP took 23.9 s (lesson range 3.0–26.6 s).
- 18: migration 36.6 ms shared vs 812.1 ms per-tenant files (lesson: 9–54 ms vs 0.45–4.5 s).
- 19: one in-process decision 86 µs (lesson: 290–1,145 µs).
- 23: a first run of `check_modularity.py` from the scratch copy printed `layered (L100 #2): 0 edges, acyclic, layers {}`
  because L100 was not in the copy; the run below is in place and matches the lesson (4 edges).
- 22: the four `--fault` runs below pipe through grep, so their `exit=` shows grep's status; the separate
  `unscoped-query` run with `PIPESTATUS` shows the real `exit=1`.
- 26, 27: no lab of their own; the outputs they quote come from the lesson 23 and 24 runs below.

## Lesson 01

### Lesson 01 — 2026-11-02 — `cd labs/L100/01-setup-workspace && python3 check_env.py` (exit 0)
```text
platform Linux x86_64
python   3.12.15    OK
stdlib   7 modules  OK
sqlite   3.44.0     OK
optional node       found - Node.js (for mermaid-cli)
optional npx        not found (ok) - runs mermaid-cli without a global install
optional podman     not found (ok) - Podman (for Structurizr; open source)
optional docker     not found (ok) - Docker (same role as podman)
optional ollama     not found (ok) - local model server (lesson 6 agent assist; optional)
```

### Lesson 01 — 2026-11-02 — `cd labs/L100/01-setup-workspace && python3 -m unittest -v` (exit 0)
```text
test_all_required_stdlib_modules_import (test_check_env.CheckEnvTest.test_all_required_stdlib_modules_import) ... ok
test_current_python_is_supported (test_check_env.CheckEnvTest.test_current_python_is_supported) ... ok
test_main_returns_zero (test_check_env.CheckEnvTest.test_main_returns_zero) ... ok
test_old_python_is_rejected (test_check_env.CheckEnvTest.test_old_python_is_rejected) ... ok
test_optional_tools_cover_both_container_engines (test_check_env.CheckEnvTest.test_optional_tools_cover_both_container_engines) ... ok
test_unknown_module_is_reported (test_check_env.CheckEnvTest.test_unknown_module_is_reported) ... ok

----------------------------------------------------------------------
Ran 6 tests in 1.966s

OK
```

### Lesson 01 — 2026-11-02 — `cd labs/L100/01-setup-workspace && python3 run_all_labs.py` (exit 0)
```text
01-setup-workspace             OK
02-layered-structure           OK
03-modular-monolith            OK
04-api-first-openapi           OK
05-config-12factor             OK
06-documenting-architecture    OK
ALL LABS PASSED
```

### Lesson 01 — 2026-11-02 — `cd labs/L100/01-setup-workspace && python3 try_it.py` (exit 0)
```text
[1] test file renamed to checks_env_test.py -> exit 5: NO TESTS RAN
[2] MIN_PYTHON=(3, 99) -> main() returns 1; python line: python   3.12.15    TOO OLD (need 3.12+)
```

## Lesson 02

### Lesson 02 — 2026-11-02 — `cd labs/L100/02-layered-structure && python3 app.py --storage memory` (exit 0)
```text
storage=memory
borrow b1 by m1 -> 201 {'id': 1, 'bookId': 'b1', 'memberId': 'm1', 'status': 'active'}
borrow b1 by m2 -> 409 {'error': 'book b1 is already on loan'}
return loan 1   -> 200 {'id': 1, 'bookId': 'b1', 'memberId': 'm1', 'status': 'returned'}
get loan 99     -> 404 {'error': 'loan 99 not found'}
```

### Lesson 02 — 2026-11-02 — `cd labs/L100/02-layered-structure && python3 app.py --storage sqlite` (exit 0)
```text
storage=sqlite
borrow b1 by m1 -> 201 {'id': 1, 'bookId': 'b1', 'memberId': 'm1', 'status': 'active'}
borrow b1 by m2 -> 409 {'error': 'book b1 is already on loan'}
return loan 1   -> 200 {'id': 1, 'bookId': 'b1', 'memberId': 'm1', 'status': 'returned'}
get loan 99     -> 404 {'error': 'loan 99 not found'}
```

### Lesson 02 — 2026-11-02 — `cd labs/L100/02-layered-structure && python3 -m unittest -v` (exit 0)
```text
test_service_has_no_infrastructure_imports (test_layers.DependencyDirectionTest.test_service_has_no_infrastructure_imports) ... ok
test_borrow_conflict_get_and_errors (test_layers.HttpTest.test_borrow_conflict_get_and_errors) ... ok
test_borrow_returns_active_loan (test_layers.InMemoryRulesTest.test_borrow_returns_active_loan) ... ok
test_member_loan_limit (test_layers.InMemoryRulesTest.test_member_loan_limit) ... ok
test_return_frees_the_book (test_layers.InMemoryRulesTest.test_return_frees_the_book) ... ok
test_same_book_cannot_be_borrowed_twice (test_layers.InMemoryRulesTest.test_same_book_cannot_be_borrowed_twice) ... ok
test_unknown_loan (test_layers.InMemoryRulesTest.test_unknown_loan) ... ok
test_borrow_returns_active_loan (test_layers.SqliteRulesTest.test_borrow_returns_active_loan) ... ok
test_member_loan_limit (test_layers.SqliteRulesTest.test_member_loan_limit) ... ok
test_return_frees_the_book (test_layers.SqliteRulesTest.test_return_frees_the_book) ... ok
test_same_book_cannot_be_borrowed_twice (test_layers.SqliteRulesTest.test_same_book_cannot_be_borrowed_twice) ... ok
test_unknown_loan (test_layers.SqliteRulesTest.test_unknown_loan) ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.591s

OK
```

### Lesson 02 — 2026-11-02 — `cd labs/L100/02-layered-structure && python3 try_it.py` (exit 0)
```text
[1] HTTP    borrow b2 by m1 -> 409 {'error': 'member m1 already has 1 loans'}
[1] service borrow b3 by m1 -> LoanLimitReached: member m1 already has 1 loans
[2] InMemoryLoanRepository   after returning loan 2, b4 gets loan id 4
[2] SqliteLoanRepository     after returning loan 2, b4 gets loan id 4
```

## Lesson 03

### Lesson 03 — 2026-11-02 — `cd labs/L100/03-modular-monolith && python3 check_boundaries.py` (exit 0)
```text
checked 7 files: 0 boundary violation(s)
```

### Lesson 03 — 2026-11-02 — `cd labs/L100/03-modular-monolith && python3 -m unittest -v` (exit 1)
```text
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/usr/lib/python3.12/unittest/__main__.py", line 18, in <module>
    main(module=None)
  File "/usr/lib/python3.12/unittest/main.py", line 104, in __init__
    self.parseArgs(argv)
  File "/usr/lib/python3.12/unittest/main.py", line 136, in parseArgs
    self._do_discovery([])
  File "/usr/lib/python3.12/unittest/main.py", line 253, in _do_discovery
    self.createTests(from_discovery=True, Loader=Loader)
  File "/usr/lib/python3.12/unittest/main.py", line 160, in createTests
    self.test = loader.discover(self.start, self.pattern, self.top)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/unittest/loader.py", line 266, in discover
    top_level_dir = os.path.abspath(top_level_dir)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen posixpath>", line 412, in abspath
FileNotFoundError: [Errno 2] No such file or directory
```

### Lesson 03 — 2026-11-02 — `cd labs/L100/03-modular-monolith && python3 try_it.py` (exit 0)
```text
[1] check_boundaries.py -> exit 1
    VIOLATION library/loans/shortcut.py:1 'loans' imports internals of 'catalog' (library.catalog.internal)
    checked 8 files: 1 boundary violation(s)
[1] python -m unittest -> exit 1; FAILED (failures=1)
    FAIL: test_real_code_has_no_violations (test_boundaries.BoundaryRuleTest.test_real_code_has_no_violations)
[2] importlib.import_module(...) -> exit 0; checked 8 files: 0 boundary violation(s)
```

### Lesson 03 — 2026-11-02 — `cd labs/L100/03-modular-monolith && python3 -m unittest -v` (exit 0)
```text
test_absolute_import_of_other_internals_is_caught (test_boundaries.BoundaryRuleTest.test_absolute_import_of_other_internals_is_caught) ... ok
test_importing_internal_as_name_is_caught (test_boundaries.BoundaryRuleTest.test_importing_internal_as_name_is_caught) ... ok
test_public_interface_and_own_internals_are_allowed (test_boundaries.BoundaryRuleTest.test_public_interface_and_own_internals_are_allowed) ... ok
test_real_code_has_no_violations (test_boundaries.BoundaryRuleTest.test_real_code_has_no_violations) ... ok
test_relative_import_of_other_internals_is_caught (test_boundaries.BoundaryRuleTest.test_relative_import_of_other_internals_is_caught) ... ok
test_reports_use_forward_slashes (test_boundaries.CrossPlatformPathTest.test_reports_use_forward_slashes) ... ok
test_windows_and_posix_paths_give_the_same_package (test_boundaries.CrossPlatformPathTest.test_windows_and_posix_paths_give_the_same_package) ... ok
test_borrow_and_return_through_public_interfaces (test_boundaries.ModulesWorkTogetherTest.test_borrow_and_return_through_public_interfaces) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.028s

OK
```

## Lesson 04

### Lesson 04 — 2026-11-02 — `cd labs/L100/04-api-first-openapi && python3 -m unittest -v` (exit 0)
```text
test_undeclared_status_and_bad_body_are_reported (test_contract.CheckerCatchesDriftTest.test_undeclared_status_and_bad_body_are_reported) ... ok
test_every_declared_response_is_exercised (test_contract.ContractTest.test_every_declared_response_is_exercised) ... ok
test_responses_match_spec (test_contract.ContractTest.test_responses_match_spec) ... ok
test_required_top_level_fields (test_contract.SpecShapeTest.test_required_top_level_fields) ... ok

----------------------------------------------------------------------
Ran 4 tests in 12.251s

OK
```

### Lesson 04 — 2026-11-02 — `cd labs/L100/04-api-first-openapi && (python3 server.py 18765 & SP=$!; sleep 2; python3 client_demo.py 18765; kill $SP)` (exit 0)
```text
GET  /health   -> 200 {'status': 'ok'}  contract: OK
POST /loans    -> 201 {'id': 1, 'bookId': 'b1', 'memberId': 'm1', 'status': 'active'}  contract: OK
POST /loans    -> 409 {'error': 'book b1 is already on loan'}  contract: OK
GET  /loans/1  -> 200 {'id': 1, 'bookId': 'b1', 'memberId': 'm1', 'status': 'active'}  contract: OK
```

### Lesson 04 — 2026-11-02 — `cd labs/L100/04-api-first-openapi && python3 try_it.py` (exit 0)
```text
[1] memberId renamed to member -> exit 1; FAILED (failures=2)
    FAIL: test_responses_match_spec (test_contract.ContractTest.test_responses_match_spec) (method='POST', path='/loans', expected=201)
    AssertionError: Lists differ: ["POST /loans 201: missing required field 'memberId'"] != []
    FAIL: test_responses_match_spec (test_contract.ContractTest.test_responses_match_spec) (method='GET', path='/loans/1', expected=200)
    AssertionError: Lists differ: ["GET /loans/{loanId} 200: missing required field 'memberId'"] != []
[2] POST /loans answered 500 -> ['POST /loans: status 500 not declared']
[2] POST /loans answered 409 -> []
```

## Lesson 05

### Lesson 05 — 2026-11-02 — `cd labs/L100/05-config-12factor && env -u LOANS_PORT python3 app.py` (exit 0)
```text
starting with Settings(port=8080, db_path='loans.db', max_active_loans=3, log_level='INFO')
smtp password: not set
```

### Lesson 05 — 2026-11-02 — `cd labs/L100/05-config-12factor && LOANS_PORT=9000 LOANS_LOG_LEVEL=debug LOANS_SMTP_PASSWORD=example-only python3 app.py` (exit 0)
```text
starting with Settings(port=9000, db_path='loans.db', max_active_loans=3, log_level='DEBUG')
smtp password: set
```

### Lesson 05 — 2026-11-02 — `cd labs/L100/05-config-12factor && LOANS_PORT=abc LOANS_LOG_LEVEL=LOUD python3 app.py; echo exit=$?` (exit 0)
```text
exit=2
invalid configuration: LOANS_PORT='abc' is not an integer; LOANS_LOG_LEVEL='LOUD' must be one of ['DEBUG', 'ERROR', 'INFO', 'WARNING']
```

### Lesson 05 — 2026-11-02 — `cd labs/L100/05-config-12factor && python3 -m unittest -v` (exit 0)
```text
test_env_name_case_rule_of_this_os (test_config.EnvNameCaseTest.test_env_name_case_rule_of_this_os) ... ok
test_all_errors_reported_together (test_config.LoadSettingsTest.test_all_errors_reported_together) ... ok
test_defaults_when_env_is_empty (test_config.LoadSettingsTest.test_defaults_when_env_is_empty) ... ok
test_env_overrides_defaults (test_config.LoadSettingsTest.test_env_overrides_defaults) ... ok
test_port_range_is_checked (test_config.LoadSettingsTest.test_port_range_is_checked) ... ok
test_secret_is_never_shown (test_config.LoadSettingsTest.test_secret_is_never_shown) ... ok
test_no_hardcoded_secret_assignments (test_config.NoSecretsInCodeTest.test_no_hardcoded_secret_assignments) ... ok
test_bad_config_fails_fast (test_config.StartupTest.test_bad_config_fails_fast) ... ok
test_good_config_starts (test_config.StartupTest.test_good_config_starts) ... ok

----------------------------------------------------------------------
Ran 9 tests in 10.359s

OK
```

### Lesson 05 — 2026-11-02 — `cd labs/L100/05-config-12factor && python3 try_it.py` (exit 0)
```text
[1] LOANS_LOG_LEVEL=warn -> exit 2: invalid configuration: LOANS_LOG_LEVEL='WARN' must be one of ['DEBUG', 'ERROR', 'INFO', 'WARNING']
[2] repr=True -> starting with Settings(port=8080, db_path='loans.db', max_active_loans=3, log_level='INFO', smtp_password='example-only')
[2] python -m unittest -> exit 1; FAILED (failures=2)
    FAIL: test_secret_is_never_shown (test_config.LoadSettingsTest.test_secret_is_never_shown)
    FAIL: test_good_config_starts (test_config.StartupTest.test_good_config_starts)
```

## Lesson 06

### Lesson 06 — 2026-11-02 — `cd labs/L100/06-documenting-architecture && python3 check_docs.py` (exit 0)
```text
OK   adr-001-sqlite-behind-repository.md
OK   c4-container.mmd
OK   c4-context.mmd
OK   workspace.dsl
```

### Lesson 06 — 2026-11-02 — `cd labs/L100/06-documenting-architecture && python3 -m unittest -v 2>&1 | tail -4` (exit 0)
```text
----------------------------------------------------------------------
Ran 16 tests in 6.769s

OK
```

### Lesson 06 — 2026-11-02 — `cd labs/L100/06-documenting-architecture && python3 -c "import shutil,pathlib,check_docs; w=pathlib.Path('/mnt/workspace/.copilot-state/1e67a17a-e6e7-4b32-b095-e8f8e0f4a9bd/session-state/host/files/aa_explain/scratch6'); shutil.rmtree(w,ignore_errors=True); shutil.copytree('doc/arch',w); p=w/'c4-context.mmd'; p.write_text(p.read_text().replace('Rel(loans, email,','Rel(loans, mail,')); import sys; sys.exit(check_docs.main(w))"; echo exit=$?` (exit 0)
```text
OK   adr-001-sqlite-behind-repository.md
OK   c4-container.mmd
FAIL c4-context.mmd
     - Rel uses undefined id 'mail'
OK   workspace.dsl
exit=1
```

### Lesson 06 — 2026-11-02 — `cd labs/L100/06-documenting-architecture && python3 try_it.py` (exit 0)
```text
[1] ADR status 'Reversed.' -> exit 1: FAIL adr-001-sqlite-behind-repository.md | - status must start with one of ('Proposed', 'Accepted', 'Deprecated', 'Superseded')
[1] ADR status 'Superseded by ADR 2.' -> exit 0: (all OK)
[2] DSL 'api -> cache' -> exit 1: FAIL workspace.dsl | - relationship uses undefined id 'cache'
```

### Lesson 06 — 2026-11-02 — `cd labs/L100/06-documenting-architecture && python3 agent_assist.py` (exit 0)
```text
model: fake model server (deterministic stand-in, not a language model)
next ADR number from doc/arch/: 2
attempt 1: REJECTED
  - agent drafts must have status 'Proposed' (a human accepts ADRs), got 'Accepted'
attempt 2: OK
--- draft (proposal only: a human reviews it, saves it under doc/arch/ and sets Accepted) ---
# ADR 2: Modules talk only through public interfaces

## Context

Library Loans is one deployable with two modules, catalog and loans. loans started to reach into catalog's internal store, so a storage change in catalog broke loans.

## Decision

We will let a module import only another module's package (its __init__), never its internal/ package. check_boundaries.py enforces this in CI and fails the build on a violation.

## Status

Proposed.

## Consequences

Modules can change their internals freely and could later be split out. New cross-module needs require a public function first, which adds a small amount of code.
---
fitness function (authoritative): checked 7 files: 0 boundary violation(s) (exit 0)
```

## Lesson 07

### Lesson 07 — 2026-11-02 — `cd labs/L200/07-hexagonal-architecture && python3 app.py --storage memory` (exit 0)
```text
storage=memory
cli  borrow b1 m1      -> 0 {"id": 1, "bookId": "b1", "memberId": "m1", "status": "active"}
http POST b1 by m2     -> 409 {'error': 'book b1 is already on loan'}
cli  return 1          -> 0 {"id": 1, "bookId": "b1", "memberId": "m1", "status": "returned"}
http GET /loans/1      -> 200 {'id': 1, 'bookId': 'b1', 'memberId': 'm1', 'status': 'returned'}
cli  show 99           -> 3 error: loan 99 not found
```

### Lesson 07 — 2026-11-02 — `cd labs/L200/07-hexagonal-architecture && python3 app.py --storage sqlite` (exit 0)
```text
storage=sqlite
cli  borrow b1 m1      -> 0 {"id": 1, "bookId": "b1", "memberId": "m1", "status": "active"}
http POST b1 by m2     -> 409 {'error': 'book b1 is already on loan'}
cli  return 1          -> 0 {"id": 1, "bookId": "b1", "memberId": "m1", "status": "returned"}
http GET /loans/1      -> 200 {'id': 1, 'bookId': 'b1', 'memberId': 'm1', 'status': 'returned'}
cli  show 99           -> 3 error: loan 99 not found
```

### Lesson 07 — 2026-11-02 — `cd labs/L200/07-hexagonal-architecture && python3 driving_cli.py --db /mnt/workspace/.copilot-state/1e67a17a-e6e7-4b32-b095-e8f8e0f4a9bd/session-state/host/files/aa_explain/demo.db borrow b1 m1; echo exit=$?; python3 driving_cli.py --db /mnt/workspace/.copilot-state/1e67a17a-e6e7-4b32-b095-e8f8e0f4a9bd/session-state/host/files/aa_explain/demo.db borrow b1 m2; echo exit=$?; python3 driving_cli.py --db /mnt/workspace/.copilot-state/1e67a17a-e6e7-4b32-b095-e8f8e0f4a9bd/session-state/host/files/aa_explain/demo.db return 1; echo exit=$?` (exit 0)
```text
{"id": 1, "bookId": "b1", "memberId": "m1", "status": "active"}
exit=0
error: book b1 is already on loan
exit=2
{"id": 1, "bookId": "b1", "memberId": "m1", "status": "returned"}
exit=0
```

### Lesson 07 — 2026-11-02 — `cd labs/L200/07-hexagonal-architecture && python3 -m unittest -v 2>&1 | grep -v ' ok$'` (exit 0)
```text

----------------------------------------------------------------------
Ran 19 tests in 34.901s

OK
```

### Lesson 07 — 2026-11-02 — `cd labs/L200/07-hexagonal-architecture && python3 try_it.py` (exit 0)
```text
[1] domain.py imports sqlite3 -> FAILED (failures=1): domain.py must depend on ports only, but imports ['sqlite3']
[2] isinstance(HalfStore(), ForStoringLoans) -> False
[2] borrow b1 -> loan 1 (still works)
[2] give_back(1) -> AttributeError: 'HalfStore' object has no attribute 'mark_returned'
```

### Lesson 07 — 2026-11-02 — `cd labs/L200/07-hexagonal-architecture && python3 -m unittest test_build_task -v` (exit 0)
```text
test_adapter_depends_only_on_the_hexagon (test_build_task.JsonFileStoreContractTest.test_adapter_depends_only_on_the_hexagon) ... ok
test_add_numbers_from_one (test_build_task.JsonFileStoreContractTest.test_add_numbers_from_one) ... ok
test_domain_rules_run_on_the_new_adapter (test_build_task.JsonFileStoreContractTest.test_domain_rules_run_on_the_new_adapter) ... ok
test_get_unknown_is_none (test_build_task.JsonFileStoreContractTest.test_get_unknown_is_none) ... ok
test_is_a_storing_port (test_build_task.JsonFileStoreContractTest.test_is_a_storing_port) ... ok
test_returned_loans_are_not_active (test_build_task.JsonFileStoreContractTest.test_returned_loans_are_not_active) ... ok

----------------------------------------------------------------------
Ran 6 tests in 4.818s

OK
```

## Lesson 08

### Lesson 08 — 2026-11-02 — `cd labs/L200/08-aggregates-invariants && python3 app.py` (exit 0)
```text
m1 borrows b1          -> ok, 1/3 active, version 1
m1 borrows b1 again    -> AlreadyBorrowed: member m1 already has b1
m1 borrows b2          -> ok, 2/3 active, version 2
m1 borrows b3          -> ok, 3/3 active, version 3
m1 borrows b4          -> LoanLimitReached: member m1 already has 3 loans
m2 borrows b1          -> BookAlreadyOnLoan: another member has that book on loan (UNIQUE constraint failed: loans.book_id)
m1 returns b1          -> ok, 2/3 active, version 4
m2 borrows b1          -> ok, 1/3 active, version 1
```

### Lesson 08 — 2026-11-02 — `cd labs/L200/08-aggregates-invariants && python3 -m unittest -v` (exit 0)
```text
test_limit (test_aggregate.MemberAggregateTest.test_limit) ... ok
test_no_double_loan_of_the_same_book (test_aggregate.MemberAggregateTest.test_no_double_loan_of_the_same_book) ... ok
test_outside_code_cannot_bypass_the_root (test_aggregate.MemberAggregateTest.test_outside_code_cannot_bypass_the_root) ... ok
test_return_frees_a_slot_and_keeps_history (test_aggregate.MemberAggregateTest.test_return_frees_a_slot_and_keeps_history) ... ok
test_cross_member_rule_is_enforced_by_the_database (test_aggregate.MemberRepositoryTest.test_cross_member_rule_is_enforced_by_the_database) ... ok
test_persists_in_a_file (test_aggregate.MemberRepositoryTest.test_persists_in_a_file) ... ok
test_round_trip (test_aggregate.MemberRepositoryTest.test_round_trip) ... ok
test_stale_copy_is_rejected (test_aggregate.MemberRepositoryTest.test_stale_copy_is_rejected) ... ok
test_unknown_member (test_aggregate.MemberRepositoryTest.test_unknown_member) ... ok
test_day_14_is_still_fine (test_build_task.OverdueInvariantTest.test_day_14_is_still_fine) ... ok
test_day_15_blocks_new_loans (test_build_task.OverdueInvariantTest.test_day_15_blocks_new_loans) ... ok
test_old_invariants_still_hold (test_build_task.OverdueInvariantTest.test_old_invariants_still_hold) ... ok
test_returning_the_overdue_book_unblocks (test_build_task.OverdueInvariantTest.test_returning_the_overdue_book_unblocks) ... ok

----------------------------------------------------------------------
Ran 13 tests in 9.723s

OK
```

### Lesson 08 — 2026-11-02 — `cd labs/L200/08-aggregates-invariants && python3 -m unittest -v test_aggregate.MemberRepositoryTest.test_stale_copy_is_rejected` (exit 0)
```text
test_stale_copy_is_rejected (test_aggregate.MemberRepositoryTest.test_stale_copy_is_rejected) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

### Lesson 08 — 2026-11-02 — `cd labs/L200/08-aggregates-invariants && python3 try_it.py` (exit 0)
```text
[1] with version check    -> ConcurrencyConflict: member m1 changed since version 1
[1] without version check -> saved; stored loans: ['b1', 'b2', 'b4'] (limit 3)
[2] no unique index: b1 is on loan to ['m1', 'm2'] at the same time
```

## Lesson 09

### Lesson 09 — 2026-11-02 — `cd labs/L200/09-event-driven-integration && python3 app.py` (exit 0)
```text
borrow b1 by m1 -> outbox pending: 1
borrow b1 by m2 -> BookAlreadyOnLoan; outbox pending: 1 (rolled back, no event)
return loan 1   -> outbox pending: 2
relay run 1     -> published 2: [('loanCreated', 'LoanCreated'), ('loanReturned', 'LoanReturned')]
relay run 2     -> published 0 (nothing pending)
notifications   -> ['to m1: you borrowed b1', 'to m1: thanks for returning b1']
projection      -> active loans per member {'m1': 0}
asyncapi.json   -> 2 events checked, problems: []
```

### Lesson 09 — 2026-11-02 — `cd labs/L200/09-event-driven-integration && python3 asyncapi_check.py` (exit 0)
```text
asyncapi.json: AsyncAPI 3.1.0, 2 channels, 2 operations: OK
```

### Lesson 09 — 2026-11-02 — `cd labs/L200/09-event-driven-integration && python3 -m unittest -v 2>&1 | tail -4` (exit 0)
```text
----------------------------------------------------------------------
Ran 20 tests in 2.011s

OK
```

### Lesson 09 — 2026-11-02 — `cd labs/L200/09-event-driven-integration && python3 try_it.py` (exit 0)
```text
[1] relay run 1 -> relay process killed; outbox pending: 1
[1] relay run 2 -> naive consumer sent 2 mails, idempotent consumer sent 1 (ignored 1 duplicate)
[2] bookId -> book: ["payload: missing required field 'bookId'", "payload: unexpected field 'book'"]
```

### Lesson 09 — 2026-11-02 — `cd labs/L200/09-event-driven-integration && python3 agent_assist.py` (exit 0)
```text
model: fake model server (deterministic stand-in, not a language model)
attempt 1: REJECTED
  - components.schemas.LoanOverduePayload: house rule - payload schema must list 'required' fields
  - operations.sendLoanOverdue: action must be 'send' or 'receive' (AsyncAPI 3), got 'publish'
  - sample event from code: payload.loanId: expected string, got int 7
  - sample event from code: payload.daysOverdue: expected string, got int 3
attempt 2: OK
proposal adds: channel loanOverdue (library.loans.overdue), operation sendLoanOverdue, message LoanOverdue
sample LoanOverdue event from code validates against the proposal: OK
asyncapi.json unchanged: True (a human reviews the proposal and edits the file)
```

## Lesson 10

### Lesson 10 — 2026-11-02 — `cd labs/L200/10-oidc-authentication && python3 app.py` (exit 0)
```text
mock IdP (LEARNING ONLY) at http://127.0.0.1:<port>
1 authorize request -> ['client_id', 'code_challenge', 'code_challenge_method', 'nonce', 'redirect_uri', 'response_type', 'scope', 'state']
2 redirect to RP    -> code of 43 chars, state matches: True
3 ID token accepted -> sub=member-m1 aud=library-web nonce ok, valid 300 s
4 same code again   -> LoginFailed: token endpoint 400: invalid_grant: code unknown or already used
```

### Lesson 10 — 2026-11-02 — `cd labs/L200/10-oidc-authentication && python3 -m unittest -v 2>&1 | grep -v ' ok$'` (exit 0)
```text

----------------------------------------------------------------------
Ran 19 tests in 5.591s

OK
```

### Lesson 10 — 2026-11-02 — `cd labs/L200/10-oidc-authentication && python3 try_it.py` (exit 0)
```text
[1] stolen code, wrong verifier -> token endpoint 400: invalid_grant: PKCE verification failed
[1] codes left at the IdP after the failed attempt -> 0
[2] aud=quiz-app -> aud ['quiz-app'] does not contain 'library-web'
```

### Lesson 10 — 2026-11-02 — `cd labs/L200/10-oidc-authentication && python3 -m unittest test_build_task 2>&1 | tail -3` (exit 0)
```text
Ran 5 tests in 0.798s

OK
```

## Lesson 11

### Lesson 11 — 2026-11-02 — `cd labs/L200/11-testing-pyramid && python3 pyramid.py` (exit 0)
```text
layer        tests  skipped  failed  total ms  mean ms
unit             8        0       0       2.9     0.34
integration      4        3       0   16819.8  4204.89
e2e              1        0       0    7061.0  7060.92
one e2e test costs about as much as 20,630 unit tests (about 10^4)
pyramid OK
```

### Lesson 11 — 2026-11-02 — `cd labs/L200/11-testing-pyramid && python3 try_it.py` (exit 0)
```text
[1] mean ms: unit 0.03, integration 119.06, e2e 15394.64 -> one e2e test = 481,818 unit tests (10^6)
[2] sqlite_store.py: bool(row[3]) -> row[3]      failed tests -> unit 0, integration 1, e2e 0
[2] http_api.py: BookAlreadyOnLoan 409 -> 422    failed tests -> unit 0, integration 0, e2e 1
```

### Lesson 11 — 2026-11-02 — `cd labs/L200/11-testing-pyramid && python3 -m unittest -v 2>&1 | tail -4` (exit 0)
```text
----------------------------------------------------------------------
Ran 20 tests in 18.604s

OK (skipped=3)
```

## Lesson 12

### Lesson 12 — 2026-11-02 — `cd labs/L300/12-cqrs-read-models (byte-identical scratch copy; the lab writes out/ files) && python3 app.py` (exit 0)
```text
write side : 40 commands -> 33 events, 7 rejected by the aggregate
read side  : consistency window from the projector log: p50 16.3 ms, p95 57.9 ms, max 58.1 ms (poll every 20 ms)
stale reads: 28 of 33 reads straight after the command did not see it yet
view       : {'m1': 2, 'm2': 3, 'm3': 2}
log        : out/projector.jsonl (33 lines); first: {"evt": "projected", "lag_ms": 20.3, "projector": "loans_view", "seq": 1, "type": "LoanCreated"}
rebuild    : replayed 33 events, view identical: True, drift: []
```

### Lesson 12 — 2026-11-02 — `cd labs/L300/12-cqrs-read-models (byte-identical scratch copy; the lab writes out/ files) && wc -l out/projector.jsonl; head -2 out/projector.jsonl` (exit 0)
```text
33 out/projector.jsonl
{"evt": "projected", "lag_ms": 20.3, "projector": "loans_view", "seq": 1, "type": "LoanCreated"}
{"evt": "projected", "lag_ms": 17.5, "projector": "loans_view", "seq": 2, "type": "LoanCreated"}
```

### Lesson 12 — 2026-11-02 — `cd labs/L300/12-cqrs-read-models (byte-identical scratch copy; the lab writes out/ files) && python3 failure_lab.py` (exit 0)
```text
base     projector.py: projector died at seq 31; restarted at position 33 of 33; drift: 2 row(s)
    member_loans[m3]: view 1, events say 2
    book_status[b6]: view None, events say 'm3'
    recovery: rebuild() -> drift []
solution projector.py: projector died at seq 31; restarted at position 33 of 33; drift: 0 row(s)
```

### Lesson 12 — 2026-11-02 — `cd labs/L300/12-cqrs-read-models (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest -v 2>&1 | tail -4` (exit 0)
```text
----------------------------------------------------------------------
Ran 11 tests in 0.342s

OK
```

### Lesson 12 — 2026-11-02 — `cd labs/L300/12-cqrs-read-models (byte-identical scratch copy; the lab writes out/ files) && CHECK_MINE=1 python3 -m unittest test_build_task 2>&1 | grep -E '^(FAIL|Ran|OK|FAILED)'` (exit 0)
```text
FAIL: test_checkpoint_does_not_move_past_a_crash (test_build_task.HardenedProjectorTest.test_checkpoint_does_not_move_past_a_crash)
FAIL: test_crash_then_restart_leaves_no_drift (test_build_task.HardenedProjectorTest.test_crash_then_restart_leaves_no_drift)
FAIL: test_replayed_event_changes_nothing (test_build_task.HardenedProjectorTest.test_replayed_event_changes_nothing)
Ran 3 tests in 0.011s
FAILED (failures=3)
```

### Lesson 12 — 2026-11-02 — `cd labs/L300/12-cqrs-read-models (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest test_build_task 2>&1 | tail -3` (exit 0)
```text
Ran 3 tests in 0.100s

OK
```

### Lesson 12 — 2026-11-02 — `cd labs/L300/12-cqrs-read-models (byte-identical scratch copy; the lab writes out/ files) && python3 try_it.py` (exit 0)
```text
[1] poll every  20 ms -> consistency window p50 13.1 ms, max 38.3 ms
[1] poll every 200 ms -> consistency window p50 123.3 ms, max 197.4 ms
[2] projector died at seq 31, after apply, before checkpoint
[2] restart -> drift: ['member_loans[m3]: view 3, events say 2']
```

## Lesson 13

### Lesson 13 — 2026-11-02 — `cd labs/L300/13-resilience-patterns (byte-identical scratch copy; the lab writes out/ files) && python3 app.py` (exit 0)
```text
# catalogue up: 3 borrows, 0 with fallback title, catalogue called 3x, breaker closed
{"calls": 6, "evt": "breaker", "failure_rate": 0.5, "from": "closed", "name": "catalogue", "to": "open"}
# catalogue down: 8 borrows, 8 with fallback title, catalogue called 3x, breaker open
{"evt": "breaker", "from": "open", "name": "catalogue", "to": "half_open"}
{"evt": "breaker", "from": "half_open", "name": "catalogue", "to": "open", "trial": "failed"}
# still down, after open_s: 1 borrows, 1 with fallback title, catalogue called 1x, breaker open
{"evt": "breaker", "from": "open", "name": "catalogue", "to": "half_open"}
{"evt": "breaker", "from": "half_open", "name": "catalogue", "to": "closed", "trial": "ok"}
# catalogue back, after open_s: 3 borrows, 0 with fallback title, catalogue called 3x, breaker closed
# transitions: closed -> open -> half_open -> open -> half_open -> closed
```

### Lesson 13 — 2026-11-02 — `cd labs/L300/13-resilience-patterns (byte-identical scratch copy; the lab writes out/ files) && python3 failure_lab.py` (exit 0)
```text
base     (one shared pool of 8): 8/24 borrows ok, 8 with fallback title
    per wave: {1: {'ok': 8}, 2: {'TimeoutError': 8}, 3: {'TimeoutError': 8}}
    first failed request log: {"degraded": false, "error": "TimeoutError: shared: no answer within 0.1 s", "evt": "request", "ms": 100.9, "ok": false, "pools": {"shared": "8/8"}, "wave": 2}
solution (members 4 + catalogue bulkhead 4): 24/24 borrows ok, 24 with fallback title
    per wave: {1: {'ok': 8}, 2: {'ok': 8}, 3: {'ok': 8}}
```

### Lesson 13 — 2026-11-02 — `cd labs/L300/13-resilience-patterns (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest -v 2>&1 | tail -4` (exit 0)
```text
----------------------------------------------------------------------
Ran 11 tests in 2.055s

OK
```

### Lesson 13 — 2026-11-02 — `cd labs/L300/13-resilience-patterns (byte-identical scratch copy; the lab writes out/ files) && CHECK_MINE=1 python3 -m unittest test_build_task 2>&1 | grep -E '^(FAIL:|Ran|OK|FAILED)'` (exit 0)
```text
FAIL: test_every_borrow_succeeds_with_a_fallback_title (test_build_task.BulkheadTest.test_every_borrow_succeeds_with_a_fallback_title)
FAIL: test_members_has_its_own_pool (test_build_task.BulkheadTest.test_members_has_its_own_pool)
Ran 3 tests in 0.865s
FAILED (failures=2)
```

### Lesson 13 — 2026-11-02 — `cd labs/L300/13-resilience-patterns (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest test_build_task 2>&1 | tail -3` (exit 0)
```text
Ran 3 tests in 0.780s

OK
```

### Lesson 13 — 2026-11-02 — `cd labs/L300/13-resilience-patterns (byte-identical scratch copy; the lab writes out/ files) && python3 try_it.py` (exit 0)
```text
[1] timeout 2.0 s: 24/24 ok, 8 degraded, fastest 1004 ms, slowest 2402 ms
[2] breaker went closed -> open; still {1: {'ok': 8}, 2: {'TimeoutError': 8}, 3: {'TimeoutError': 8}}
```

## Lesson 14

### Lesson 14 — 2026-11-02 — `cd labs/L300/14-consumer-driven-contracts (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest -v test_consumer` (exit 0)
```text
test_client_against_the_mock_provider_and_write_the_contract (test_consumer.ConsumerContractTest.test_client_against_the_mock_provider_and_write_the_contract) ... ok
test_mock_fails_when_an_interaction_is_never_exercised (test_consumer.ConsumerContractTest.test_mock_fails_when_an_interaction_is_never_exercised) ... ok
test_receipt_with_a_stub (test_consumer.ConsumerUnitTest.test_receipt_with_a_stub) ... ok

----------------------------------------------------------------------
Ran 3 tests in 1.092s

OK
```

### Lesson 14 — 2026-11-02 — `cd labs/L300/14-consumer-driven-contracts (byte-identical scratch copy; the lab writes out/ files) && python3 -c "import json;d=json.load(open('contracts/loans-service--catalogue-service.json'));print(d['consumer'],d['provider'],d.get('consumerVersion'),len(d['interactions']));print(json.dumps(d['interactions'][0],indent=1)[:900])"` (exit 0)
```text
loans-service catalogue-service None 2
{
 "description": "a request for an existing book",
 "providerState": "book b1 exists",
 "request": {
  "method": "GET",
  "path": "/books/b1"
 },
 "response": {
  "body": {
   "available": true,
   "id": "b1",
   "title": "Dune"
  },
  "matchingRules": {
   "$.available": "type",
   "$.title": "type"
  },
  "status": 200
 }
}
```

### Lesson 14 — 2026-11-02 — `cd labs/L300/14-consumer-driven-contracts (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest -v test_provider` (exit 0)
```text
test_get_book (test_provider.ProviderUnitTest.test_get_book) ... ok
test_every_consumer_contract_holds (test_provider.ProviderVerificationTest.test_every_consumer_contract_holds) ... ok

----------------------------------------------------------------------
Ran 2 tests in 7.251s

OK
```

### Lesson 14 — 2026-11-02 — `cd labs/L300/14-consumer-driven-contracts (byte-identical scratch copy; the lab writes out/ files) && python3 failure_lab.py` (exit 0)
```text
provider renames title -> name; base verifier (status only):
    provider unit test          PASS
    consumer unit test (stub)   PASS
    consumer in production      FAIL KeyError: 'title'
    contract verification       PASS
provider renames title -> name; solution verifier (body + matchers):
    provider unit test          PASS
    consumer unit test (stub)   PASS
    consumer in production      FAIL KeyError: 'title'
    contract verification       FAIL ['a request for an existing book: $.title: missing (the consumer reads it)']
```

### Lesson 14 — 2026-11-02 — `cd labs/L300/14-consumer-driven-contracts (byte-identical scratch copy; the lab writes out/ files) && CHECK_MINE=1 python3 -m unittest test_build_task 2>&1 | grep -E '^(FAIL:|Ran|OK|FAILED)'` (exit 0)
```text
FAIL: test_renamed_field_fails (test_build_task.VerifierTest.test_renamed_field_fails)
FAIL: test_retyped_field_fails_and_extra_field_passes (test_build_task.VerifierTest.test_retyped_field_fails_and_extra_field_passes)
Ran 3 tests in 4.515s
FAILED (failures=2)
```

### Lesson 14 — 2026-11-02 — `cd labs/L300/14-consumer-driven-contracts (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest test_build_task 2>&1 | tail -3` (exit 0)
```text
Ran 3 tests in 2.063s

OK
```

### Lesson 14 — 2026-11-02 — `cd labs/L300/14-consumer-driven-contracts (byte-identical scratch copy; the lab writes out/ files) && python3 try_it.py` (exit 0)
```text
[1] consumer adds isbn to its expectations -> ['a request for an existing book: $.isbn: missing (the consumer reads it)']
[2] provider adds isbn and returns another title -> []
```

### Lesson 14 — 2026-11-02 — `cd labs/L300/14-consumer-driven-contracts (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest 2>&1 | tail -3` (exit 0)
```text
Ran 8 tests in 17.218s

OK
```

### Lesson 14 — 2026-11-02 — `cd labs/L300/14-consumer-driven-contracts (byte-identical scratch copy; the lab writes out/ files) && python3 -c "import json;d=json.load(open('contracts/loans-service--catalogue-service.json'));print({k:v for k,v in d.items() if k!='interactions'}); print([i['description'] for i in d['interactions']])"` (exit 0)
```text
{'consumer': 'loans-service', 'metadata': {'consumerVersion': '1.4.0', 'format': 'lesson-14 contract v1'}, 'provider': 'catalogue-service'}
['a request for an existing book', 'a request for a missing book']
```

## Lesson 15

### Lesson 15 — 2026-11-02 — `cd labs/L300/15-slo-error-budgets (byte-identical scratch copy; the lab writes out/ files) && python3 app.py` (exit 0)
```text
log        : out/requests.jsonl, 25920 requests, 2026-10-25T12:00:00Z .. 2026-10-28T11:59:50Z
availability: SLI 3d 99.9884% vs SLO 99.9%; budget used in 3d: 1.2% of 30 days; burn rates {'5m': 0.0, '1h': 0.0, '6h': 0.0, '3d': 0.1}
latency 1h : {'mean': 147.9, 'p50': 42.9, 'p95': 94.3, 'p99': 2846.3, 'requests': 360}
mean check : OK
alerts     : none
```

### Lesson 15 — 2026-11-02 — `cd labs/L300/15-slo-error-budgets (byte-identical scratch copy; the lab writes out/ files) && tail -2 out/requests.jsonl` (exit 0)
```text
{"ts": "2026-10-28T11:59:40Z", "route": "GET /books", "status": 200, "ms": 28.4}
{"ts": "2026-10-28T11:59:50Z", "route": "GET /books", "status": 200, "ms": 38.9}
```

### Lesson 15 — 2026-11-02 — `cd labs/L300/15-slo-error-budgets (byte-identical scratch copy; the lab writes out/ files) && python3 failure_lab.py` (exit 0)
```text
last hour  : mean 147.9 ms, p95 94.3 ms, p99 2846.3 ms
base     slo.py (mean <= 200 ms): latency problems none; alerts none
solution slo.py (latency SLI): latency problems ['latency page: burn 19.7 over 1h/5m']; alerts [{'sli': 'latency', 'severity': 'page', 'windows': '1h/5m', 'burn_long': 19.7, 'burn_short': 33.3, 'threshold': 14.4}]
```

### Lesson 15 — 2026-11-02 — `cd labs/L300/15-slo-error-budgets (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest 2>&1 | tail -3` (exit 0)
```text
Ran 17 tests in 20.972s

OK
```

### Lesson 15 — 2026-11-02 — `cd labs/L300/15-slo-error-budgets (byte-identical scratch copy; the lab writes out/ files) && CHECK_MINE=1 python3 -m unittest test_build_task 2>&1 | grep -E '^(FAIL:|Ran|OK|FAILED)'` (exit 0)
```text
FAIL: test_slow_tail_pages_on_the_latency_sli (test_build_task.LatencySliTest.test_slow_tail_pages_on_the_latency_sli)
Ran 3 tests in 14.340s
FAILED (failures=1, errors=1)
```

### Lesson 15 — 2026-11-02 — `cd labs/L300/15-slo-error-budgets (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest test_build_task 2>&1 | tail -3` (exit 0)
```text
Ran 3 tests in 20.852s

OK
```

### Lesson 15 — 2026-11-02 — `cd labs/L300/15-slo-error-budgets (byte-identical scratch copy; the lab writes out/ files) && python3 try_it.py` (exit 0)
```text
[1] incident starts 10:30 -> first alert at 11:27 UTC (57 min later): [{'sli': 'latency', 'severity': 'page', 'windows': '1h/5m', 'burn_long': 16.4, 'burn_short': 20.0, 'threshold': 14.4}]
[2] 5% slow instead of 20%: latency burn rates {'5m': 0.0, '1h': 1.4, '6h': 0.2, '3d': 0.0}; alerts none
```

### Lesson 15 — 2026-11-02 — `cd labs/L300/15-slo-error-budgets (byte-identical scratch copy; the lab writes out/ files) && python3 agent_assist.py` (exit 0)
```text
model: fake model server (deterministic stand-in, not a language model)
facts (computed by code): evaluated_at=12:00 UTC, alert=latency page, windows=1h/5m, burn_rate=19.7, slow_since=10:34 UTC, p99_ms=2846.3, p95_ms=94.3, mean_ms=147.9, budget_used_1h=2.7%, availability_3d=99.9884%
attempt 1: REJECTED
  - number 1.97 is not in the facts
  - p99 is 2846.3, the draft says 147.9
  - burn rate is 19.7, the draft says 1.97
  - missing p99_ms 2846.3
  - missing burn_rate 19.7
attempt 2: OK
accepted draft (a human posts it):
  Incident summary: the latency page fired at 12:00 UTC (1h/5m windows, burn rate 19.7). From 10:34 UTC some POST /loans requests took seconds: p99 2846.3 ms in the last hour, while the mean was 147.9 ms and p95 94.3 ms. The last hour used 2.7% of the 30-day latency error budget. Availability stayed at 99.9884%.
```

### Lesson 15 — 2026-11-02 — `cd labs/L300/15-slo-error-budgets (byte-identical scratch copy; the lab writes out/ files) && CHECK_MINE=1 python3 -m unittest test_build_task 2>&1 | grep -E '^(FAIL:|ERROR:|[A-Za-z]*Error|Ran|OK|FAILED)'` (exit 0)
```text
ERROR: test_latency_slo_is_99_percent_of_post_loans_under_300_ms (test_build_task.LatencySliTest.test_latency_slo_is_99_percent_of_post_loans_under_300_ms)
KeyError: 'latency'
FAIL: test_slow_tail_pages_on_the_latency_sli (test_build_task.LatencySliTest.test_slow_tail_pages_on_the_latency_sli)
AssertionError: Lists differ: [] != [('latency', 'page', '1h/5m')]
Ran 3 tests in 9.991s
FAILED (failures=1, errors=1)
```

## Lesson 16

### Lesson 16 — 2026-11-02 — `cd labs/L300/16-performance-fitness-ci (byte-identical scratch copy; the lab writes out/ files) && python3 fitness.py; echo exit=$?` (exit 0)
```text
{"budget": "domain.py imports no adapters", "gate": "import-boundaries", "ok": true, "value": []}
{"budget": 2, "gate": "query-count", "ok": false, "value": {"10": 11, "500": 337}}
{"budget": 50, "gate": "micro-benchmark", "ok": true, "value": 2.33}
{"budget": 200, "gate": "response-time-p95", "ok": true, "value": {"errors": 0, "max_ms": 84.0, "p50_ms": 23.8, "p95_ms": 80.1, "requests": 40}}
fitness: FAILED query-count
exit=1
```

### Lesson 16 — 2026-11-02 — `cd labs/L300/16-performance-fitness-ci (byte-identical scratch copy; the lab writes out/ files) && python3 failure_lab.py` (exit 0)
```text
same report rows (unit-test view): True, 168 overdue loans
base     (after refactor): query-count {10: 11, 500: 337} -> FAIL; p95 52.4 ms -> PASS; with 0.5 ms round trips: 209.8 ms per report
    trace (10 loans), first 3: ['SELECT id, member_id, book_id, due FROM loans WHERE returned = 0 ORDER BY id', 'SELECT name FROM members WHERE id = 15', 'SELECT title FROM books WHERE id = 229']
solution (one JOIN)     : query-count {10: 1, 500: 1} -> PASS; p95 34.8 ms -> PASS; with 0.5 ms round trips: 1.4 ms per report
    trace (10 loans), first 3: ["SELECT l.id, m.name, b.title, l.due FROM loans l JOIN members m ON m.id = l.member_id JOIN books b ON b.id = l.book_id WHERE l.returned = 0 AND l.due < '2026-10-28' ORDER BY l.id"]
```

### Lesson 16 — 2026-11-02 — `cd labs/L300/16-performance-fitness-ci (byte-identical scratch copy; the lab writes out/ files) && CHECK_MINE=1 python3 -m unittest test_build_task 2>&1 | grep -E '^(FAIL:|ERROR:|Ran|OK|FAILED)'` (exit 0)
```text
FAIL: test_all_fitness_gates_pass (test_build_task.QueryBudgetTest.test_all_fitness_gates_pass)
FAIL: test_query_count_does_not_grow_with_the_data (test_build_task.QueryBudgetTest.test_query_count_does_not_grow_with_the_data)
Ran 3 tests in 6.035s
FAILED (failures=2)
```

### Lesson 16 — 2026-11-02 — `cd labs/L300/16-performance-fitness-ci (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest test_build_task 2>&1 | tail -3` (exit 0)
```text
Ran 3 tests in 0.376s

OK
```

### Lesson 16 — 2026-11-02 — `cd labs/L300/16-performance-fitness-ci (byte-identical scratch copy; the lab writes out/ files) && python3 fitness.py --solution; echo exit=$?` (exit 0)
```text
{"budget": "domain.py imports no adapters", "gate": "import-boundaries", "ok": true, "value": []}
{"budget": 2, "gate": "query-count", "ok": true, "value": {"10": 1, "500": 1}}
{"budget": 50, "gate": "micro-benchmark", "ok": true, "value": 2.11}
{"budget": 200, "gate": "response-time-p95", "ok": true, "value": {"errors": 0, "max_ms": 84.7, "p50_ms": 25.2, "p95_ms": 76.8, "requests": 40}}
fitness: all gates passed
exit=0
```

### Lesson 16 — 2026-11-02 — `cd labs/L300/16-performance-fitness-ci (byte-identical scratch copy; the lab writes out/ files) && (python3 http_api.py 18016 & SP=$!; sleep 3; python3 load_test.py http://127.0.0.1:18016/reports/overdue; kill $SP)` (exit 0)
```text
{"requests": 80, "errors": 0, "p50_ms": 22.4, "p95_ms": 81.9, "max_ms": 84.4}
```

### Lesson 16 — 2026-11-02 — `cd labs/L300/16-performance-fitness-ci (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest 2>&1 | tail -3` (exit 0)
```text
Ran 10 tests in 3.301s

OK
```

### Lesson 16 — 2026-11-02 — `cd labs/L300/16-performance-fitness-ci (byte-identical scratch copy; the lab writes out/ files) && python3 try_it.py` (exit 0)
```text
[1] in-process SQLite, 500 loans, best of 5 x 5 (ms per report): {'N+1': 3.4, 'JOIN': 0.41}
[2] domain.py imports sqlite3 -> {'gate': 'import-boundaries', 'ok': False, 'value': ['domain.py imports sqlite3'], 'budget': 'domain.py imports no adapters'}
```

## Lesson 17

### Lesson 17 — 2026-11-02 — `cd labs/L400/17-strangler-fig (byte-identical scratch copy; the lab writes out/ files) && python3 app.py` (exit 0)
```text
shadow : {'comparisons': 2000, 'mismatches': 108, 'candidate_errors': 0} in 23.9 s over HTTP
cutover: {'ready': False, 'mismatch_rate': 0.054, 'reasons': ['mismatch rate 5.40% > 0.10%']}
mismatch log: out/mismatches.jsonl (108 lines); first: {'days_late': 7, 'member_type': 'student', 'control': '0.63', 'candidate': '0.62'}
```

### Lesson 17 — 2026-11-02 — `cd labs/L400/17-strangler-fig (byte-identical scratch copy; the lab writes out/ files) && head -2 out/mismatches.jsonl` (exit 0)
```text
{"candidate": "0.62", "control": "0.63", "days_late": 7, "member_type": "student"}
{"candidate": "0.12", "control": "0.13", "days_late": 3, "member_type": "student"}
```

### Lesson 17 — 2026-11-02 — `cd labs/L400/17-strangler-fig (byte-identical scratch copy; the lab writes out/ files) && python3 failure_lab.py` (exit 0)
```text
base    : big-bang would charge 108 of 2000 wrong; shadow found 108 mismatches, members saw 0; cutover ready False ['mismatch rate 5.40% > 0.10%']
solution: big-bang would charge 0 of 2000 wrong; shadow found 0 mismatches, members saw 0; cutover ready True []
mismatching (type, days late), first 6: [('student', 3), ('student', 7), ('student', 11), ('student', 15), ('student', 19), ('student', 23)]
```

### Lesson 17 — 2026-11-02 — `cd labs/L400/17-strangler-fig (byte-identical scratch copy; the lab writes out/ files) && python3 fitness_legacy.py; echo exit=$?` (exit 0)
```text
{"budget": "<= 2 known callers, no new ones", "gate": "no-new-legacy-callers", "ok": true, "value": {"callers": 2, "migrated": [], "new": []}}
exit=0
```

### Lesson 17 — 2026-11-02 — `cd labs/L400/17-strangler-fig (byte-identical scratch copy; the lab writes out/ files) && CHECK_MINE=1 python3 -m unittest test_build_task 2>&1 | grep -E '^(FAIL:|ERROR:|Ran|OK|FAILED)'` (exit 0)
```text
FAIL: test_half_cent_rounds_up_like_the_monolith (test_build_task.ExtractedServiceTest.test_half_cent_rounds_up_like_the_monolith)
FAIL: test_parallel_run_allows_cutover (test_build_task.ExtractedServiceTest.test_parallel_run_allows_cutover)
Ran 3 tests in 0.038s
FAILED (failures=2)
```

### Lesson 17 — 2026-11-02 — `cd labs/L400/17-strangler-fig (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest test_build_task 2>&1 | tail -3` (exit 0)
```text
Ran 3 tests in 0.067s

OK
```

### Lesson 17 — 2026-11-02 — `cd labs/L400/17-strangler-fig (byte-identical scratch copy; the lab writes out/ files) && python3 app.py --solution` (exit 0)
```text
shadow : {'comparisons': 2000, 'mismatches': 0, 'candidate_errors': 0} in 2.9 s over HTTP
cutover: {'ready': True, 'mismatch_rate': 0.0, 'reasons': []}
canary 10%: routed {'legacy': 466, 'service': 34}
canary 50%: routed {'legacy': 255, 'service': 245}
service: all fine calls go to the extracted service; legacy fine code can be deleted next
```

### Lesson 17 — 2026-11-02 — `cd labs/L400/17-strangler-fig (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest 2>&1 | tail -3` (exit 0)
```text
Ran 12 tests in 14.835s

OK
```

### Lesson 17 — 2026-11-02 — `cd labs/L400/17-strangler-fig (byte-identical scratch copy; the lab writes out/ files) && python3 try_it.py` (exit 0)
```text
[1] new_feature.py imports the monolith -> {'gate': 'no-new-legacy-callers', 'ok': False, 'value': {'new': ['new_feature.py'], 'migrated': [], 'callers': 3}, 'budget': '<= 2 known callers, no new ones'}
[2] fixed service, 300 shadow requests -> {'ready': False, 'mismatch_rate': 0.0, 'reasons': ['only 300 comparisons (< 1000)']}
```

## Lesson 18

### Lesson 18 — 2026-11-02 — `cd labs/L400/18-multi-tenancy (byte-identical scratch copy; the lab writes out/ files) && python3 app.py` (exit 0)
```text
{"layout": "shared-schema", "isolation": {"rows": 700, "leaked": 686, "guard_violations": 1}, "noisy_neighbour": {"attempts": 20, "blocked": 20}, "migration": {"ddl_statements": 1, "files": 1, "ms": 36.6}}
{"layout": "schema-per-tenant", "isolation": {"rows": 14, "leaked": 0, "guard_violations": 1}, "noisy_neighbour": {"attempts": 20, "blocked": 20}, "migration": {"ddl_statements": 50, "files": 1, "ms": 372.1}}
{"layout": "db-per-tenant", "isolation": {"rows": 14, "leaked": 0, "guard_violations": 1}, "noisy_neighbour": {"attempts": 20, "blocked": 0}, "migration": {"ddl_statements": 50, "files": 50, "ms": 812.1}}
```

### Lesson 18 — 2026-11-02 — `cd labs/L400/18-multi-tenancy (byte-identical scratch copy; the lab writes out/ files) && python3 failure_lab.py` (exit 0)
```text
base    : lib00 overdue report returns 700 rows, 686 from other libraries; guard violations 1; static gate ok=False
    guard saw: SELECT id, member_id, book_id, due FROM loans WHERE due < '2026-10-28' ORDER BY id
solution: lib00 overdue report returns 14 rows, 0 from other libraries; guard violations 0; static gate ok=True
```

### Lesson 18 — 2026-11-02 — `cd labs/L400/18-multi-tenancy (byte-identical scratch copy; the lab writes out/ files) && python3 fitness_tenant.py; echo exit=$?` (exit 0)
```text
{"gate": "tenant-scoped-queries", "ok": false, "value": ["repository.py:8 SELECT id, member_id, book_id, due FROM {table} WHERE due < ? ORDER BY id"], "budget": 0}
exit=1
```

### Lesson 18 — 2026-11-02 — `cd labs/L400/18-multi-tenancy (byte-identical scratch copy; the lab writes out/ files) && CHECK_MINE=1 python3 -m unittest test_build_task 2>&1 | grep -E '^(FAIL:|ERROR:|Ran|OK|FAILED)'` (exit 0)
```text
FAIL: test_every_repository_call_passes_the_guard (test_build_task.TenantScopeTest.test_every_repository_call_passes_the_guard)
FAIL: test_overdue_report_sees_only_its_tenant (test_build_task.TenantScopeTest.test_overdue_report_sees_only_its_tenant)
FAIL: test_static_gate (test_build_task.TenantScopeTest.test_static_gate)
Ran 3 tests in 0.658s
FAILED (failures=3)
```

### Lesson 18 — 2026-11-02 — `cd labs/L400/18-multi-tenancy (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest test_build_task 2>&1 | tail -3` (exit 0)
```text
Ran 3 tests in 1.238s

OK
```

### Lesson 18 — 2026-11-02 — `cd labs/L400/18-multi-tenancy (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest 2>&1 | tail -3` (exit 0)
```text
Ran 9 tests in 2.719s

OK
```

### Lesson 18 — 2026-11-02 — `cd labs/L400/18-multi-tenancy (byte-identical scratch copy; the lab writes out/ files) && python3 try_it.py` (exit 0)
```text
[1] attached 10 tenant files, then: too many attached databases - max 10
[2] session lib00 queries tenant_id='lib01' -> 6 rows; guard violations ["SELECT id FROM loans WHERE tenant_id = 'lib01'"]
```

## Lesson 19

### Lesson 19 — 2026-11-02 — `cd labs/L400/19-policy-as-code (byte-identical scratch copy; the lab writes out/ files) && python3 app.py` (exit 0)
```text
policy policy/loans.rego (revision 58df760cbce4): 13/14 requirement cases
RBAC role table            : 7/14 requirement cases
  WRONG: librarian of another library (expected allowed=False)
decision log: out/decisions.jsonl, 14 lines; first: {"decision_id": "58df760cbce4-000001", "deny": [], "erased": ["/input/subject/email"], "input": {"action": "borrow", "resource": {"active_loans": 2, "member_id": "m1", "tenant": "lib00"}, "subject": {"id": "m1", "roles": ["member"], "tenant": "lib00"}}, "matched": ["allow@12", "allowed@44"], "path": "loans/authz/allowed", "result": true, "revision": "58df760cbce4", "timestamp": "2026-10-28T12:00:00Z"}
in-process decision: 86 us (varies by host)
```

### Lesson 19 — 2026-11-02 — `cd labs/L400/19-policy-as-code (byte-identical scratch copy; the lab writes out/ files) && head -1 out/decisions.jsonl` (exit 0)
```text
{"decision_id": "58df760cbce4-000001", "deny": [], "erased": ["/input/subject/email"], "input": {"action": "borrow", "resource": {"active_loans": 2, "member_id": "m1", "tenant": "lib00"}, "subject": {"id": "m1", "roles": ["member"], "tenant": "lib00"}}, "matched": ["allow@12", "allowed@44"], "path": "loans/authz/allowed", "result": true, "revision": "58df760cbce4", "timestamp": "2026-10-28T12:00:00Z"}
```

### Lesson 19 — 2026-11-02 — `cd labs/L400/19-policy-as-code (byte-identical scratch copy; the lab writes out/ files) && python3 failure_lab.py` (exit 0)
```text
request: {'action': 'view', 'subject': {'id': 's9', 'tenant': 'lib01', 'roles': ['librarian']}, 'resource': {'tenant': 'lib00', 'member_id': 'm2', 'active_loans': 1}}
base    : allowed=True matched=['allow@27', 'allowed@44']; policy tests failed: ['librarian of another library']
solution: allowed=False matched=[]; policy tests failed: []
```

### Lesson 19 — 2026-11-02 — `cd labs/L400/19-policy-as-code (byte-identical scratch copy; the lab writes out/ files) && python3 fitness_policy.py; echo exit=$?` (exit 0)
```text
{"gate": "policy-tests", "ok": false, "value": ["librarian of another library"], "budget": "14/14 pass"}
{"gate": "rule-coverage", "ok": true, "value": [], "budget": "every allow/deny rule"}
{"gate": "pep-coverage", "ok": true, "value": [], "budget": "0 handlers without authorize()"}
exit=1
```

### Lesson 19 — 2026-11-02 — `cd labs/L400/19-policy-as-code (byte-identical scratch copy; the lab writes out/ files) && CHECK_MINE=1 python3 -m unittest test_build_task 2>&1 | grep -E '^(FAIL:|ERROR:|Ran|OK|FAILED)'` (exit 0)
```text
FAIL: test_all_policy_gates (test_build_task.LibrarianScopeTest.test_all_policy_gates)
FAIL: test_librarian_of_another_library_is_denied (test_build_task.LibrarianScopeTest.test_librarian_of_another_library_is_denied)
Ran 3 tests in 0.010s
FAILED (failures=2)
```

### Lesson 19 — 2026-11-02 — `cd labs/L400/19-policy-as-code (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest test_build_task 2>&1 | tail -3` (exit 0)
```text
Ran 3 tests in 0.003s

OK
```

### Lesson 19 — 2026-11-02 — `cd labs/L400/19-policy-as-code (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest 2>&1 | tail -3` (exit 0)
```text
Ran 12 tests in 1.611s

OK
```

### Lesson 19 — 2026-11-02 — `cd labs/L400/19-policy-as-code (byte-identical scratch copy; the lab writes out/ files) && python3 try_it.py` (exit 0)
```text
[1] new renew() handler -> {'gate': 'pep-coverage', 'ok': False, 'value': ['renew'], 'budget': '0 handlers without authorize()'}
[2] suspended librarian borrows for m2 -> {'allowed': False, 'deny': ['account suspended'], 'matched': ['allow@27', 'deny@34']}
```

## Lesson 20

### Lesson 20 — 2026-11-02 — `cd labs/L400/20-evolutionary-migrations (byte-identical scratch copy; the lab writes out/ files) && python3 app.py` (exit 0)
```text
big_bang        : 36 failed requests of 100; first error: v1: no such column: name
expand_contract : 62 failed requests of 700; first error: v2: table members has no column named name
history: out/fitness.jsonl (python dashboard.py)
```

### Lesson 20 — 2026-11-02 — `cd labs/L400/20-evolutionary-migrations (byte-identical scratch copy; the lab writes out/ files) && python3 dashboard.py; echo exit=$?` (exit 0)
```text
plan / step                                                        fleet      errors unbackfilled  columns
big_bang / migrate all at once                                     v1v1v1v1        0            0  id,given_name,family_name
big_bang / deploy v3                                               v3v3v3v3       36            0  id,given_name,family_name  <-- errors=36 > 0
expand_contract / expand                                           v1v1v1v1        0          250  id,name,given_name,family_name
expand_contract / deploy v2 (dual write)                           v2v2v2v2        0          262  id,name,given_name,family_name
expand_contract / backfill                                         v2v2v2v2        0            0  id,name,given_name,family_name
expand_contract / flag read_split_name on                          v2v2v2v2        0            0  id,name,given_name,family_name
expand_contract / try contract: dropped name                       v2v2v2v2       50            0  id,given_name,family_name  <-- errors=50 > 0
expand_contract / deploy v3 (new columns only)                     v3v3v3v3       12            0  id,given_name,family_name  <-- errors=12 > 0
expand_contract / contract: dropped name                           v3v3v3v3        0            0  id,given_name,family_name
9 steps, 3 broke a fitness function
exit=1
```

### Lesson 20 — 2026-11-02 — `cd labs/L400/20-evolutionary-migrations (byte-identical scratch copy; the lab writes out/ files) && python3 failure_lab.py` (exit 0)
```text
base    : try contract: dropped name with fleet v2v2v2v2 -> 62 failed requests of 700; first: v2: table members has no column named name
solution: try contract: refused (instances on v2 still use members.name) with fleet v2v2v2v2 -> 0 failed requests of 700
big bang: schema changed in one step -> 36 failed requests of 100; first: v1: no such column: name
```

### Lesson 20 — 2026-11-02 — `cd labs/L400/20-evolutionary-migrations (byte-identical scratch copy; the lab writes out/ files) && CHECK_MINE=1 python3 -m unittest test_build_task 2>&1 | grep -E '^(FAIL:|ERROR:|Ran|OK|FAILED)'` (exit 0)
```text
FAIL: test_refuses_while_v2_instances_run (test_build_task.ContractGuardTest.test_refuses_while_v2_instances_run)
FAIL: test_zero_failed_requests_and_old_column_gone (test_build_task.ContractGuardTest.test_zero_failed_requests_and_old_column_gone)
Ran 3 tests in 0.063s
FAILED (failures=2)
```

### Lesson 20 — 2026-11-02 — `cd labs/L400/20-evolutionary-migrations (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest test_build_task 2>&1 | tail -3` (exit 0)
```text
Ran 3 tests in 0.008s

OK
```

### Lesson 20 — 2026-11-02 — `cd labs/L400/20-evolutionary-migrations (byte-identical scratch copy; the lab writes out/ files) && python3 app.py --solution` (exit 0)
```text
big_bang        : 36 failed requests of 100; first error: v1: no such column: name
expand_contract : 0 failed requests of 700; first error: -
history: out/fitness.jsonl (python dashboard.py)
```

### Lesson 20 — 2026-11-02 — `cd labs/L400/20-evolutionary-migrations (byte-identical scratch copy; the lab writes out/ files) && python3 dashboard.py --plan expand_contract; echo exit=$?` (exit 0)
```text
plan / step                                                        fleet      errors unbackfilled  columns
expand_contract / expand                                           v1v1v1v1        0          250  id,name,given_name,family_name
expand_contract / deploy v2 (dual write)                           v2v2v2v2        0          262  id,name,given_name,family_name
expand_contract / backfill                                         v2v2v2v2        0            0  id,name,given_name,family_name
expand_contract / flag read_split_name on                          v2v2v2v2        0            0  id,name,given_name,family_name
expand_contract / try contract: refused (instances on v2 still use members.name) v2v2v2v2        0            0  id,name,given_name,family_name
expand_contract / deploy v3 (new columns only)                     v3v3v3v3        0            0  id,name,given_name,family_name
expand_contract / contract: dropped name                           v3v3v3v3        0            0  id,given_name,family_name
7 steps, 0 broke a fitness function
exit=0
```

### Lesson 20 — 2026-11-02 — `cd labs/L400/20-evolutionary-migrations (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest 2>&1 | tail -3` (exit 0)
```text
Ran 10 tests in 0.158s

OK
```

### Lesson 20 — 2026-11-02 — `cd labs/L400/20-evolutionary-migrations (byte-identical scratch copy; the lab writes out/ files) && python3 try_it.py` (exit 0)
```text
[1] name TEXT NOT NULL -> 38 failed requests {'deploy v3 (new columns only)': 38}; first: v3: NOT NULL constraint failed: members.name
[2] today 2026-12-01 -> {'gate': 'no-expired-flags', 'ok': False, 'value': ['read_split_name'], 'budget': 0}
```

## Lesson 21

### Lesson 21 — 2026-11-02 — `cd labs/L400/21-capacity-planning (byte-identical scratch copy; the lab writes out/ files) && python3 app.py --solution` (exit 0)
```text
load model : {'avg_rps': 40.0, 'peak_rps': 120.0, 'mix': {'GET /books': 0.449, 'GET /loans': 0.351, 'POST /loans': 0.2}, 'mean_service_ms': 45.2}
Little's law: 120.0 req/s x 45.2 ms = 5.4 requests in flight at peak; emails 3.6 in flight -> 5 sender slots
{"option": "sync email", "mean_service_ms": 75.1, "capacity_rps": 35, "instances": 6, "p99_at_peak_ms": 230.8, "p99_one_down_ms": 239.1, "cost_per_million_usd": 4.17}
{"option": "async email", "mean_service_ms": 45.2, "capacity_rps": 75, "instances": 3, "p99_at_peak_ms": 102.4, "p99_one_down_ms": 130.4, "cost_per_million_usd": 2.08}
{"option": "async email + cache", "mean_service_ms": 32.6, "capacity_rps": 105, "instances": 3, "p99_at_peak_ms": 94.7, "p99_one_down_ms": 100.5, "cost_per_million_usd": 2.08}
```

### Lesson 21 — 2026-11-02 — `cd labs/L400/21-capacity-planning (byte-identical scratch copy; the lab writes out/ files) && python3 failure_lab.py` (exit 0)
```text
demand: avg 40.0 req/s, peak 120.0 req/s; one instance meets the SLO up to 75 req/s; raw c/S = 88.5 req/s
base    : 1 instance(s) -> at peak 120 req/s each, utilization 1.35, p99 58210.3 ms; one instance down: p99 58210.3 ms (SLO 300 ms)
solution: 3 instance(s) -> at peak 40 req/s each, utilization 0.45, p99 102.4 ms; one instance down: p99 130.4 ms (SLO 300 ms)
```

### Lesson 21 — 2026-11-02 — `cd labs/L400/21-capacity-planning (byte-identical scratch copy; the lab writes out/ files) && python3 fitness_capacity.py; echo exit=$?` (exit 0)
```text
{"gate": "capacity-n-plus-1", "ok": false, "budget": "p99 <= 300 ms with one down, peak <= 80% of capacity with one down", "value": {"instances": 1, "p99_one_down_ms": 58210.3, "peak_share_one_down": 1.6}}
exit=1
```

### Lesson 21 — 2026-11-02 — `cd labs/L400/21-capacity-planning (byte-identical scratch copy; the lab writes out/ files) && python3 fitness_capacity.py --solution; echo exit=$?` (exit 0)
```text
{"gate": "capacity-n-plus-1", "ok": true, "budget": "p99 <= 300 ms with one down, peak <= 80% of capacity with one down", "value": {"instances": 3, "p99_one_down_ms": 130.4, "peak_share_one_down": 0.8}}
exit=0
```

### Lesson 21 — 2026-11-02 — `cd labs/L400/21-capacity-planning (byte-identical scratch copy; the lab writes out/ files) && CHECK_MINE=1 python3 -m unittest test_build_task 2>&1 | grep -E '^(FAIL:|ERROR:|Ran|OK|FAILED)'` (exit 0)
```text
FAIL: test_six_instances_if_email_stays_synchronous (test_build_task.SizingTest.test_six_instances_if_email_stays_synchronous)
FAIL: test_slo_holds_with_one_instance_down (test_build_task.SizingTest.test_slo_holds_with_one_instance_down)
FAIL: test_three_instances_for_the_async_option (test_build_task.SizingTest.test_three_instances_for_the_async_option)
Ran 3 tests in 1.957s
FAILED (failures=3)
```

### Lesson 21 — 2026-11-02 — `cd labs/L400/21-capacity-planning (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest test_build_task 2>&1 | tail -3` (exit 0)
```text
Ran 3 tests in 0.622s

OK
```

### Lesson 21 — 2026-11-02 — `cd labs/L400/21-capacity-planning (byte-identical scratch copy; the lab writes out/ files) && python3 agent_assist.py` (exit 0)
```text
model: fake model server (deterministic stand-in, not a language model)
facts (computed by code): peak_rps=120.0, avg_rps=40.0, mean_service_ms=45.2, in_flight_at_peak=5.4, capacity_rps=75, instances=3, p99_at_peak_ms=102.4, p99_one_down_ms=130.4, cost_per_million_usd=2.08, email_senders=5, rejected_option=sync email, rejected_instances=6
attempt 1: REJECTED
  - number 1.8 is not in the facts
  - peak_rps is 120.0, the memo says 40.0
  - in_flight_at_peak is 5.4, the memo says 1.8
  - the plan is 3 instances, the memo says 1
  - missing peak_rps 120.0
  - missing instances 3
  - missing p99_one_down_ms 130.4
attempt 2: OK
accepted memo (a human reviews and signs it):
  Capacity memo: plan for a peak of 120.0 req/s (average 40.0 req/s). With a mean service time of 45.2 ms, Little's law gives 5.4 requests in flight at peak. One instance meets the p99 SLO up to a capacity of 75 req/s, so we recommend 3 instances (N+1): p99 102.4 ms at peak and 130.4 ms with one instance down, at a cost of 2.08 USD per million requests. Confirmation emails move to the outbox with 5 sender slots; the sync email option would need 6 instances.
```

### Lesson 21 — 2026-11-02 — `cd labs/L400/21-capacity-planning (byte-identical scratch copy; the lab writes out/ files) && python3 -m unittest 2>&1 | tail -3` (exit 0)
```text
Ran 10 tests in 13.472s

OK
```

### Lesson 21 — 2026-11-02 — `cd labs/L400/21-capacity-planning (byte-identical scratch copy; the lab writes out/ files) && python3 try_it.py` (exit 0)
```text
[1] 800 libraries (peak 240.0 req/s), async email: 5 instances, 1.74 USD per million requests
[1] 800 libraries (peak 240.0 req/s), async email + cache: 4 instances, 1.39 USD per million requests
[2] 2 instances (no spare), one down at peak: 120 req/s on the survivor, utilization 1.35, p99 58210.3 ms
```

## Lesson 22

### Lesson 22 — 2026-11-02 — `cd labs/L400/22-capstone (byte-identical scratch copy; the lab writes out/ files) && python3 run_capstone.py; echo exit=$?` (exit 0)
```text
{"milestone": "M1 strangle", "criterion": "fines parallel run", "measure": "mismatch rate over 2,000 shadow requests", "value": 0.0, "threshold": "<= 0.001", "pass": true}
{"milestone": "M1 strangle", "criterion": "fines cut over", "measure": "facade mode after the run", "value": "service", "threshold": "service", "pass": true}
{"milestone": "M1 strangle", "criterion": "no new legacy callers", "measure": "capstone files importing legacy_monolith", "value": [], "threshold": "[]", "pass": true}
{"milestone": "M2 tenancy", "criterion": "tenant guard", "measure": "statements without the current tenant id", "value": 0, "threshold": 0, "pass": true}
{"milestone": "M2 tenancy", "criterion": "tenant-scoped SQL", "measure": "loans queries without WHERE tenant_id", "value": [], "threshold": "[]", "pass": true}
{"milestone": "M2 tenancy", "criterion": "cross-library reads", "measure": "rows of another library returned", "value": 0, "threshold": 0, "pass": true}
{"milestone": "M3 policy", "criterion": "policy requirement cases", "measure": "cases decided as specified", "value": "14/14", "threshold": "14/14", "pass": true}
{"milestone": "M3 policy", "criterion": "cross-library probes denied", "measure": "probes allowed across libraries", "value": 0, "threshold": 0, "pass": true}
{"milestone": "M3 policy", "criterion": "every entry point enforces policy", "measure": "public methods without _authorize", "value": [], "threshold": "[]", "pass": true}
{"milestone": "M3 policy", "criterion": "decision log privacy", "measure": "decisions logged 615, with email", "value": 0, "threshold": 0, "pass": true}
{"milestone": "M4 events", "criterion": "outbox completeness", "measure": "committed changes vs outbox rows", "value": "469/469", "threshold": "equal", "pass": true}
{"milestone": "M4 events", "criterion": "relay published", "measure": "unpublished outbox rows", "value": 0, "threshold": 0, "pass": true}
{"milestone": "M4 events", "criterion": "idempotent consumers", "measure": "projection rows wrong after redelivering every event", "value": 0, "threshold": 0, "pass": true}
{"milestone": "M5 SLO + CI", "criterion": "availability SLI", "measure": "good / valid over 615 requests", "value": 1.0, "threshold": ">= 0.999", "pass": true}
{"milestone": "M5 SLO + CI", "criterion": "latency SLI", "measure": "good / valid over 615 requests", "value": 1.0, "threshold": ">= 0.99", "pass": true}
{"milestone": "M5 SLO + CI", "criterion": "burn-rate alerts", "measure": "alerts firing at the end of the run", "value": 0, "threshold": 0, "pass": true}
{"milestone": "M5 SLO + CI", "criterion": "consumer contract", "measure": "member-portal contract problems", "value": [], "threshold": "[]", "pass": true}
{"milestone": "M5 SLO + CI", "criterion": "capacity N+1", "measure": "p99 ms with one instance down", "value": 130.4, "threshold": "<= 300", "pass": true}
{"milestone": "M5 SLO + CI", "criterion": "ADR log", "measure": "ADRs in Nygard format of 9", "value": [], "threshold": "[]", "pass": true}
{"summary": true, "fault": null, "passed": 19, "total": 19, "failed": [], "verdict": "GO"}
exit=0
```

### Lesson 22 — 2026-11-02 — `cd labs/L400/22-capstone (byte-identical scratch copy; the lab writes out/ files) && python3 run_capstone.py --fault fines-rounding | grep -v '"pass": true'; echo exit=$?` (exit 0)
```text
{"milestone": "M1 strangle", "criterion": "fines parallel run", "measure": "mismatch rate over 2,000 shadow requests", "value": 0.054, "threshold": "<= 0.001", "pass": false}
{"milestone": "M1 strangle", "criterion": "fines cut over", "measure": "facade mode after the run", "value": "shadow", "threshold": "service", "pass": false}
{"summary": true, "fault": "fines-rounding", "passed": 17, "total": 19, "failed": ["fines parallel run", "fines cut over"], "verdict": "NO-GO"}
exit=0
```

### Lesson 22 — 2026-11-02 — `cd labs/L400/22-capstone (byte-identical scratch copy; the lab writes out/ files) && python3 run_capstone.py --fault cross-tenant-policy | grep -v '"pass": true'; echo exit=$?` (exit 0)
```text
{"milestone": "M2 tenancy", "criterion": "cross-library reads", "measure": "rows of another library returned", "value": 5, "threshold": 0, "pass": false}
{"milestone": "M3 policy", "criterion": "policy requirement cases", "measure": "cases decided as specified", "value": "13/14", "threshold": "14/14", "pass": false}
{"milestone": "M3 policy", "criterion": "cross-library probes denied", "measure": "probes allowed across libraries", "value": 5, "threshold": 0, "pass": false}
{"summary": true, "fault": "cross-tenant-policy", "passed": 16, "total": 19, "failed": ["cross-library reads", "policy requirement cases", "cross-library probes denied"], "verdict": "NO-GO"}
exit=0
```

### Lesson 22 — 2026-11-02 — `cd labs/L400/22-capstone (byte-identical scratch copy; the lab writes out/ files) && python3 run_capstone.py --fault unscoped-query | grep -v '"pass": true'; echo exit=$?` (exit 0)
```text
{"milestone": "M2 tenancy", "criterion": "tenant guard", "measure": "statements without the current tenant id", "value": 135, "threshold": 0, "pass": false}
{"milestone": "M2 tenancy", "criterion": "tenant-scoped SQL", "measure": "loans queries without WHERE tenant_id", "value": ["MEMBER_LOANS"], "threshold": "[]", "pass": false}
{"milestone": "M2 tenancy", "criterion": "cross-library reads", "measure": "rows of another library returned", "value": 20, "threshold": 0, "pass": false}
{"summary": true, "fault": "unscoped-query", "passed": 16, "total": 19, "failed": ["tenant guard", "tenant-scoped SQL", "cross-library reads"], "verdict": "NO-GO"}
exit=0
```

### Lesson 22 — 2026-11-02 — `cd labs/L400/22-capstone (byte-identical scratch copy; the lab writes out/ files) && python3 run_capstone.py --fault duplicate-delivery | grep -v '"pass": true'; echo exit=$?` (exit 0)
```text
{"milestone": "M4 events", "criterion": "idempotent consumers", "measure": "projection rows wrong after redelivering every event", "value": 20, "threshold": 0, "pass": false}
{"summary": true, "fault": "duplicate-delivery", "passed": 18, "total": 19, "failed": ["idempotent consumers"], "verdict": "NO-GO"}
exit=0
```

### Lesson 22 — 2026-11-02 — `cd labs/L400/22-capstone (byte-identical scratch copy; the lab writes out/ files) && python3 agent_assist.py --fault cross-tenant-policy` (exit 0)
```text
scorecard (computed by code): passed=16, total=19, failed=cross-library reads, policy requirement cases, cross-library probes denied, verdict=NO-GO
attempt 1: REJECTED
  - verdict is NO-GO, the note says GO
  - failed criterion not named: cross-library reads
  - failed criterion not named: policy requirement cases
  - failed criterion not named: cross-library probes denied
attempt 2: OK
accepted note (a human posts it):
  Release summary: NO-GO. 16 of 19 criteria passed; failed: cross-library reads, policy requirement cases, cross-library probes denied. Fix these before the release.
```

### Lesson 22 — 2026-11-02 — `cd labs/L400/22-capstone (byte-identical scratch copy; the lab writes out/ files) && wc -l out/requests.jsonl out/decisions.jsonl` (exit 0)
```text
   615 out/requests.jsonl
   615 out/decisions.jsonl
  1230 total
```

### Lesson 22 — 2026-11-02 — `cd labs/L400/22-capstone (byte-identical scratch copy; the lab writes out/ files) && python3 run_capstone.py --fault unscoped-query | tail -1; echo exit=${PIPESTATUS[0]}` (exit 0)
```text
{"summary": true, "fault": "unscoped-query", "passed": 16, "total": 19, "failed": ["tenant guard", "tenant-scoped SQL", "cross-library reads"], "verdict": "NO-GO"}
exit=1
```

## Lesson 23

### Lesson 23 — 2026-11-02 — `cd labs/L500/23-modularity-theory && python3 check_modularity.py; echo exit=$?` (exit 0)
```text
T1 strict layering <=> acyclic
  [OK] 2000/2000 random strictly layered graphs are acyclic
      (same-layer edges allowed: 1659/2000 graphs have a cycle - strictness matters)
  [OK] converse: longest-path layering of 2000 random DAGs has 0 violations
  [OK] layered (L100 #2): 4 edges, acyclic, layers {0: ['repository', 'service'], 1: ['handler'], 2: ['app']}
  [OK] hexagonal (L200 #7): 10 edges, acyclic, layers {0: ['ports'], 1: ['domain'], 2: ['driven_memory', 'driven_sqlite', 'driving_cli', 'driving_http'], 3: ['app']}
T2 the condensation (SCC graph) of any directed graph is acyclic
  [OK] 2000/2000 condensations acyclic (1634 of the inputs had cycles)
  [OK] hexagonal lab read WITH its __main__ blocks: cycle component [['app', 'driving_cli']] (driving_cli's entry block imports app, app imports driving_cli)
  [OK] seeded edge domain -> driving_http creates the cycle component [['domain', 'driving_http']]
T3 Martin metrics on Library Loans (L200 #7 hexagonal): I, A in [0,1]; distance to A + I = 1 is Dn / sqrt(2)
      module         Ca Ce      I     A     Dn  numeric d
      app             0  5  1.000  0.00  0.000     0.0000
      domain          5  1  0.167  0.00  0.833     0.5893
      driven_memory   1  1  0.500  0.00  0.500     0.3536
      driven_sqlite   1  1  0.500  0.00  0.500     0.3536
      driving_cli     1  1  0.500  0.00  0.500     0.3536
      driving_http    1  1  0.500  0.00  0.500     0.3536
      ports           1  0  0.000  1.00  0.000     0.0000
  [OK] all I and A in [0, 1]
  [OK] max |numeric distance - Dn/sqrt(2)| = 4.7e-12 (< 1e-5)
      mean Dn = 0.405; furthest from the main sequence: domain (stable and concrete: the 'zone of pain' corner)
Worked example: Parnas KWIC change impact (modules that must change per design decision)
      conventional        [1, 4, 4, 3, 2] total 14, worst 4
      information hiding  [1, 1, 1, 1, 1] total 5, worst 1
  [OK] information hiding: every decision is known by exactly one module
ALL CHECKS OK
exit=0
```

### Lesson 23 — 2026-11-02 — `cd research && python3 l500_checks.py 2>&1 | sed -n 1,12p` (exit 0)
```text
theorem checks:
  OK  23-modularity-theory/check_modularity.py (10 checks)
  OK  24-quality-attributes/check_quality.py (13 checks)
  OK  25-formal-reasoning/check_formal.py (13 checks)
problem-set numbers:
  OK  P23-3: I = 0.25, A = 0.25, Dn = 0.50
  OK  P23-4: domain I = 0.25, Dn = 0.75; ports A = 0.33, Dn = 0.67; mean Dn 0.405 -> 0.488
  OK  P23-5: 14 vs 5 module changes (2.8 vs 1.0 per decision)
  OK  P23-7: 72 possible edges, 26 allowed
  OK  P24-1: 21.6 min per 30 days, 4.38 h per year
  OK  P24-2: 99.341%, 284.7 min per 30 days
  OK  P24-3: 3 replicas (API tier 99.9999875%); system 99.840%
```

## Lesson 24

### Lesson 24 — 2026-11-02 — `cd labs/L500/24-quality-attributes && python3 check_quality.py; echo exit=$?` (exit 0)
```text
T1/T2 series = product, parallel = 1 - product of unavailabilities (independent components)
  [OK] Library Loans (LB, 2 API replicas, DB, IdP): formula 99.837569% = enumeration of 32 states 99.837569% (|diff| 1.1e-16)
  [OK] Monte Carlo 400,000 trials: 99.8363% within 4 sigma (0.0255%) of the formula
  [OK] one API instance: series 99.3409%; union bound 99.3400% <= A <= min 99.50%
      adding the 2nd API replica: 99.3409% -> 99.8376%; a 3rd: 99.8401% (the database is now the limit: 99.90%)
  [OK] 1-of-3 replicas at 99%: binomial 99.999900% = enumeration 99.999900%
  [OK] 2-of-3 replicas at 99%: binomial 99.970200% = enumeration 99.970200%
  [OK] 3-of-3 replicas at 99%: binomial 97.029900% = enumeration 97.029900%
  [OK] 1-of-n equals parallel([a]*n)
T3 nines -> downtime, and steady-state availability = MTTF / (MTTF + MTTR)
           SLO  min / 30 days  h / year
       99.000%         432.00    87.600
       99.900%          43.20     8.760
       99.950%          21.60     4.380
       99.990%           4.32     0.876
       99.999%           0.43     0.088
  [OK] each extra nine divides allowed downtime by 10: ratios [10.0, 10.0, 10.0]
  [OK] CACM example: 3 outages x 20 min = 60 min > 52.56 min allowed by 99.99%/year
  [OK] MTTF 720 h, MTTR 1 h, exponential repair: simulated up fraction 99.86079% vs formula 99.86130%
  [OK] MTTF 720 h, MTTR 1 h, uniform repair: simulated up fraction 99.86142% vs formula 99.86130%
T4 two criteria, weights (w, 1-w): at most one break-even weight w*; preference flips there
  [OK] SQLite (0.4, 0.9) vs replicated PostgreSQL (0.95, 0.5): w* = 0.4211; sweep flips at [0.4211]
  [OK] 2,000 random option pairs: sign changes match the formula (0 mismatches)
      utility tree, highest priority first (importance, difficulty):
        (H,H) availability: Primary database fails at peak; service restored within 5 min, no comm...
        (H,M) availability: Identity provider is down; members already signed in can still renew l...
        (H,M) interaction capability: A screen-reader user completes 'borrow a book' with keyboard only; WCA...
ALL CHECKS OK
exit=0
```

### Lesson 24 — 2026-11-02 — `cd research && python3 l500_checks.py 2>&1 | grep -E 'P24|P25|^OK|theorems'` (exit 0)
```text
  OK  P24-1: 21.6 min per 30 days, 4.38 h per year
  OK  P24-2: 99.341%, 284.7 min per 30 days
  OK  P24-3: 3 replicas (API tier 99.9999875%); system 99.840%
  OK  P24-4: 99.9997% (2-of-3) vs 99.9% (single)
  OK  P24-5: 99.8975% with the common cause vs 99.9975% assumed
  OK  P24-6: 99.861%; MTTR <= 0.360 h (21.6 min)
  OK  P24-7: w* = 0.421; at w = 0.6 PostgreSQL 0.770 vs SQLite 0.600
  OK  P25-4: post broken at 4 of 44 points, pre at 0
  OK  P25-5: 4 steps; 9 and 8 reachable states
  OK  P25-6: fixed 8, 20, 48, 112, 256; buggy 9, 27, 81, 243, 729
theorems checked: 10; problem numbers recomputed: 14; exam numbers: 15; problems: 38
OK
```

## Lesson 25

### Lesson 25 — 2026-11-02 — `cd labs/L500/25-formal-reasoning && python3 check_formal.py; echo exit=$?` (exit 0)
```text
T1 invariant induction: Inv(initial) and every operation preserves Inv => Inv in every reachable state
  [OK] base case: a new Member satisfies Inv
      310,352 random calls on the real L200 #8 Member aggregate, 178,288 rejected by rules
  [OK] Inv broken after 0 calls
  [OK] borrow postcondition broken 0 times
  [OK] rejected calls that changed state: 0
  [OK] loans is exposed as a read-only tuple (no append behind the root's back)
T2 Liskov rule: weaker-or-equal precondition and stronger-or-equal postcondition => safe substitution
      StrictLimit        pre broken at  0 of 44 points, post broken at  0; supertype client (overdue 0 / 1) ends with: [2, 0]
  [OK] StrictLimit: violations (0, 0) as predicted (0, 0)
      GenerousLimit      pre broken at  0 of 44 points, post broken at  8; supertype client (overdue 0 / 1) ends with: [5, 5]
  [OK] GenerousLimit: violations (0, 8) as predicted (0, 8)
      NoOverdueAccepted  pre broken at 33 of 44 points, post broken at  0; supertype client (overdue 0 / 1) ends with: [3, 'error: members with overdue loans are not accepted']
  [OK] NoOverdueAccepted: violations (33, 0) as predicted (33, 0)
  [OK] the client written for the supertype stays within 3 loans only with the valid subtype
T3 BFS model checking: explores every reachable state; the first violation found has a shortest trace
      buggy check-then-act: violation after exploring 9 states; counterexample: ['A reads: book free', 'B reads: book free', 'A borrows', 'B borrows']
  [OK] BFS counterexample length 4 = brute-force minimum 4
  [OK] atomic conditional insert: 8 reachable states, no violation, 0 deadlocks
  [OK] AG EF book available: from all 8 reachable states the book can become free again
      state explosion, members -> (buggy, fixed) reachable states: {2: (9, 8), 3: (27, 20), 4: (81, 48), 5: (243, 112), 6: (729, 256)}
  [OK] buggy = 3^n and fixed = (n + 2) * 2^(n - 1) for n = 2..6
ALL CHECKS OK
exit=0
```
