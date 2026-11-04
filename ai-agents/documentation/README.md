# AI Agents – applied engineering (L100 + L200 + L300 + L400 + capstone + L500 theory)

**Status: not yet run on macOS or Windows; CI matrix pending.**

**What this covers:** calling a language model over HTTP and building the smallest useful agent – prompt layout, JSON output you can trust, tool calls, and a bounded agent loop – without a framework.
Everything uses the chat-completions `POST /v1/chat/completions` wire format, so the same code runs against Ollama, llama.cpp, vLLM or a hosted API by changing `LOCAL_MODEL_URL` and `LOCAL_MODEL`.

Audience: software engineers who want to *apply* LLMs. L100 = run it: copy, run, observe.

## L100 lesson map
**Tools** = open-source learning tools for that lesson (see, build without code, check, inspect) – installs, licences and exercises: [`LEARNING-TOOLS.md`](LEARNING-TOOLS.md) and each lesson's `learningTools` field. They complement the labs; you still write the code.

| # | Level | Lesson | Lab folder | You will be able to… | Status | Tools |
|---|---|---|---|---|---|---|
| 1 | Setup | Set up your environment | `labs/L100/01-setup` | reach a local chat-completions endpoint (Ollama or the fake server) | validated-local | – |
| 2 | L100 | Call a model over HTTP | `labs/L100/02-call-model-http` | POST messages with `requests`/`urllib`, read content, finish_reason, usage | validated-local | Ollama, KNIME |
| 3 | L100 | Prompt structure | `labs/L100/03-prompt-structure` | use system vs user messages, few-shot examples, delimiters | validated-local | – |
| 4 | L100 | Structured output | `labs/L100/04-structured-output` | get JSON, validate in code, retry, use `response_format` | validated-local | promptfoo |
| 5 | L100 | Your first tool call | `labs/L100/05-first-tool-call` | declare a tool, run it locally, return the result | validated-local | promptfoo |
| 6 | L100 | A minimal agent loop | `labs/L100/06-minimal-agent-loop` | loop with a step budget, stop condition, logs, approval gate | validated-local | Langflow |

## L200 lesson map – build it
L200 = change and combine: each lab starts from working code, you add one feature (`buildTask`, with a solution and a test), and the concept notes go one level deeper (`content/concepts/L200/`). Lessons: `content/L200.json`.

| # | Lesson | Lab folder | You will be able to… | Status | Tools |
|---|---|---|---|---|---|
| 7 | Retrieval-augmented answers | `labs/L200/07-rag-answers` | chunk, embed (`/v1/embeddings`), cosine top-k with numpy, check citations | validated-local; sqlite-vec / pgvector equivalents pending-ci | Orange, Langflow |
| 8 | Agents with several tools | `labs/L200/08-multi-tool-agent` | pick among 3 tools, validate arguments with JSON Schema, return errors to the model | validated-local; jsonschema cross-check pending-ci | – |
| 9 | State and memory | `labs/L200/09-state-memory` | budget tokens, summarise to fit, save/recall facts in SQLite | validated-local | – |
| 10 | Build an MCP server and client | `labs/L200/10-mcp-server-client` | stdio JSON-RPC server + client per MCP 2026-07-28, 2025-11-25 fallback | validated-local; official SDK pending-ci | MCP Inspector, AnythingLLM |
| 11 | Guardrails basics | `labs/L200/11-guardrails` | allow-lists, argument limits, injection screening, approval, secret redaction | validated-local | promptfoo, Open WebUI (non-OSI) |

Install for L200 (adds numpy; needs Python 3.12): `python -m pip install -r labs/L200/requirements.txt` (same on macOS and in PowerShell). Optional cross-checks: `labs/L200/requirements-equivalents.txt` (jsonschema, sqlite-vec, mcp). Run all L200 tests: `for d in labs/L200/*/; do (cd "$d" && python -m unittest) || break; done`.
Agent assist (model proposes, code decides): lesson 8 (schema draft) and lesson 11 (risk labels).

## L300 lesson map – harden it
L300 = harden it: every lab starts from code that works on the happy path, injects a seeded, deterministic fault (`failureLab`: fault → symptom → fix → proof, the proof test fails before and passes after), and the build task is the hardening change: you edit a file that ships **unfixed** in the lab folder (`category_gate.py`, `latency_budget.py`, `circuit_breaker.py`, `resumable_gate.py`, `refund_session.py`); `BUILD_TARGET=mine python -m unittest -v test_build_task` (PowerShell `$env:BUILD_TARGET="mine"`) tests your file – it fails until you fix it – and without the variable the same test checks `solution/`. Lessons: `content/L300.json`; concept notes: `content/concepts/L300/`. All labs use `labs/L300/fake_server_l300.py` – the L100 fake server plus documented L300 rules (seeded faults, ticket triage, agent tools with injection/exfiltration, attack paraphrases); the shared `kb/shared/local_agent/` copy is untouched.

