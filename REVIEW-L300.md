# Review: L300 "Harden it" (lessons 12–16, 7 topics)

Reviewed 2026-10-28. Read-only review: the only file written in the KB is this report (running the tests created `__pycache__` folders and refreshed the lab log files the tests write).
Checked against L300-SPEC.md and the specs it references (SPEC, REBALANCE, PLATFORM-AGENT, L200, UPDATE-TOOLS-REVIEW), using the same method, format and severity scale as REVIEW-L100-L200.md.

## Executive summary

**Overall: strong. L300 is a real step up from L200. Every lesson injects a seeded fault, shows the symptom and proves the fix. I re-ran all 35 failure-lab proofs myself, and every one fails before the fix and passes after it. The weak spots are evidence (still nothing run on Mac or Windows), one flaky timing test, Wycheproof vectors taken from mirrors, and missing cross-topic links.**

- **Tests** (`python -m unittest -v <module>` from each test's folder):
  - 107 test files, **401 tests, 24 skipped** (SDK/tool paths that are pending-ci).
  - **Clean sequential run: 1 failure.** `ai-agents/labs/L300/13-tracing-observability/test_build_task.py` failed with `AssertionError: 2 != 1`: a chat span went over its 500 ms wall-clock budget (R3-02).
  - In my first run, a second copy of the suite was running at the same time by mistake. That run also failed `ai-agents 13 test_traced_agent` and `quantum 15 test_vqe`. The test_vqe failure happened because both copies wrote the same `logs/test_gd.jsonl` file (R3-15).
  - Everything else passed in both runs. The slowest file took 33 s (ai-agents 14).
- **Failure labs (fail-before / pass-after), proven by script, not taken from self-reports:**
  - **25 of 25** lessons that have a learner switch (`BUILD_TASK_MODULE`, `BUILD_IMPL`, `BUILD_TARGET=mine`, `CHECK_MINE=1`, `BUILD_FILE`) fail on the unfixed file and pass on the solution. The failure counts match the `failureLab.proof` text.
  - Simulation: `research/failure_proofs_L300.py` prints fault FAIL / fix PASS for all 5 lessons.
  - ai-agents: the paired fault/fix tests pass. However, ai-agents and simulation have no learner switch, and in those topics the fix is already written in the shipped code (R3-06).
- **Schema (checked by script):**
  - All 35 lessons have `failureLab` (all 4 keys), 2–3 `tradeOffs` rows, a `buildTask` whose solution file exists, 5–7 `codeWalkthrough` items, 2 `tryIt`, at most 2 `learningTools`, `platforms`, and `validation.pendingCi`.
  - `code` matches the lab file byte-for-byte in 35/35 lessons. Numbering is 12–16 in every topic.
  - Every L200 #11 `next` names the real L300 #12 title, and every L300 #16 `next` is "L400 (planned): …".
  - Gaps:
    - `seeAlso` is missing in 7 lessons (R3-04).
    - 7 tool names do not exactly match the catalog (R3-08).
    - 1 `buildTask.solution` value is not a path (R3-09).
- **Notes and concept share:**
  - Concept notes are 483–550 words (`wc -w`), and all have the required headings.
  - Every "→ see lab step N" points to a step that exists.
  - Concept share is **17.3–21.6 %** per topic. That is far below your 30–35 % target, and only cryptography reports it (R3-14).
- **Accuracy:** about 20 claims checked against official sources were correct (see "Verified correct").
  - Two problems: the trace-flags handling in the W3C traceparent lab (R3-12), and Wycheproof vectors copied from mirrors (R3-03).
- **Safety:**
  - All 7 L300 agent assists keep the decision in code, and their tests use only the fake model server.
  - The cryptography assist redacts, then gates, then sends, and never sends secret values.
  - The injection suite uses `attacker.test` placeholders and `$SECRET` tokens rather than working exploits.
  - Scope is civilian throughout.
  - One privacy gap: promptfoo's red-team mode uses Promptfoo's hosted inference by default (R3-07).
- **Cross-platform scan (AST + regex over all L300 `.py` files):**
  - No POSIX-only calls, `/tmp`, `shell=True` or `0.0.0.0` binds in code.
  - Every text-mode file read or write sets `encoding="utf-8"`.
  - `multiprocessing` uses the `spawn` context with `__main__` guards.
  - Wall-clock assertions are loose, except ai-agents 13 (R3-02).

**Findings by severity: High 1 · Medium 6 · Low 13 (20 in total).**

## Method (reproducible)

The scripts and raw outputs are in the session folder `files/review_l300/`:
- `schema300.py`: fields, code against file, numbering, next, tools against the catalog, word counts, headings, step references, concept share;
- `run_tests300.py`: writes `test_results300_run1.json` (overlapping run) and `test_results300_run2.json` (clean run);
- `proofs.py`: fail-before/pass-after for 25 labs, plus the simulation proof script; writes `proofs.log`;
- `xplat300.py`: cross-platform scan;
- `urls300.json`: 346 L300 URLs grouped by domain.

I re-ran the timing-sensitive ai-agents 13 tests 11 more times on their own, including under CPU load; all of those passed.
Official sources fetched:
- PyPI: pact-python, SALib, mitiq, PennyLane.
- PennyLane `qp` announcement and release notes.
- Google SRE Workbook, "Alerting on SLOs".
- W3C Trace Context REC.
- The open-telemetry/semantic-conventions-genai repository.
- docs.rs feature list for embassy-nrf.
- Homebrew formula page for toxiproxy.
- Promptfoo red-team inference and data-handling docs.

## Verified correct (sample)

| Claim in KB | Official evidence |
|---|---|
| pact-python 4.2.0 (MIT, Python ≥ 3.11) | PyPI: released 2026-10-22, latest |
| SALib 1.6.0. The lab uses the current `SALib.sample.sobol` / `analyze.sobol` / `morris` API, not the deprecated `saltelli` sampler. | PyPI: 2026-09-19, MIT |
| mitiq 1.1.0 is GPL-3.0 and requires Python ≥ 3.11 and < 3.13, so it gets its own venv. API: `zne.execute_with_zne`, `fold_gates_at_random(fidelities=)`, `Richardson/LinearFactory`, `rem.*` | PyPI 2026-09-03 ("Requires Python <3.13, >=3.11"); README technique table |
| PennyLane 0.45.1; "docs now use `import pennylane as qp`" | PyPI 2026-06-26; PennyLane blog of 2026-03-19 announcing `qp` |
| Burn rates 14.4 (1 h / 5 m, page), 6 (6 h / 30 m, page) and 1 (3 d / 6 h, ticket); short window = 1/12 of the long one; "Table 5-8" | SRE Workbook ch. 5, Table 5-8 and Figure 5-6 |
| traceparent `00-<32 lowercase hex>-<16 lowercase hex>-<2 hex>`. All-zero ids and uppercase are invalid, and an invalid header starts a new trace. | W3C Trace Context REC §3.2.2 and §4.3 |
| Raft: the election restriction compares (last term, last index) as a tuple (§5.4.1), and a leader commits only entries from its own term by counting replicas (§5.4.2) | Raft paper. The `solution_raft.py` logic matches. |
| OTel GenAI conventions live in `open-telemetry/semantic-conventions-genai`, status Development. Attributes `gen_ai.provider.name`, `gen_ai.operation.name`, `gen_ai.tool.call.id` | The GitHub repository exists and is active |
| embassy-nrf 0.11.0 has the features `nrf52833`, `time-driver-rtc1`, `gpiote`, `unstable-pac`, `time` | docs.rs feature list |
| paho-mqtt 2.x: `Client(CallbackAPIVersion.VERSION2, …)`, `wait_for_publish` | paho-mqtt 2.x API (used correctly in `mqtt_bridge.py`) |
| CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF) | Recomputed: the check value of "123456789" is 0x29B1, as the catalogue lists (current name CRC-16/IBM-3740) |
| SPSA gains α = 0.602 and γ = 0.101 | Spall / JHU APL SPSA page (the lab cites it) |
| FMI 3.0.2 is current; OpenModelica supports FMI 2.0 and has experimental 3.0, so the lab exports FMI 2.0 CS | Consistent with the evidence file; the lab uses `buildModelFMU(version="2.0", fmuType="cs")` |
| `brew install toxiproxy` (homebrew-core, 2.12.0) | formulae.brew.sh |
| nRF52 addresses: TIMER1 0x40009000, UART0 0x40002000 | nRF52 memory map |

