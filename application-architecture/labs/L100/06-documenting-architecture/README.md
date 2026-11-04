# Lab 06 – Documenting architecture (C4 as text + ADR)

Architecture docs live in `doc/arch/` next to the code, as plain text that is reviewed and
versioned like code: a C4 System Context and Container view (Mermaid C4 **and**
Structurizr DSL) plus one Architecture Decision Record in Michael Nygard's format.

## Files
| File | Purpose |
|---|---|
| `doc/arch/c4-context.mmd` | Mermaid `C4Context` – member, librarian, Library Loans, e-mail system |
| `doc/arch/c4-container.mmd` | Mermaid `C4Container` – Loans API + SQLite database inside the system boundary |
| `doc/arch/workspace.dsl` | Structurizr DSL – one model, two views (`systemContext`, `container`) |
| `doc/arch/adr-001-sqlite-behind-repository.md` | ADR 1 (Title, Context, Decision, Status, Consequences) |
| `check_docs.py` | Local structural lint: ADR sections/status, defined ids in relationships, balanced brackets |
| `test_docs.py` | Lint passes on real docs and catches typical mistakes |
| `puppeteer-config.json` | `--no-sandbox` for mermaid-cli on CI runners |
| `try_it.py` | Runs the lesson's two tryIt experiments and prints what happened (never edits the lab files) |
| `agent_assist.py` | Agent assist: a local model drafts ADR 2, code checks it (retry once), boundary checker has the last word |
| `test_agent_assist.py` | Agent-assist tests, against the deterministic fake model server only |
| `../../_shared/local_agent/` | Vendored stdlib chat client + fake model server (with one `[[ADR-DRAFT]]` rule) |

## Run (local, stdlib)
```bash
cd labs/L100/06-documenting-architecture
python check_docs.py
python -m unittest -v
```

## Render (optional locally, always in CI)
Use Podman (open source) or Docker with the same arguments. The Structurizr image is published for
linux/amd64 and linux/arm64, so it runs natively on the Apple-silicon Mac mini.
```bash
# Mac mini (zsh) - needs Node.js 24 LTS and a started Podman machine (lesson 1, step 6)
npx -p @mermaid-js/mermaid-cli@11.17.0 mmdc -i doc/arch/c4-context.mmd -o doc/arch/c4-context.svg
podman run --rm -v "$PWD/doc/arch:/usr/local/structurizr" docker.io/structurizr/structurizr:2026.09.19 validate -workspace /usr/local/structurizr/workspace.dsl
podman run -it --rm -p 8080:8080 -v "$PWD/doc/arch:/usr/local/structurizr" docker.io/structurizr/structurizr:2026.09.19 local
# then open http://localhost:8080
```
```powershell
# Windows PC (PowerShell) - Podman machine runs in WSL 2; Windows paths can be mounted directly
npx -p @mermaid-js/mermaid-cli@11.17.0 mmdc -i doc\arch\c4-context.mmd -o doc\arch\c4-context.svg
podman run --rm -v "${PWD}\doc\arch:/usr/local/structurizr" docker.io/structurizr/structurizr:2026.09.19 validate -workspace /usr/local/structurizr/workspace.dsl
podman run -it --rm -p 8080:8080 -v "${PWD}\doc\arch:/usr/local/structurizr" docker.io/structurizr/structurizr:2026.09.19 local
```
None of these were run in the sandbox (no Node packages, no container engine): see KNOWN-GAPS.