| # | Lesson | Lab folder | Failure lab (seeded) | Status | Tools |
|---|---|---|---|---|---|
| 12 | Evaluating agents with a golden set | `labs/L300/12-eval-golden-set` | a prompt "cleanup" silently breaks 2 of 20 cases → regression gate exits 1 | validated-local; promptfoo equivalent pending-ci | promptfoo |
| 13 | Tracing and observability | `labs/L300/13-tracing-observability` | a cold tool hides inside "the agent is slow" → GenAI spans name it | validated-local; OpenTelemetry SDK equivalent pending-ci | Orange, Jaeger |
| 14 | Reliability: timeouts, retries, budgets and fallbacks | `labs/L300/14-reliability-budgets` | 30 % 503 + 20 % 2 s stalls → naive loop hangs/overspends → hardened loop | validated-local | Toxiproxy |
| 15 | Safe tool execution | `labs/L300/15-safe-tool-execution` | timeout + retry refunds twice → idempotency key + SQLite approval queue + audit log | validated-local | Open WebUI (non-OSI) |
| 16 | Red-teaming prompt injection | `labs/L300/16-red-team-injection` | injected document makes the agent call an unapproved tool → policy layer + 8-case suite | validated-local; promptfoo red team / garak manual | promptfoo (local-first config), garak |

No new packages for the L300 labs (requests only). Optional cross-check: `python -m pip install -r labs/L300/requirements-equivalents.txt` (opentelemetry-sdk 1.45.1; same command on macOS and in PowerShell). Run all L300 tests: `for d in labs/L300/*/; do (cd "$d" && python -m unittest) || break; done` plus `(cd labs/L300 && python -m unittest test_fake_server_l300)`.
Structured logs/metrics the learner reads: `trace.jsonl` (13), `reliability.jsonl` (14), the SQLite audit log (15), `redteam_report.jsonl` (16). Agent assist (model proposes, code decides): lesson 16 (attack paraphrases).
Red-team tools stay local-first: promptfoo's red team uses promptfoo's hosted inference unless you set `PROMPTFOO_DISABLE_REMOTE_GENERATION=true` + `PROMPTFOO_DISABLE_TELEMETRY=1` and a local provider (`labs/L300/16-red-team-injection/promptfoo-redteam-local.yaml`; the npm download and promptfoo account/usage checks still go out); garak runs against Ollama only.

**Validation key:** `validated-local` = the lab and its tests ran in the Linux sandbox against the fake server (output pasted in the README). `validation.pendingCi` lists the files or variants of that lesson that have **not** run yet (real model, optional SDK/database equivalents, manual installs); they wait for the CI matrix or a manual run. `platforms` stays `expected` until CI has passed on macOS and Windows.

## L400 lesson map – design it
L400 = design it: each lesson gives a design brief with measurable constraints, measures 2-3 options on the fake server, records the decision as a Nygard ADR in the lab folder, and keeps it true with a fitness test (`test_fitness_*.py`). Lesson fields add `designBrief`, `options` (with measured evidence), `decisionRecord`, `fitnessFunction` and `scalingLimits`. Build tasks keep the L300 switch: the learner file ships unfixed; `BUILD_TARGET=mine python -m unittest -v test_build_task`. Lessons: `content/L400.json`; notes: `content/concepts/L400/`. All labs use `labs/L400/fake_server_l400.py` – the L300 fake server plus documented L400 rules (context limit, prefix cache, model registry with digests, ops tools and plan/route/split/results blocks, refund decisions, incident proposals); L100 and L300 files are untouched.

| # | Lesson | Lab folder | Decision (ADR) · fitness test | Status | Tools |
|---|---|---|---|---|---|
| 17 | Multi-agent patterns: when one agent with tools is enough | `labs/L400/17-multi-agent-patterns` | one agent by default, supervisor/worker only on predicted context overflow · 10/10, no extra tokens | validated-local | Langflow |
| 18 | Durable agent workflows: checkpoints, resume and exactly-once effects | `labs/L400/18-durable-workflows` | SQLite event history + keys + outbox; Temporal later · 12-point crash sweep, 0 duplicates | validated-local; Temporal equivalent pending-ci | Temporal CLI, Toxiproxy |
| 19 | Cost, latency and model choice | `labs/L400/19-cost-latency-model-choice` | rules + validated cascade, instructions first · 20/20 at <= 60 % cost | validated-local; real-hardware probe manual | Ollama |
| 20 | Deterministic core, LLM at the edge | `labs/L400/20-deterministic-core` | code decides, model proposes/explains · 600 hostile answers, 0 changed decisions | validated-local | promptfoo |
| 21 | Governance and evaluation in production | `labs/L400/21-governance-evals` | pin by digest, regression gate + red team + drift + audit · REJECT/ACCEPT, drift alarm, chain verify | validated-local | promptfoo, garak |
| 22 | An incident-triage agent (Capstone) | `labs/L400/22-capstone` | ADR-001..003 · scorecard (`run_capstone.py`), CI gate (`eval_capstone.py`), 6 milestone tests | validated-local | MCP Inspector, Orange |