Not re-verified here: Renode 1.17.0, cosign v3.1.4, OpenBao 2.7.2, opentelemetry-sdk 1.45.1, promptfoo 0.125.1, k6 v2.3.0, embassy-executor 0.10.0 feature names (the docs.rs page was blocked), and the nRF52833 1.5 µA figure.

## Findings

Severity: **High** = a stated user goal or a hard spec rule is not met · **Med** = misleading, inconsistent or fragile; fix before publishing · **Low** = polish.

| ID | Topic | Lesson | Sev | Finding | Evidence | Fix |
|---|---|---|---|---|---|---|
| R3-01 | all (quantum, microbit worst) | 12–16 | **High** | **Still nothing has run on macOS or Windows (carried over from F01).** All 35 `platforms` are "expected". L300 adds more unrun paths: Qiskit/Aer (11 quantum skips), mitiq, PennyLane, the OpenBao transit API, minisign/cosign, pact-python, the OTel SDK, promptfoo, Mosquitto/paho, SALib, FMPy, the Rust/Embassy build and Renode. That is 24 skipped tests plus the manual-only tools. The root `.github/workflows/*.yml` files now exist and include L300, which is progress, but no run has been recorded. | schema300.txt; test_results300_run2.json (24 skipped); root workflows | Run the root matrix (macos-latest, windows-latest, ubuntu) once. Then flip `platforms` to `tested-ci`, empty the `pendingCi` lists that turn green, and paste the SDK output into the READMEs. |
| R3-02 | ai-agents | #13 | Med | **The buildTask check depends on wall-clock time and is flaky.** `test_build_task` requires exactly one budget violation (chat ≤ 500 ms, tool ≤ 200 ms, measured with real time against the fake server). The tool violation must also print as `execute_tool search_docs: 6…`. Results: it failed in **both** full-suite runs (`AssertionError: 2 != 1`) and passed in all 11 solo runs. Hosted Windows and macOS runners are slower and more variable. | test_results300_run2.json; run1.log | Give the fake server and the tool fixed simulated latencies (or a fake clock), and assert on the tool span only. Alternatively, give chat a generous budget and check `startswith("execute_tool search_docs")` without the "6". |
| R3-03 | cryptography | #15 | Med | **Wycheproof vectors were vendored from mirrors and search snippets, not from upstream.** AES-GCM tests come from the **pycryptodome 3.7.2** copy (Wycheproof 0.4 format, 2018), reached through `gemfury.com/aroundthecode/...`, which is an unofficial package mirror. The Ed25519 tests were "copied from search-result text of boringssl.googlesource.com". The licence is handled correctly (Apache-2.0 text plus NOTICE, derived vectors clearly separated). But the provenance cannot be checked, and "verified with cryptography" proves nothing for *invalid* vectors. This is honestly recorded in KNOWN-GAPS #47. | `vectors/*.json` "vendored" field; NOTICE.md; VERIFIED-RESOURCES rows 121–125 | Re-vendor from `C2SP/wycheproof/testvectors_v1/` at a pinned commit (VR already names d17cc89). Record the file SHA-256 and keep the current schema. Remove the gemfury and search-snippet sources. Have CI diff the subset against upstream. |
| R3-04 | cross-topic (simulation, microbit worst) | see fix | Med | **Required `seeAlso` links are missing, including all 5 pairs you asked about.** The field itself is absent in simulation #12–16 and microbit #13 and #16. Missing pairs: distributed-systems #15 ↔ ai-agents #13 (ai-agents #13 links to distributed-systems L100 #4 "for its Jaeger exercise", but the Jaeger lesson is distributed-systems #15); application-architecture #13 ↔ distributed-systems #16; application-architecture #15 ↔ distributed-systems #16; cryptography #16 ↔ ai-agents #16. Present: ai-agents #14 → distributed-systems L100 #4 (no back-link). Other real overlaps with no link: ai-agents #14's buildTask is a **circuit breaker**, the same pattern as application-architecture #13, under a different name; distributed-systems #13 ↔ application-architecture #13 (both use Toxiproxy); distributed-systems #14 sagas ↔ ai-agents #15 (idempotent refunds and compensation); simulation #12 ↔ quantum #15 (standard error and shot noise); simulation #13 ↔ quantum #13 (calibrating a model); simulation #16 ↔ distributed-systems #16 (throughput and queues). All 59 existing `seeAlso` titles match their targets exactly. | schema300.txt; seeAlso dump | Add both directions for each pair, using real titles. Use one term for the breaker ("circuit breaker"), and link distributed-systems L100 #4 → ai-agents #14. Give every simulation L300 lesson 1–2 links. |
| R3-05 | quantum, cryptography, ai-agents, distributed-systems, application-architecture, simulation | L200 #7–10 | Med | **L200 `next` pointers are stale now that L300 exists (same class as F03).** 22 lessons still say "L300 (planned): …". Several promise lessons that were not built: quantum #7–9 (Simon, phase estimation, amplitude estimation); ai-agents #7–10 (hybrid search, tool routing, durable runs, remote MCP); distributed-systems #8–10 (total-order broadcast, quorums, replicated caches); application-architecture #7–10. Others were built but are not referenced by number: simulation #7 → #13 and #12, #9 → #15, #10 → #12; cryptography #9 → #13. The spec only asked for #11 to be updated. | next-pointer scan | Point each pointer at a real L300 lesson ("L300 #NN title"), or say "L400 (planned)". Move the unbuilt topics to the KNOWN-GAPS "L400 candidates" list. |
| R3-06 | ai-agents, simulation | 12–16 | Med | **The failure lab is fixed for the learner, and the buildTask cannot be checked against the learner's own file.** In these 2 topics the hardened version is already shipped (`resilient_agent.py`, `antithetic_fixed`, `select(…, 'holdout')`, …), and the buildTask is a further feature (category gate, latency budget, circuit breaker, `pick_estimator`, `run_guarded` …). Its test imports only `solution/` and has no `CHECK_MINE`/`BUILD_TARGET` switch. Simulation's test says "point the import at your own file", meaning edit the test. So there is no fail-before for the learner's change. The other 5 topics do it as the spec says (buildTask = the hardening change, plus a switch). | test_build_task.py headers; `failureLab.fix` and `buildTask.task` texts | Add a `BUILD_TARGET=mine` switch whose starter stub fails, or make the failure-lab fix the learner's buildTask. Keep the extra features as stretch tasks. |
| R3-07 | ai-agents | #16 (and #12) | Med | **The promptfoo red-team exercise is not local-first.** `promptfoo redteam init/run` uses Promptfoo-hosted inference **by default**: it sends the purpose text, plugin config and your email to api.promptfoo.app, is usage-limited, and has telemetry on. The exercise says "local Ollama model as target", which gives a false impression that everything stays on the machine. The lesson never mentions this. | promptfoo.dev red-team "Configuring inference" and data-handling docs; L300.json learningTools | Add `PROMPTFOO_DISABLE_REMOTE_GENERATION=true` and `PROMPTFOO_DISABLE_TELEMETRY=1`, plus a local provider for generation and grading, with commands for zsh and PowerShell. Alternatively, mark the exercise "uses Promptfoo's hosted service" and make it optional. In #12, add the telemetry variable. |
| R3-08 | simulation, application-architecture | sim 12–16; application-architecture #15 | Low | 7 `learningTools.name` values do not exactly match the catalog: "marimo 0.25.2", "JupyterLab 4.6.4", "OpenModelica 1.27.1 (OMEdit)", "Scilab 2027.0.0 + Xcos", and "JupyterLab". The tools are in the catalog, but anything that matches by name breaks. | schema300.txt | Use the catalog name exactly and put the version in `expected` or `mac`/`windows`. |
| R3-09 | microbit | #16 | Low | `buildTask.solution` is the string "labs/…/fixed.rs (Python mirror: labs/…/solution_model.py)", which is not a path, so the schema tooling reports the file as missing. | schema300.txt | Make it a list of 2 paths. |
| R3-10 | distributed-systems, cryptography, microbit | distributed-systems #12; cryptography #12; microbit #13 | Low | Main lab file sizes fall outside the "~60–120 lines" guide: `raft.py` 137, `envelope.py` 127, microbit `main.py` 54. | schema300.txt | Move plumbing into `helpers.py` (Raft already has one), or accept and note it. |
| R3-11 | quantum | #14 | Low | The prerequisites list includes "Lesson 15 is the general version of this loop", which is a forward reference. It also omits #13, which `next` relies on, and L200 #10's sweep. | L300.json prerequisites | Replace it with "Lesson 10 (parameterized circuits)" and "Lesson 12 (noise)", and move the forward note into `next` or a caution. |
| R3-12 | distributed-systems | #15 | Low | `traced_call` always sends trace-flags `01`, ignoring the incoming sampled flag (W3C says a component SHOULD respect it and propagate it unchanged if it deferred the decision). The parser rejects higher versions instead of parsing the first 4 fields as §3.2.4 asks. The version limit is commented "simplified"; the flags issue is not mentioned. | `tracing.py` lines 10 and 33; W3C §3.2.2.5.1, §3.2.4 | Carry the received flags into the outgoing header, and add one checkYourself or troubleshooting line about sampling. |
| R3-13 | cryptography, application-architecture, microbit, simulation, ai-agents | cryptography #12, #16; application-architecture #12; microbit #14; simulation #14 | Low | New vendor or secondary sources (same issue as F15): Google Cloud KMS (×2), AWS KMS, Azure Architecture Center (×2), docs.kurrent.io, Docker Swarm secrets, a farnell.com distributor copy of the Energizer E92 datasheet, Wikipedia (Sobol indices), and Hugging Face blog posts. | urls300.json | Use NIST SP 800-57 and the OpenBao docs (envelope encryption and rotation), Fowler/Young (CQRS), the Energizer datasheet from Energizer's own site, and Saltelli et al. 2010 (Sobol). Keep vendor pages only as one-line equivalents. |
| R3-14 | all | — | Low | Concept share is 17.3–21.6 % (quantum 19.9, cryptography 18.6, ai-agents 17.6, distributed-systems 17.3, application-architecture 21.6, microbit 20.1, simulation 20.3), against your 30–35 % target. The notes are already at full length, so this is the "report, don't pad" case. Only cryptography's README reports it. | schema300.py | Report the share in every topic README. The main lever is trimming step and troubleshooting text, not growing the notes. |
| R3-15 | quantum | #15 | Low | `test_vqe` writes to a fixed path in the lab folder (`logs/test_gd.jsonl`). Two runs at the same time (parallel CI on one checkout, or a learner and an IDE test runner) corrupt the file; I saw `JSONDecodeError` in the overlapping run. | run1 results | Use `tempfile.TemporaryDirectory()`, as ai-agents does. |
| R3-16 | application-architecture | documentation | Low | LEARNING-TOOLS.md is 654 words (spec: 250–500). | `wc -w` | Trim it. Move the per-lesson exercises to the lessons, where they already are. |
| R3-17 | simulation | 12–15 | Low | `next` uses "Lesson 13: …"; every other topic uses "L300 #13 …". Machine parsing and the lesson map are inconsistent. | next scan | Use "L300 #NN title: why". |
| R3-18 | ai-agents | #16 agent assist | Low | `validate()` calls `json.loads` on a regex-captured `{…}` without try/except. One malformed model proposal crashes the run instead of being rejected. Decisions still stay in code, so this is a robustness issue, not a safety one. | `agent_assist.py` lines 33–42 | Wrap each variant in try/except and count rejects. |
| R3-19 | microbit | #14 | Low | The 15,275 h battery-life headline uses the chip-only System ON floor (1.5 µA). Board-level sleep current (the interface MCU, the regulator) is not modelled. The note mentions self-discharge but not the board floor. | concept note line 26–30; `budget.py` | Add a "board sleep floor (unknown, pending measurement)" row, or show the life at e.g. 50 µA too, so the headline is not read as a board figure. |
| R3-20 | distributed-systems (+ shared catalog) | #12, #13 | Low | The Maelstrom `windows` field reads "partial — No official statement; WSL2 likely (unverified)", which is not an install command. The catalog's Toxiproxy Mac line adds `brew tap shopify/shopify`, but toxiproxy is in homebrew-core (2.12.0). | L300.json learningTools; formulae.brew.sh | Give a WSL2 recipe or "not supported on Windows; use WSL2". Drop the tap in the catalog when shared/ is next edited. |