## Expected output (observed 2026-10-28, Python 3.12.15)
```
OK   adr-001-sqlite-behind-repository.md
OK   c4-container.mmd
OK   c4-context.mmd
OK   workspace.dsl
```
```
test_boundary_result_comes_from_the_checker (test_agent_assist.BoundaryStaysAuthoritativeTest.test_boundary_result_comes_from_the_checker) ... ok
test_main_never_writes_into_doc_arch (test_agent_assist.BoundaryStaysAuthoritativeTest.test_main_never_writes_into_doc_arch) ... ok
test_prompt_has_no_words_that_trigger_other_fake_rules (test_agent_assist.BoundaryStaysAuthoritativeTest.test_prompt_has_no_words_that_trigger_other_fake_rules) ... ok
test_first_draft_rejected_then_fixed_by_feedback (test_agent_assist.FakeModelLoopTest.test_first_draft_rejected_then_fixed_by_feedback) ... ok
test_one_attempt_only_leaves_the_draft_rejected (test_agent_assist.FakeModelLoopTest.test_one_attempt_only_leaves_the_draft_rejected) ... ok
test_accepted_status_is_rejected (test_agent_assist.ValidateDraftTest.test_accepted_status_is_rejected) ... ok
test_decision_must_name_the_check (test_agent_assist.ValidateDraftTest.test_decision_must_name_the_check) ... ok
test_good_draft_passes (test_agent_assist.ValidateDraftTest.test_good_draft_passes) ... ok
test_missing_section_is_rejected (test_agent_assist.ValidateDraftTest.test_missing_section_is_rejected) ... ok
test_wrong_number_is_rejected (test_agent_assist.ValidateDraftTest.test_wrong_number_is_rejected) ... ok
test_adr_bad_status (test_docs.LintCatchesMistakesTest.test_adr_bad_status) ... ok
test_adr_missing_consequences (test_docs.LintCatchesMistakesTest.test_adr_missing_consequences) ... ok
test_dsl_unbalanced_and_undefined (test_docs.LintCatchesMistakesTest.test_dsl_unbalanced_and_undefined) ... ok
test_mermaid_undefined_alias (test_docs.LintCatchesMistakesTest.test_mermaid_undefined_alias) ... ok
test_all_docs_pass (test_docs.RealDocsTest.test_all_docs_pass) ... ok
test_expected_files_are_stored_next_to_the_code (test_docs.RealDocsTest.test_expected_files_are_stored_next_to_the_code) ... ok

----------------------------------------------------------------------
Ran 16 tests in 2.981s

OK
```
After changing `Rel(loans, email,` to `Rel(loans, mail,` in `c4-context.mmd` (exit code 1):
```
OK   adr-001-sqlite-behind-repository.md
OK   c4-container.mmd
FAIL c4-context.mmd
     - Rel uses undefined id 'mail'
OK   workspace.dsl
```

**Rendering status: pending-ci.** No renderer was available locally (no mermaid-cli, no
Docker). The diagram syntax was checked by hand against the Mermaid C4 and Structurizr DSL
language reference; `.github/workflows/labs.yml` renders the `.mmd` files with mermaid-cli
11.17.0 and runs `structurizr validate`.

## Agent assist (local model drafts, code decides)
A local model (Ollama or llama.cpp server, OpenAI-compatible API at `http://localhost:11434/v1`) drafts
ADR 2 from Nygard's template and a short brief. `validate_draft()` is the judge: Nygard sections in order
(`check_adr`), the next free number, status `Proposed` (only a human accepts), and the Decision must name
its automated check `check_boundaries.py`. One retry sends the checker's findings back. The draft is
printed, never saved into `doc/arch/`. Finally lesson 3's `check_boundaries.py` runs: its exit code, not
the ADR text, says whether the code obeys the rule.
```bash
python agent_assist.py                    # deterministic fake model server (no download)
export LOCAL_MODEL_URL=http://localhost:11434/v1   # Windows: $env:LOCAL_MODEL_URL = "http://localhost:11434/v1"
export LOCAL_MODEL=qwen2.5:1.5b           # Windows: $env:LOCAL_MODEL = "qwen2.5:1.5b"
python agent_assist.py --real             # your local Ollama / llama.cpp server
```
Observed with the fake server (2026-10-28). Its first draft says `Accepted.` on purpose, to show the check:
```
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
A real model was not run here; its wording will differ, and the same checks apply.
**Caution:** the agent only proposes. Never paste secrets, keys or code you may not share into a prompt;
keep `LOCAL_MODEL_URL` on localhost.

## Try it (observed 2026-10-28, Python 3.12.15)
Predict first, then run. `try_it.py` never edits the lab files (code changes go to a temporary `.tryit-work/` copy that is deleted afterwards); the tasks and predictions are in the lesson's `tryIt` field.
```bash
python try_it.py
```
```
[1] ADR status 'Reversed.' -> exit 1: FAIL adr-001-sqlite-behind-repository.md | - status must start with one of ('Proposed', 'Accepted', 'Deprecated', 'Superseded')
[1] ADR status 'Superseded by ADR 2.' -> exit 0: (all OK)
[2] DSL 'api -> cache' -> exit 1: FAIL workspace.dsl | - relationship uses undefined id 'cache'
```

## Troubleshooting
| Symptom | Action |
|---|---|
| Mermaid renders boxes in an odd order | Mermaid C4 has no auto-layout; order of statements sets position. Reorder lines or use `UpdateLayoutConfig($c4ShapeInRow="3")`. |
| `mmdc` fails with a Chromium sandbox error on Linux | Pass `-p puppeteer-config.json` (contains `--no-sandbox`), as the CI job does. |
| Podman asks which registry to use for `structurizr/structurizr` | Use the fully qualified name `docker.io/structurizr/structurizr:2026.09.19`. |
| `agent_assist.py --real`: connection refused | Start Ollama (`brew services start ollama` / the Windows app) or run without `--real`. |