Run all L400 tests: `for d in labs/L400/*/; do (cd "$d" && python -m unittest) || break; done` plus `(cd labs/L400 && python -m unittest test_fake_server_l400)`. The capstone and lessons 18/21 write SQLite files on every step: on a slow or network disk the suite takes several minutes. No new packages (lesson 7's numpy for the capstone's RAG); optional: `python -m pip install -r labs/L400/requirements-equivalents.txt` (temporalio 1.34.0). Agent assist (model proposes/explains, code decides): lesson 20 (explanations), 21 (upgrade-record draft), 22 (triage proposals).

## L500 lesson map – theory & rigour
L500 = the undergraduate theory companion: the mathematics, statistics and computer science the labs rest on, plus ethics and primary literature. Lessons 23-25 go definitions → results **with proofs** → a numerical check in code → a problem set; lesson 26 is a structured case analysis with primary law and professional codes; lesson 27 is a reading seminar. Lesson fields add `learningObjectives` (Bloom verbs), `theorems` (statement, proof, `check` command, real `checkOutput`), `problemSet` (worked solutions, marks), `caseStudy`, `readings` and `rubric`. Lessons: `content/L500.json`; notes: `content/concepts/L500/`; labs: `labs/L500/` (numpy for 23, standard library for 24-25; no model server needed).

| # | Lesson | Lab / material | Theorems (each checked in code) | Status |
|---|---|---|---|---|
| 23 | Foundations I: how language models work | `labs/L500/23-language-model-foundations` | softmax-with-temperature = max-entropy, dH/dT >= 0; Var(q.k) = d → 1/sqrt(d); Gibbs: counting minimises cross-entropy, PP = exp(H); truncated sampling = conditioning | validated-local |
| 24 | Foundations II: statistics for evaluating agents | `labs/L500/24-evaluation-statistics` | Wilson interval; sample size for a regression; McNemar exact test; union bound / Bonferroni | validated-local |
| 25 | Foundations III: decision theory and planning | `labs/L500/25-decision-planning` | retry cost and budgets; Bellman contraction; BFS/A* optimality; undecidability → allow-lists | validated-local |
| 26 | Ethics, society and professional responsibility for AI agents | case study (Moffatt v. Air Canada), ACM Code, NIST AI RMF, AI Act Art. 14/50, GDPR Art. 22 | – | validated-local (calculations) |
| 27 | Reading seminar: Attention Is All You Need and ReAct | guided questions + critical response | – | validated-local (calculations) |

Checks: `python research/l500_checks.py` (re-runs all 12 theorem checks, recomputes the 19 calculation problems and the exam numbers), `python research/check_l500_qbank.py` (L500 bank + concept inventory, same rules as `tools/check_qbank.py`), `python research/qbank_checks.py` (now L100-L500). Rebuild after edits: `python research/build_l500.py`, `python research/build_l500_qbank.py`.

**Assessment pack** (`content/assessment/`): `syllabus.md` (14 weeks, readings, L100-L500 → weeks, weights: labs 35 %, problem sets 25 %, two exams 20 %, capstone + oral defence + peer-reviewed ADRs 20 %; outcomes mapped to CS2023 and ABET CAC/EAC), `midterm.md`, `final.md` (model answers, marks), `concept-inventory.json` (15 pre/post items), `capstone-oral-defence.md`, `peer-review-adr.md`, `team-roles.md`. Question bank: `content/qbank/L500.json` (45 questions, 9 per lesson).

**Read first:** `documentation/CONCEPTS-PRIMER.md` (domain primer), then each lesson's concept note in `content/concepts/` before its lab (linked from `conceptNote` in `content/L100.json`).