## Pedagogy notes (no finding unless listed above)

- **The step up from L200 is real.** L200 builds a feature; L300 breaks it on purpose, observes the failure and hardens it. Examples:
  - Raft's election restriction with a safety checker;
  - partitions with a linearizability check;
  - burn-rate alerts that a mean hides;
  - antithetic pairs that are not really antithetic;
  - an ISR lost-update race that every interleaving exposes.
- **Quantum L300** introduces new algorithms (QAOA, VQE, classifier) rather than hardening the L200 ones. Each still carries a genuine robustness lesson (restarts, SPSA under shot noise, barren-plateau initialisation, a classical baseline).
- **Failure-mode sections** name how you would *notice* each failure (a metric, a log field or a test), not just what goes wrong.
- **Trade-off tables** are useful decision aids with a "chooseWhen" column. For example: exact versus statistical assertions; stop-and-wait versus FEC; deterministic versus timing gates.
- **Observability:** every topic has at least 3 lessons that emit JSON lines the learner reads.
- **Agent assists** (one per topic, 7 in total): the model proposes paraphrases, hypotheses or explanations, and code decides by range checks, scanner truth, the suite result or a recomputed value.

## Per-topic verdicts

| Topic | Verdict |
|---|---|
| **quantum-computing** | Good. Clear failure labs (a model-based tolerance instead of exact equality, constrained mitigation, restarts, SPSA, near-identity init); all 5 proven. Versions and APIs are correct (mitiq 1.1.0's Python < 3.13 limit is handled with a separate venv). Still the least proven: 11 SDK tests skipped (R3-01). Fix the prerequisites in #14 (R3-11) and the shared-path test (R3-15). **Ready after CI.** |
| **cryptography** | Excellent hardening topic (rotation with retire guards, renewal with jitter, a strict release verifier, Wycheproof-driven wrappers, log redaction plus an agent with a secret gate). All proofs exact. The main problem is the provenance of the Wycheproof vectors (R3-03); vendor KMS sources (R3-13). **Ready after re-vendoring the vectors.** |
| **ai-agents** | Strong content (golden-set gate, GenAI-convention spans, budgets and fallback, an idempotent approval queue, a policy layer against injection with safe payloads). Weakest test hygiene: a flaky timing test (R3-02), and a buildTask that cannot be checked against the learner's file (R3-06). promptfoo red-team privacy (R3-07). Missing link to distributed-systems #15 (R3-04). **Fix R3-02 and R3-07 first.** |
| **distributed-systems** | Excellent. Deterministic simulations, the Raft rule from §5.4.1, linearizability checking, sagas with an idempotent log, traceparent propagation and a critical path, open-model backpressure with Little's law. All proofs exact; no timing flakes. Minor: trace-flags (R3-12), `raft.py` length, Maelstrom on Windows. **Ready.** |
| **application-architecture** | Strong and practical (projections that rebuild, breaker plus bulkhead, Pact-shaped contracts, SRE burn rates matching Table 5-8, deterministic query-count fitness gates). All proofs exact. Needs cross-links to distributed-systems #16 (R3-04) and a trimmed LEARNING-TOOLS (R3-16). **Ready.** |
| **microbit** | Good, and honest (`validated-stub`; Renode runs the nRF52840 model as a "close sibling", marked pending-ci). Correct CRC-16, ARQ with backoff, a scheduler, an adaptive-sampling power model, a robust serial parser, an IRQ race. Fix the #16 schema path (R3-09), the missing `seeAlso` (R3-04) and the power-floor caveat (R3-19). **Needs the simulator/CI run (R3-01).** |
| **simulation** | Rigorous (CRN-correct antithetic pairs, holdout calibration, Sobol ST against OAT, a stability bound for the FMI communication step, SeedSequence spawning; current SALib API; FMI 2.0 export chosen for the right reason). There are no L300 cross-links at all, and the failure-lab fixes are pre-built (R3-04, R3-06). Tool names (R3-08). **Ready after the links.** |

## Regressions vs the L100–L200 review

| Earlier fix | Status after L300 | Evidence |
|---|---|---|
| F03 / L200 #11 `next` → real L300 #12 title | **OK**: all 7 match the real titles. L300 #16 → "L400 (planned): …" in all 7. | next scan |
| F03 L100 `next` → existing L200 lessons | **OK**: no stale L100 pointers. **New, same class:** 22 L200 #7–10 pointers still say "L300 (planned)" (R3-05). | next scan |
| F08 `seeAlso` titles exact | **OK**: 59/59 entries in L100–L300 match the target titles exactly. Coverage gaps at L300 (R3-04). | seeAlso validator |
| F05 shared setup commands | **OK**: L300 installs (k6, Grafana, Bruno, step, KeyStore Explorer, minisign, Orange, JupyterLab, Mosquitto, rustup) match the catalog / WORKSTATION-SETUP; Ollama and Python are not re-specified. | install-command grep |
| F19 `LOCAL_MODEL_URL` / `LOCAL_MODEL` | **OK**: all 7 L300 agent assists use them; ai-agents keeps the `BASE_URL`/`MODEL` fallback. The default model is `qwen2.5:1.5b`; the `qwen2.5:0.5b` in ai-agents 14 is the documented fallback. | grep |
| F02 / F07 honest validation | **OK**: `pendingCi` is present on 35/35 lessons; microbit stays `validated-stub`; SDK files are listed as pending. | schema300 |
| F06 no unofficial mirrors | **Regressed in cryptography #15**: a gemfury.com package mirror and BoringSSL mirrors read from search snippets are used as vector sources (R3-03). No winget.tech / winstall.app links. | urls300.json |
| F14 no localhost "resources" | **OK** (the only hits are prose inside an Ollama row and the F06/F14 change notes). | grep |
| F15 vendor pages | **Partly regressed**: new KMS, Azure, Kurrent and Docker pages (R3-13). | urls300.json |
| F18 subprocess text without encoding | **OK**: none in L300. | xplat300 |
| F24 secret regex coverage | **OK**: the cryptography #16 gate reuses the broadened L200 #9 `SECRET` (base64/base64url keys, JWK private members) plus the lesson's scanner. | agent_assist.py |
| F27 housekeeping | Unchanged: running the tests creates `__pycache__`; only 3 topics have a `.gitignore`, and there is none at the root. | `ls -a` |
| F01 CI | **Improved**: root workflows now exist and include L300. Still no recorded run (R3-01). | `.github/workflows/` |
