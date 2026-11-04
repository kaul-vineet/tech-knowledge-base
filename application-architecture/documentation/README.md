# Application Architecture – L100 + L200 + L300 + L400 + capstone + L500 theory (applied, technology-agnostic)

**Status: not yet run on macOS or Windows; CI matrix pending.**

Full workstation setup (Mac mini + Windows 11, all topics): [`../../shared/WORKSTATION-SETUP.md`](../../shared/WORKSTATION-SETUP.md).

**Covers:** how to structure a small service so it stays changeable. You build one running
example, **Library Loans** (members borrow and return books), and grow it lesson by lesson.
Labs use Python 3.12 and its standard library only, and run on an Apple-silicon **Mac mini** (zsh) and a
**Windows 11 PC** (PowerShell). Each lesson lists the same idea in Spring, ASP.NET Core, Express and similar tools.

L100 means "run it": copy, run, observe. Hands-on leads: concept notes are short (≈20% of the
lesson words), and comments in the lab code name each concept where it happens.

## L100 lesson map
| # | Lesson | You run | Builds on | Lab | Validation | Tools |
|---|---|---|---|---|---|---|
| 1 | Set up your environment (Mac mini + Windows) | `check_env.py`, unittest, `run_all_labs.py` | – | `labs/L100/01-setup-workspace` | validated-local | – |
| 2 | Layered structure: presentation, service, repository | Loans API, in-memory → SQLite swap | 1 | `labs/L100/02-layered-structure` | validated-local | – |
| 3 | Modular monolith boundaries with a fitness function | `catalog` + `loans` modules, import rule check | 2 | `labs/L100/03-modular-monolith` | validated-local | import-linter |
| 4 | API-first with OpenAPI 3.1 | `openapi.json` → `http.server` → contract test | 2 | `labs/L100/04-api-first-openapi` | validated-local | Swagger Editor, Bruno |
| 5 | Configuration the 12-factor way | `LOANS_*` env vars (`export` and `$env:`), fail-fast validation | 2 | `labs/L100/05-config-12factor` | validated-local | – |
| 6 | Documenting architecture: C4 as text + ADR | Mermaid C4, Structurizr DSL, ADR 1, doc lint, **agent assist** (local model drafts ADR 2) | 2–5 | `labs/L100/06-documenting-architecture` | validated-local (lab, fake model); rendering pending-ci | Structurizr local |

## L200 lesson map ("build it")
L200 means "build it": each lab starts from working code, you add one feature (`buildTask`), and a test proves it.
Concept notes are longer (320–400 words, `content/concepts/L200/`, with a Trade-offs table), and each lesson
adds a `codeWalkthrough`. Content: `content/L200.json`. No new packages; reuse the lesson 1 setup.

| # | Lesson | You build | Builds on | Lab | Validation | Tools |
|---|---|---|---|---|---|---|
| 7 | Hexagonal architecture: ports and adapters | HTTP + CLI driving adapters, memory + SQLite driven adapters; **build:** JSON-file adapter | 2, 4 | `labs/L200/07-hexagonal-architecture` | validated-local | import-linter |
| 8 | Aggregates and invariants (DDD) | `Member` aggregate, one repository, version check; **build:** overdue rule | 7 | `labs/L200/08-aggregates-invariants` | validated-local | – |
| 9 | Event-driven integration | Outbox + relay + idempotent consumers, AsyncAPI 3.1.0 contract, **agent assist** (event schema); **build:** dead letters | 4, 8 | `labs/L200/09-event-driven-integration` | validated-local (fake model); official AsyncAPI CLI pending-ci | AsyncAPI Studio |
| 10 | Authentication with OIDC | Code flow + PKCE against a learning-only mock IdP, ID-token checks; **build:** `max_age` | 4 | `labs/L200/10-oidc-authentication` | validated-local; Keycloak pending-ci | Keycloak |
| 11 | Testing pyramid, measured | Unit / integration / e2e layers timed by `pyramid.py`; **build:** speed budgets | 7 | `labs/L200/11-testing-pyramid` | validated-local; Testcontainers pending-ci | Bruno |