**Concept share** (REBALANCE-SPEC measure script, concept-note words vs lesson-object words, 2026-10-28 after L400): L100 1,541 / 7,456 = 17.1 % (target 20–25 %); L200 2,050 / 9,983 = 17.0 % (target 25–30 %); L300 2,725 / 14,118 = 16.2 % (target 30–35 %); L400 + capstone 4,164 / 19,012 = 18.0 % (target 35–40 %). All below target because the hands-on side (code, mac/windows steps, codeWalkthrough, failureLab, options/evidence, learningTools, seeAlso, pendingCi) dominates; notes are at full length (wc -w: L100 242–249, L200 377–397, L300 483–548, L400 694–750, capstone 510) and were not padded (KNOWN-GAPS, R3-14).

Lesson content (schema per SPEC): `content/L100.json`. Sources: `documentation/VERIFIED-RESOURCES.md`. Research trail: `research/L100-evidence.md`. Open issues: `documentation/KNOWN-GAPS.md`.

## How to run the labs
Requirements: Python 3.10+ (validated on 3.12.15) and `requests==2.34.2`.

**A. Offline / tests – fake model server (no download, deterministic)**
```bash
pip install requests==2.34.2
python labs/L100/01-setup/fake_model_server.py --port 8765          # terminal 1
cd labs/L100/02-call-model-http                                     # terminal 2
LOCAL_MODEL_URL=http://127.0.0.1:8765/v1 LOCAL_MODEL=fake-model python call_model.py
python -m unittest -v      # every lab test starts its own fake server in a thread
```
Each lab also has `test_try_it_NN.py`: the lesson's two `tryIt` changes, run and asserted (predict first, then run it).
Run all tests like CI does: `for d in labs/L100/*/; do (cd "$d" && python -m unittest -v) || break; done`

**B. Optional manual run – real local model on the Mac mini or Windows PC**
Install exactly as in the shared page – Full workstation setup: [`../../shared/WORKSTATION-SETUP.md`](../../shared/WORKSTATION-SETUP.md).
```bash
brew install ollama && brew services start ollama   # macOS; Metal GPU on Apple silicon (server must run before pull)
# Windows: installer OllamaSetup.exe from https://ollama.com/download (winget Ollama.Ollama lags); NVIDIA/AMD GPU, else CPU
ollama pull qwen2.5:1.5b                       # ~1 GB, Apache-2.0, 'tools' capability
python labs/L100/01-setup/check_endpoint.py    # defaults: http://localhost:11434/v1
```
Scripts read `LOCAL_MODEL_URL` / `LOCAL_MODEL` (the same names as every other topic) and default to `http://localhost:11434/v1` and `qwen2.5:1.5b`; the older `BASE_URL` / `MODEL` still work as a fallback (the new names win). Real-model output differs in wording and is not guaranteed to follow instructions every time.
PowerShell sets variables with `$env:LOCAL_MODEL_URL="..."; $env:LOCAL_MODEL="..."`. Lesson 1 gives zsh and PowerShell commands for every step (fields `mac` / `windows`), including serving the Mac mini's model to the Windows PC over the LAN (`OLLAMA_HOST`).
Hardware, GPU support, model storage and RAM sizing: `documentation/HARDWARE.md`.

**Shared helper:** `kb/shared/local_agent/` (reused by the other topics' agent-assist labs) holds the same `fake_model_server.py` as lesson 1 (with an `EXTRA_RULES` marker hook, empty here) plus a stdlib `client.py`; `labs/L100/01-setup/test_shared_helper.py` keeps them identical. L200 extended it with documented rules (several tools, validation retry, injection, `<context>`/`<transcript>`/`<tool_spec>`/`<tool_list>` blocks) and `POST /v1/embeddings` + `/api/embed`; the shared copy was updated in the same change and L100 behaviour is unchanged (all L100 tests still pass).

**CI:** `.github/workflows/labs.yml` runs every L100–L500 lab test (L500: theorem checks, problem-set numbers and question banks via `research/l500_checks.py`, `check_l500_qbank.py`, `qbank_checks.py`) (L400 adds the shipped-build-task-must-fail check, the capstone eval gate and a `temporal` job) against the fake server (plus the lesson-12 gate as a real CI step: v1 must pass, v2 must be blocked) on `ubuntu-latest`, `macos-latest` (Apple silicon) and `windows-latest` on each push, re-checks the four concept-example outputs (L100–L400), runs the pending-ci equivalents (jsonschema, sqlite-vec, official MCP SDK, OpenTelemetry SDK) and the promptfoo golden-set run on all three OSes and pgvector in a Linux service container; a manual `workflow_dispatch` input `real_model=true` also installs Ollama 0.40.12 on Linux (CPU), pulls `qwen2.5:1.5b` and `embeddinggemma`, and runs each lab script.

## Two rules that run through every lesson
- Never give an agent destructive tools (delete, send, pay, shell) without human approval and least privilege.
- Keep decisions that must be deterministic – validation, permissions, budgets, arithmetic – in code, not in the model.