**Tools** column: optional open-source learning tools (see, prototype, check) – details, installs and licences in
[`LEARNING-TOOLS.md`](LEARNING-TOOLS.md); each lesson's `learningTools` field has the exercise. Lessons that overlap
other topics carry a `seeAlso` field (lesson 4 ↔ ai-agents #10, lesson 9 ↔ distributed-systems #5/#8, lesson 10 ↔ cryptography #11).
`validation.pendingCi` lists, per lesson, the files and OS variants that have not run yet.

Each L200 lab has `solution/` and `test_build_task.py`. The check runs against the solution by default;
set `CHECK_MINE=1` (PowerShell: `$env:CHECK_MINE = "1"`) to check your own file.

## L300 lesson map ("harden it")
L300 means "harden it". Every lab starts from code that works on the happy path, and a seeded fault then makes it fail
(`failureLab`: fault, symptom, fix, proof). Your `buildTask` is the hardening change, and `test_build_task.py` fails on the base
file and passes on the fix. Each lesson also has a `tradeOffs` table and a 6–7 item `codeWalkthrough`. Concept notes are 450–550 words
(`content/concepts/L300/`, with a Failure modes section). Content: `content/L300.json`. Lessons 12, 13, 15 and 16 emit JSON-lines logs or
gate results that you read to diagnose. No new packages; pact-python and k6 are optional / CI only.

| # | Lesson | You harden | failureLab | Lab | Validation | Tools |
|---|---|---|---|---|---|---|
| 12 | CQRS and read models: projections that survive crashes | Projector: checkpoint + view in one transaction, idempotent handlers, rebuild, drift check | Projector dies at seq 31 → event lost | `labs/L300/12-cqrs-read-models` | validated-local | marimo |
| 13 | Resilience patterns: timeouts, circuit breaker, bulkhead, fallback | One bulkhead per dependency | Slow catalogue exhausts the shared pool (8/24 ok) | `labs/L300/13-resilience-patterns` | validated-local | Toxiproxy |
| 14 | Consumer-driven contract testing | Body + type-matcher verification | Provider renames `title` → consumer breaks, all unit tests green | `labs/L300/14-consumer-driven-contracts` | validated-local; Pact pending-ci | Bruno, Pact Broker (OSS) |
| 15 | SLOs and error budgets: burn-rate alerts from request logs | Latency SLI + multiwindow burn-rate alerts; **agent assist** (incident summary, every number checked) | Mean 148 ms looks fine, p99 2.8 s | `labs/L300/15-slo-error-budgets` | validated-local (fake model) | JupyterLab, Prometheus (promtool) |
| 16 | Performance and architecture fitness functions in CI | Query-count, import, benchmark and p95 gates; JOIN instead of N+1 | Refactor adds N+1 (337 statements) | `labs/L300/16-performance-fitness-ci` | validated-local; k6 pending-ci | Grafana k6, import-linter |

L300 `seeAlso`: lesson 12 ↔ distributed-systems L300 #14 (sagas), lessons 13 and 15 ↔ distributed-systems L300 #16 (backpressure),
lesson 13 ↔ ai-agents L300 #14 (the same circuit breaker). L200 #7–9 `next` name real L300 lessons; #10 now points at L400 #19.

## L400 lesson map ("design it") and capstone
L400 means "design it". Each lesson states a **design brief** (context, measurable constraints, the question), compares 2–3
**options** with evidence the lab generates, records the decision as an **ADR** (Nygard: title, Status, Context, Decision,
Consequences; log in `labs/L400/22-capstone/adr/README.md`) and keeps it true with a **fitness function**. Every lesson still has a
seeded `failureLab`, a `buildTask` with `CHECK_MINE=1`, `tradeOffs`, `scalingLimits` and two `tryIt`. Concept notes are 600–750 words
(`content/concepts/L400/`: Why it matters · Mental model · Design space · How to decide · Failure modes at scale · Common mistakes).
Content: `content/L400.json`. Stdlib only; OPA 1.21.4 is optional (CI).

| # | Lesson | You decide | failureLab | Fitness function | ADR | Validation | Tools |
|---|---|---|---|---|---|---|---|
| 17 | Strangler-fig decomposition: facade, branch by abstraction, parallel run, cut-over | Big bang vs facade + parallel run + canary | Rounding bug: 108 of 2,000 fines differ | no new legacy callers (ratchet) | 0001 | validated-local | import-linter, Structurizr (local) |
| 18 | Multi-tenancy: shared schema vs schema per tenant vs database per tenant | Layout per tier, guards | Report without tenant filter leaks 686 of 700 rows | tenant-scoped SQL + TenantGuard | 0002 | validated-local | JupyterLab |
| 19 | Policy as code: RBAC vs ABAC, policy tests and decision logs | RBAC (7/14) vs ABAC policy (14/14) | Librarian rule crosses libraries | policy tests, rule + PEP coverage | 0003 | validated-local; OPA pending-ci | Keycloak |
| 20 | Evolutionary architecture: expand/contract migrations, API versions, flags, fitness over time | Big bang (36/100 fail) vs guarded expand/contract (0/700) | Contract while v2 still writes: 62 failures | fitness history dashboard, flag expiry | 0004 | validated-local | Swagger Editor, JupyterLab |
| 21 | Cost and capacity planning: Little's law, benchmarks, headroom, cost per request | 6 vs 3 instances; cache later; **agent assist** (memo) | Sized on the average: p99 58 s at peak | capacity N+1 gate | 0005 | validated-local (fake model) | Grafana k6, JupyterLab |
| 22 | **Capstone:** Library Loans, production-ready | 19-criterion scorecard, GO/NO-GO; **agent assist** (release note) | 4 seeded faults, each NO-GO | scorecard + `test_faults.py` | 0006–0009 | validated-local (fake model) | Structurizr (local), Bruno, Prometheus |

L400 `seeAlso`: #17 ↔ L200 #7, #19 ↔ L200 #10 and ↔ #18, #20 ↔ L300 #14 and #16, #21 ↔ L300 #15 (both directions); one-way links to
distributed-systems (sharding, rate limiting, backpressure, sagas), simulation (Erlang C), cryptography (tokens) and ai-agents (tool safety, evals).

**Concept share** (REBALANCE-SPEC measure script, concept-note words vs the lesson objects, 2026-10-28 after the L400 build):
L100 1530 / 8072 = 15.9% (target 20–25%) · L200 2052 / 6708 = 23.4% (target 25–30%) · L300 2714 / 10264 = 20.9% (target 30–35%) ·
L400 4271 / 14996 = 22.2% (target 35–40%). All four are below target: the notes are at full length (L400 737–748 words, capstone 513),
and the hands-on side carries the code, failure labs, design fields and Mac/Windows steps. Notes were not padded and labs were not cut.

**Read the concepts first:** `documentation/CONCEPTS-PRIMER.md` covers the whole domain: a mental model,
the L100→L400 map, a glossary and common misconceptions. Each lesson then has a concept note in
`content/concepts/NN-*.md` (200–250 words: Why it matters, Mental model, How it works, Common mistakes;
each "How it works" point names the lab step that shows it). The lesson objects link to it through
`conceptNote` and `conceptSummary`. The numbers in the notes' worked examples come from `research/concept_examples.py`.

Lesson content (steps, expected results, troubleshooting, equivalents, sources) is in
`content/L100.json`. Each lesson also has `checkYourself` (shown with the checkpoint), two `tryIt`
experiments (task / predict / observed `expected`), one-line `inRealSystems` and `useWhen`, and `next`
(the L200 topic). Each lesson's `code` field is an exact copy of the main lab file.

## L500 lesson map ("theory & rigour") and assessment pack
L500 is the undergraduate theory companion: the mathematics and computer science the earlier lessons rest on, ethics and
primary literature. Lessons 23–25 follow **definitions → theorems with proofs → a numerical check in code → a problem set**;
every check runs here and its real output is pasted into `content/L500.json` (`theorems[].checkOutput`). Lesson 26 is a
structured ethics case, lesson 27 a reading seminar. Concept notes: `content/concepts/L500/`. Stdlib only.

| # | Lesson | Theorems (proved + checked) | Problems | Lab / check | Validation |
|---|---|---|---|---|---|
| 23 | Foundations I: modularity theory – information hiding, dependency graphs and Martin's metrics | strict layering ⇔ acyclic; condensation is a DAG; distance to the main sequence (on the real L200 #7 code) | 9 | `labs/L500/23-modularity-theory` | validated-local |
| 24 | Foundations II: quality attributes and trade-off analysis – ISO/IEC 25010, ATAM and availability maths | series bounds; parallel / k-of-n; nines and MTTF/(MTTF+MTTR); break-even weight | 9 | `labs/L500/24-quality-attributes` | validated-local |
| 25 | Foundations III: formal reasoning about design – contracts, Liskov substitution, model checking and the evidence | invariant induction (on the real L200 #8 `Member`); substitution rule; BFS shortest counterexample | 8 | `labs/L500/25-formal-reasoning` | validated-local |
| 26 | Ethics and professional responsibility: accessibility, privacy by design and honest technical debt | case study: WCAG 2.2 AA, GDPR Art. 25, ACM Code 2018 | 6 | – | content (sources retrieved) |
| 27 | Reading seminar: Parnas (1972) and the SEI ATAM report (2000) | 2 readings × 5 guiding questions + critical response | 6 | – | content (sources retrieved) |

Findings from the theory applied to our own code: the L200 #7 hexagonal lab is strictly layered, but reading its
`if __name__ == "__main__":` blocks adds the cycle {app, driving_cli} (problem P23-6); the hexagonal `domain` module is the
furthest from Martin's main sequence (Dn 0.833).

**Assessment pack** (`content/assessment/`): `syllabus.md` (14-week plan, weights labs 35 % / problem sets 25 % / two exams
20 % / capstone + oral defence + peer-reviewed ADRs 20 %, policies, outcomes mapped to CS2023 and ABET CAC/EAC),
`midterm.md`, `final.md` (with model answers and marks), `concept-inventory.json` (15 pre/post items),
`capstone-oral-defence.md`, `peer-review-adr.md`, `team-roles.md`. Question bank: `content/qbank/L500.json` (45 items).

**Checks (all exit 0):** `python research/l500_checks.py` (re-runs every theorem check, recomputes every problem-set and exam
number, checks structure and note lengths), `python research/check_l500_qbank.py` (qbank rules for L500 + concept
inventory), `python research/qbank_checks.py` (recomputes calculations and runs code-reading snippets, now L100–L500).

## How to run labs
Each lesson step has an OS-neutral `detail` plus `mac` (zsh) and `windows` (PowerShell) commands, and each
lesson has `platforms` (`expected` on both until the CI matrix runs). Inside an activated venv the commands below
are the same on both machines; use `\` in paths on Windows.
```bash
python --version                       # 3.12+
cd labs/L100/02-layered-structure      # any lab folder (labs/L200/... the same)
python -m unittest -v                  # run that lab's tests
python try_it.py                       # the lesson's two tryIt experiments (predict first)
cat README.md                          # run commands + real observed output
python ../01-setup-workspace/run_all_labs.py   # all labs
```
- No `pip install` is needed. pytest works too, but labs only rely on `unittest`.
- Tests that start a server bind to port 0 (any free port), so they do not clash with other processes.
- Optional tools: Node.js 24 (Maintenance LTS) for `npx` (mermaid-cli 11.17.0 in lesson 6, @asyncapi/cli 6.2.1 in lesson 9), and Podman or Docker for
  Structurizr 2026.09.19 (lesson 6), Keycloak 26.8.1 (lesson 10) and Testcontainers (lesson 11, `requirements-ci.txt`).
  What runs where, RAM/disk and GPU notes: `documentation/HARDWARE.md`.

## Agent assist (local model, lessons 6, 9, 15, 21 and the capstone)
`labs/L100/06-documenting-architecture/agent_assist.py` asks a **local** model (Ollama or llama.cpp server,
`http://localhost:11434/v1`) to draft ADR 2. Code decides: the Nygard checker, the next ADR number, status
`Proposed`, and the lesson 3 boundary checker as the last word. Tests use the vendored deterministic fake server
in `labs/_shared/local_agent/` (a copy of the KB's shared helper, plus documented `[[ADR-DRAFT]]`, `[[EVENT-SCHEMA]]` and
`[[INCIDENT-SUMMARY]]`, `[[CAPACITY-MEMO]]` and `[[GO-NO-GO]]` rules). Lesson 15's agent drafts an incident summary from SLO burn data;
lesson 21's drafts the capacity memo; the capstone's explains the release scorecard. Code checks every number and the verdict.

## CI
`.github/workflows/labs.yml` runs a matrix of `ubuntu-latest`, `macos-latest` (arm64) and `windows-latest`: every L100–L400 lab's
tests on Python 3.12, every `try_it.py`, the shared helper tests, the boundary check, `agent_assist.py` (fake model), and
lesson 5's env-var commands in zsh (macOS) and PowerShell (Windows). It renders the Mermaid C4 files with mermaid-cli
11.17.0 via `npx` (Node 24) on all three OSes and runs `structurizr validate` on Linux. L200 adds Linux jobs for the official
AsyncAPI CLI (lesson 9), a Keycloak 26.8.1 discovery check (lesson 10) and PostgreSQL via Testcontainers (lesson 11).
L300 adds the demos, failure labs and fitness gates to the matrix, plus Linux jobs for Pact (pact-python 4.2.0, lesson 14) and
k6 thresholds (`grafana/k6:2.3.0`, lesson 16).
L400 adds every L400 lab and the capstone to the matrix (tests, try-its, demos, failure labs, gates; the capstone must be GO without
faults and NO-GO with each seeded fault), plus a Linux job that runs OPA 1.21.4 (`opa test`, `opa_parity.py`) for lesson 19.
L500 adds a matrix step that runs every L500 lab's tests and `research/l500_checks.py`, `research/check_l500_qbank.py`
and `research/qbank_checks.py`.
The workflow assumes `application-architecture/` is the repository root. If it isn't, move the
file and set `DOMAIN_DIR`.

## Other files
- `documentation/VERIFIED-RESOURCES.md`: every source used, with its rubric score.
- `documentation/KNOWN-GAPS.md`: what could not be verified or run locally.
- `documentation/HARDWARE.md`: Mac mini vs Windows PC, RAM/disk, GPU.
- `documentation/LEARNING-TOOLS.md`: open-source learning tools per lesson, and tools not recommended.
- `research/L100-evidence.md` … `research/L500-evidence.md`: research questions, sources kept or dropped, key facts with URLs.
- `research/l500_checks.py`, `research/check_l500_qbank.py`: the L500 validators (see the L500 section).
- `research/L400_concept_examples.py`: the numbers in the L400 notes and ADRs (output in `research/L400-concept-examples-output.txt`).
- `research/L300_concept_examples.py`: the numbers in the L300 notes' worked examples (output in `research/L300-concept-examples-output.txt`).
- `research/L200_concept_examples.py`: computes the numbers in the L200 notes' worked examples (output in `research/L200-concept-examples-output.txt`).
