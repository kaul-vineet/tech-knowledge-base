# Review: L100 + L200 knowledge base (7 topics)

Reviewed 2026-10-28. This was a read-only review; the only file written is this report. Running the tests created some `__pycache__` folders.
Checked against SPEC.md, CONCEPTS-SPEC.md, REBALANCE-SPEC.md, PLATFORM-AGENT-SPEC.md and L200-SPEC.md.

## Executive summary

**Overall: good. The content is applied, example-heavy, open-source-first and honest about its limits. The weakest part is evidence: nothing has run on a Mac or Windows PC yet.**

- **Tests:** I ran all 180 `test_*.py` files with `python3 -m unittest <module>` from each test's folder (240 s timeout).
  - 715 tests ran: **0 failures, 0 errors, 0 timeouts**, 78 skipped. The slowest file took 11.8 s.
  - 58 of the 78 skips are in quantum-computing, because Qiskit, Aer and Cirq are not installed here.
- **Schema (checked by script, not taken from status files):**
  - All 77 lessons have every required field.
  - The `code` field matches the lab file byte-for-byte in all 77 lessons.
  - Lessons are numbered 1–11 with no gaps in every topic.
  - Every L200 lesson has `buildTask` (solution file exists), 3–4 `codeWalkthrough` items and exactly 2 `tryIt` items.
  - Every lesson has a `platforms` field.
  - Concept notes have the right headings, and every "→ see lab step N" points to a step that exists.
  - Word counts with `wc -w`: L100 notes 242–249, L200 notes 377–399, so all are within the spec.
- **Accuracy:** about 25 version, API and formula claims checked against official sources were all correct. That includes the MCP 2026-07-28 claim, AsyncAPI 3.1.0, Qiskit 2.6.1 / Aer 0.18.2, cryptography 50.0.2 Argon2id, and the winget lag for Ollama. See the "Verified correct" list below.
  - Weak spots: the Node 24 / 26 LTS handover on Windows (F04), OpenAPI 3.1.2 chosen without saying why (F11), and two small MCP and llama.cpp details (F12, F13).
- **Biggest risks:**
  1. **No code has run on macOS or Windows.** Every `platforms` value is "expected". All Qiskit/Cirq code in all 11 quantum lessons has never run. The CI workflows sit inside each topic folder, in a folder that is not a git repository, so GitHub will never run them as placed (F01).
  2. **micro:bit is labelled `validated-local`, but it only ran against a home-made CPython stub.** It never ran on MicroPython or in the micro:bit simulator (F02).
  3. **L100 `next` pointers often promise L200 lessons that were never built.** This affects 19 of 42 L100 lessons (F03).
- **Cross-platform code is clean.** I scanned 772 files with AST and regex checks:
  - no POSIX-only calls, no hard-coded `/tmp`, no `shell=True`, no `0.0.0.0` binds;
  - every text-mode `open()` sets `encoding="utf-8"`;
  - every shell step that differs by OS has both `mac` and `windows` versions.
- **Safety and ethics are good.**
  - All 14 agent-assist scripts keep decisions in code; the model only proposes or explains.
  - The cryptography assists refuse to send key material.
  - The simulation assist checks value ranges and caps the size of a sweep.
  - No military or weapons content appears in simulation, quantum or micro:bit.

**Findings by severity: High 2 · Medium 6 · Low 19 (27 in total).**

## Method (reproducible)

The scripts and raw outputs are in the session folder `files/review/`:
- `schema_check.py`: fields, code against file, numbering, buildTask, word counts, concept share;
- `xplat.py`: AST and regex cross-platform scan;
- `run_tests.py`: runs every test file, writes `test_results.json`.

Extra checks:
- URLs: extracted 427 unique URLs from lesson `sources` and VERIFIED-RESOURCES and grouped them by domain.
- Official sources fetched for the version checks: PyPI (qiskit, qiskit-aer, cirq, qiskit-qasm3-import, mcp, simpy, scipy, Mesa), cryptography.io changelog, modelcontextprotocol.io (basic, versioning, latest), asyncapi/spec releases, spec.openapis.org, nodejs.org releases page + schedule.json, winget-pkgs folders (OpenJS.NodeJS.LTS, Ollama.Ollama), ollama/ollama releases, etcd releases, keycloak.org downloads, micro:bit MicroPython radio docs.
- Formulas recomputed by hand or code: Grover P(k), Erlang B and C, t-quantiles, heavy-hex qubit count.

## Verified correct (sample)

| Claim in KB | Official evidence |
|---|---|
| MCP spec 2026-07-28 is current. It has no `initialize`; each request carries `io.modelcontextprotocol/protocolVersion` and `clientCapabilities` in `_meta`. `server/discover` exists. Error -32022 = UnsupportedProtocolVersion; missing fields → -32602. | modelcontextprotocol.io versioning + basic pages; `/specification/latest` resolves to 2026-07-28 |
| Python SDK `mcp` 2.3.0 | PyPI, released 2026-10-02 |
| AsyncAPI 3.1.0 is the latest | asyncapi/spec releases (v3.1.0, 2026-01-31) |
| Qiskit 2.6.1 / qiskit-aer 0.18.2; Aer is in "reduced maintenance mode" | PyPI (2026-10-22 / 2026-10-26). The Aer note is already in quantum KNOWN-GAPS. |
| cirq 1.7.0, qiskit-qasm3-import 0.6.0 | PyPI |
| cryptography 50.0.2 wheels use OpenSSL 4.0.3. Argon2id was added in 44.0.0 (needs OpenSSL ≥ 3.2); the PHC helpers in 45.0.0. | cryptography.io changelog |
| Ollama 0.40.12 is the latest; the winget `Ollama.Ollama` manifest lags at 0.34.2 | GitHub releases; winget-pkgs folder |
| `OpenJS.NodeJS.LTS` 24.19.0 exists (the pin in application-architecture) | winget-pkgs folder |
| SimPy 4.1.2, SciPy 1.18.1, Mesa 3.5.1 (needs Python ≥ 3.12) | PyPI |
| etcd v3.7.3, Keycloak 26.8.1 | etcd releases; keycloak.org downloads |
| micro:bit radio defaults: length 32, channel 0–83, group 0–255, `send()` adds a 3-byte header | microbit-micropython v2 docs |
| Grover N=8, M=1: k=2 → P=0.9453, k=3 → 0.3301. Erlang C (λ=2.4, μ=1, c=3): Wq=1.079. Erlang B: 0.268. t(0.975) for df 9/19/39/79 = 2.262/2.093/2.023/1.990. Heavy-hex d=3 has 19 qubits. TLS verify codes 62 and 20. TMP102 pointer 0x03 = T_HIGH. | Recomputed independently |

## Findings

Severity: **High** = the user's stated goal or a hard spec rule is not met · **Med** = misleading or inconsistent; fix before publishing · **Low** = polish.

| ID | Topic | Lesson | Sev | Finding | Evidence | Recommended fix |
|---|---|---|---|---|---|---|
| F01 | all (quantum worst) | all | **High** | **No lab has run on macOS or Windows.** Every `platforms` value is `{"mac":"expected","windows":"expected"}`. In quantum, every Qiskit/Cirq/Aer code path in lessons 1–11 has never run; only numpy cross-checks ran (58 of 130 quantum tests skipped). The 7 `labs.yml` files are in `<topic>/.github/workflows/`, inside a folder that is not a git repository. GitHub only runs workflows from the repository root, as several of the workflow headers themselves say. So the "pending-ci" path will never happen as things stand. | schema_check output; test_results.json (quantum 130 tests / 58 skipped); `ls */.github/workflows`; header comments in the quantum, microbit and application-architecture workflows | Create the repository, then either put one root workflow that calls each topic with `working-directory`, or move the files there. Run the macos-latest / windows-latest / ubuntu-latest matrix once. Then change `platforms` to `tested-ci`, change quantum `validation.status`, and paste the real SDK output into the READMEs. Until then, add one line to each topic README: "not yet run on Mac/Windows". |
| F02 | microbit | 1–11 | **High** | **`validation.status` is `validated-local` for all 11 lessons, but the code only ran on `labs/sim_stub`.** That is a CPython imitation of the `microbit` API written for this KB. MicroPython and the micro:bit Python Editor simulator were never run: the Playwright harness `harness/simulator*.spec.js` is CI-only and the L200 simulator runs are pending-ci. Your rule is "pending-ci where SDK/simulator not run". Some tryIt `expected` values come from stub-only behaviour (for example, radio truncation is modelled from the **V1** `modradio.cpp`; KNOWN-GAPS #41). | `validation.how` in microbit L100/L200 ("validates the lab logic only", "pending-ci: no internet") | Set status to `pending-ci`, or add a separate value such as `validated-stub`. Run the Playwright harness in CI and copy the simulator output into tryIt/README. Mark tryIt values that came only from the stub with "(stub)". This is already done in L200 but not consistently in L100. |
| F03 | quantum, cryptography, ai-agents, distributed-systems, simulation | L100 1–6 | Med | **L100 `next` names L200 lessons that do not exist (19 of 42 L100 lessons).** Quantum 3, 4, 5 ("Estimator primitive", "teleportation", "OpenQASM 3 classical control"). Cryptography 1, 3, 4, 5 and partly 6 ("hash-pinned deps", "nonce strategies", "envelope encryption", "peppers"). ai-agents 1, 2, 3, 4, 6 ("streaming", "prompt evaluation sets", "workflow patterns"). Distributed-systems 1, 2, 3, 4, 6 ("health checks", "RPC/IDLs", "deadline propagation", "circuit breakers", "vector clocks"). Simulation 5 ("Mesa data collection"; there is no agent-based L200 lesson). Application-architecture and microbit use real lesson numbers and are correct. | `next` field compared with L200 titles (printed by script) | Point each `next` to an actual L200 lesson number, as application-architecture and microbit do. Move topics that were not built to an "L300 candidates" list in KNOWN-GAPS. |
| F04 | microbit (also application-architecture docs) | microbit L100 #1; HARDWARE | Med | **Node on Windows is about to drift away from the spec's "Node 24".** microbit installs `winget install -e --id OpenJS.NodeJS.LTS # Node 24 LTS` without a version, while CI uses Node 24. application-architecture's own KNOWN-GAPS says Node 26 is scheduled to become LTS today (2026-10-28), after which `OpenJS.NodeJS.LTS` moves to 26.x. schedule.json shows Node 24 entered **Maintenance** LTS on 2026-10-20. Note: today nodejs.org still lists v26 as "Current" and winget LTS is 24.19.0, so the claim is plausible but was not yet visible. | microbit/content/L100.json line ~104; application-architecture KNOWN-GAPS lines 99–101; nodejs.org releases page; schedule.json; winget-pkgs folder | Pin `--version 24.19.0`, as application-architecture L200 #9 already does, or use `OpenJS.NodeJS.24` if that id exists (check winget-pkgs first). Change the HARDWARE text to "Node 24 (Maintenance LTS)". Check again after the Node 26 LTS promotion. |
| F05 | all | Setup lessons + HARDWARE | Med | **Install recipes contradict each other across topics, on the same two machines.** Ollama on Mac: `brew install ollama` + `brew services start ollama` (quantum, application-architecture, microbit) versus `brew install --cask ollama-app` followed directly by `ollama pull` (cryptography, simulation, ai-agents). The cask does not start the server until the app is opened, so that `pull` can fail. Python on Windows: winget `Python.Python.3.12` (4 topics, id checked in winget-pkgs) versus the python.org installer in ai-agents, whose KNOWN-GAPS says the winget id "could not be fetched". | Grep of `mac`/`windows` step fields; ai-agents KNOWN-GAPS line 45; simulation KNOWN-GAPS (id confirmed) | Write one shared "workstation setup" page (Mac mini + Windows 11) and link it from each topic's lesson 1. Pick one Ollama path; if it is the cask, add "open Ollama.app once". Pick one Python path. |
| F06 | cryptography, distributed-systems | cryptography #1 (source); VERIFIED-RESOURCES | Med | **Unofficial winget mirrors are cited as evidence** (`winget.tech/app/ollama`, `winstall.app/apps/ShiningLight.OpenSSL.Light`, `winstall.app/apps/Python.Python.3.12`). The spec says to check winget ids in official sources. Cryptography's KNOWN-GAPS also lists "ragerworks, vmheaven" for the OpenSSL package. | urls.json; cryptography KNOWN-GAPS | Replace them with `github.com/microsoft/winget-pkgs/tree/master/manifests/...` links, as the other topics do. If a package id cannot be found in winget-pkgs, drop it. |
| F07 | ai-agents, application-architecture, cryptography, distributed-systems, simulation | ai-agents 7, 8, 10 · application-architecture 6, 9, 10, 11 · cryptography 8, 10 · distributed-systems 1, 7, 10 · simulation 3, 4, 5, 7–11 | Med | **Mixed status hidden behind one value.** These lessons are `validated-local`, but some files they present have never run: the official MCP SDK interop, sqlite-vec/pgvector, jsonschema, the AsyncAPI CLI, Keycloak, Testcontainers, the age/openssl CLIs, etcd, Valkey, SimPy, SciPy and Mesa. The `how` text says so honestly, but a reader or dashboard only sees "validated". | `validation.how` strings; skipped tests (ai-agents 5, application-architecture 3, cryptography 2, simulation 10) | Add `validation.pendingCi: [files]` or use the value `validated-local+pending-ci`. Show a small "partly unverified" badge in the lesson. |
| F08 | cross-topic | application-architecture 9/10, distributed-systems 5/8/11, cryptography 11, ai-agents 11 | Med | **Overlapping content in different topics is never linked.** Idempotency keys, outbox and idempotent consumer appear in distributed-systems L100 #5 and L200 #8 and in application-architecture #9. JWT / ID-token checks (alg allow-list, aud, exp) appear in cryptography #11 and application-architecture #10. Rate limiting appears in distributed-systems #11 and the ai-agents #11 buildTask. Each has different code and different names for the same idea, and none mentions the others. | No cross-topic references found in any L200.json | Add one `seeAlso` line per lesson pointing to the other topic's lesson. Use the same term for the same concept, for example "idempotent consumer" everywhere. |
| F09 | all except simulation L100 | — | Low | **Concept share is below the REBALANCE target.** L100: quantum 18%, cryptography 18%, ai-agents 19%, distributed-systems **14%**, application-architecture 17%, microbit 18%, simulation 20% (target 20–25%). L200: ai-agents 19%, distributed-systems 19%, simulation 22% (target 25–30%). The specs allow reporting this instead of padding. | REBALANCE measurement script (schema_check.py) | Report it in each README. The reason is the extra hands-on material, mainly Mac/Windows steps and agent assist. Optionally trim the longest step text instead of growing the notes. |
| F10 | simulation | #8 (source); VERIFIED-RESOURCES | Low | An odd domain is used for a validation cross-check: `kcl.digimat.in/nptel/.../lec15.pdf`, an NPTEL lecture mirror that backs the Erlang C value 0.702. | urls.json | Cite the official nptel.ac.in course page, or a textbook or university page. The formula itself is correct (Wq recomputed: 1.079). |
| F11 | application-architecture | #4 | Low | The lesson teaches OpenAPI 3.1.2, but spec.openapis.org lists 3.2.1 and 3.2.0. The evidence file knows this, yet the lesson does not say why 3.1 was chosen. | spec.openapis.org/oas; application-architecture research/L100-evidence.md line 96 | Add one line: "3.2 exists; we use 3.1.x because validators and generators support it widely". Also add a 3.2 line to `equivalents`. |
| F12 | ai-agents | #10 | Low | The MCP lab server answers -32022 with `supported: ["2026-07-28","2025-11-25"]`, but it rejects a modern-style request that uses 2025-11-25. That version is only reachable through `initialize`. A client that trusts the error data would retry with an unusable version. | labs/L200/10-mcp-server-client/mcp_server.py lines 47–53 | List only the versions accepted in `_meta`, and document that 2025-11-25 is reached only through the legacy handshake. Alternatively, return a separate hint. |
| F13 | ai-agents | #10 README | Low | `llama-server --mcp-servers-config` is presented as a normal feature. Current llama.cpp documentation and guides mark it **experimental**, and much of the MCP host role sits in the bundled web UI. | web search (llama.cpp MCP articles, 2026) | Add "(experimental)" and a link to the llama.cpp server README. |
| F14 | quantum, cryptography, application-architecture, simulation | VERIFIED-RESOURCES | Low | `http://localhost:11434/v1` appears as a "verified resource". | urls.json | Remove it from the resource tables; it is configuration, not a source. |
| F15 | application-architecture, distributed-systems, ai-agents | application-architecture #3, #7; distributed-systems VR; ai-agents #6 | Low | Vendor or vendor-adjacent pages are used as sources: AWS Prescriptive Guidance (hexagonal), Confluent docs (delivery semantics), Thoughtworks Radar, LangChain docs, `mermaid.ai` (commercial domain). They are not main examples, but open-source or original sources exist. | urls.json | Use Cockburn's original hexagonal article, kafka.apache.org docs (already cited), the Ford/Parsons fitness-function material and mermaid.js.org. Keep LangChain only as an `equivalents` line. |
| F16 | several | VERIFIED-RESOURCES | Low | Duplicate or stale source entries: `pythonnumericalmethods.berkeley.edu` and `.studentorg.berkeley.edu`; `informs-sim.org` and `www.informs-sim.org`; Ollama docs cited three ways (docs.ollama.com, GitHub blob `.mdx`, raw); microbit cites the Ollama winget **0.20.0** manifest (current is 0.34.2); ai-agents cites the Ollama v0.13.5 README for a RAM rule that has since been removed (already in KNOWN-GAPS). | urls.json | Use one URL per document and point to the current manifest folder. Replace the RAM rule with numbers from docs.ollama.com/faq, or measure them. |
| F17 | quantum | VERIFIED-RESOURCES | Low | A personal blog (scottaaronson.blog) is kept as a resource. That is fine as background, but it is not implementation material. | urls.json | Mark it "background" or drop it. |
| F18 | cryptography, distributed-systems | cryptography #2 `hash_and_hmac.py:38`, `test_age_cli.py`; distributed-systems #1 `test_lab.py`, `try_it.py`; distributed-systems #7 `etcd_equivalent.py` | Low | `subprocess.run(..., text=True)` without `encoding=`. On Windows this decodes with the ANSI code page. `certutil` output is localised, so parsing may break on a non-English Windows. | xplat.py output | Add `encoding="utf-8", errors="replace"`, or parse bytes. For certutil, match the 64-hex-character line only. |
| F19 | ai-agents | all | Low | ai-agents does not vendor `labs/_shared/local_agent` and uses `BASE_URL`/`MODEL`. Every other topic uses `LOCAL_MODEL_URL`/`LOCAL_MODEL`. A learner has to set different variables per topic. | grep of `os.environ` | Accept both names in ai-agents, or document the mapping in the shared setup page (F05). |
| F20 | ai-agents | #7, #11 | Low | `projectFiles` contains glob paths (`labs/L200/07-rag-answers/docs/*.md`, `11-guardrails/docs/*.md`) that are not real files, so tools reading the schema break. | schema_check.py | List each file, or add `"glob": true`. |
| F21 | distributed-systems, simulation | distributed-systems #1; simulation #2 | Low | Lesson size is uneven. The distributed-systems setup lesson is the **largest lesson in the KB** (~1,960 hands-on words; median 1,206), which is heavy for an L100 "run it" setup. Simulation #2 is the thinnest (727). | schema_check.py lesson sizes | Move the optional Compose/Podman path in distributed-systems #1 to an appendix. Simulation #2 is acceptable but could use a third troubleshooting row. |
| F22 | application-architecture | L100 1–6 | Low | The L100 style rules are exceeded: 3–4 troubleshooting rows in lessons 1, 3, 5, 6 (spec: 1–2) and 2-sentence overviews everywhere (spec: 1–2, at the edge). | schema_check.py | Trim to 2 rows; move the extra rows to the lab README. |
| F23 | application-architecture | #10 | Low | The checkpoint "you can say which attack state, nonce, PKCE and aud each stop" cannot be tested by code. The other checkpoints can. | L200.json checkpoint | Make this one of the `checkYourself` items and keep the checkpoint to "all tests pass". |
| F24 | cryptography | #6, #9 agent assist | Low | The secret gates use regexes for PEM headers, long hex strings and AKIA keys. They would miss base64 keys, JWK `"d"` values and raw 32-byte keys encoded in base64url. The design is sound (deterministic gate before sending); only the coverage is narrow. | agent_assist.py lines 23–27 and 25 | Add patterns for base64 / base64url ≥ 43 characters and JWK private members. Better: send an allow-listed summary (certificate fields only) rather than filtering free text. |
| F25 | quantum | L100 1–6 | Low | L100 uses AerSimulator as the main simulator. The KB itself notes Aer is in reduced-maintenance mode, and L200 already moved to `StatevectorSampler` / `GenericBackendV2`. | PyPI qiskit-aer page; quantum KNOWN-GAPS | Make Qiskit's reference primitives the default in L100 and keep Aer as the "noise models / speed" equivalent. |
| F26 | microbit | #7 tryIt | Low | The radio truncation rule (`'A'*40` → 23 characters) comes from the V1 `modradio.cpp`; the V2 behaviour was not read (KNOWN-GAPS #41). The official v2 docs only say `length` is the maximum. | microbit radio docs; KNOWN-GAPS #41 | Check this in the simulator run from F01/F02 before presenting it as fact. |
| F27 | all | housekeeping | Low | Housekeeping: `__pycache__` folders throughout the labs and vendored helpers; `quantum-computing/run_labs.log` committed; `ResourceWarning: unclosed socket` in the shared fake-server test. | `ls`, run_labs.log | Add a `.gitignore` (pycache, logs, `*.db`). Close the socket in `test_shared.py`. |

## Checks with no findings

- **Schema:** every check listed in the executive summary passed. In addition, every `projectFiles` path exists except the globs in F20, and there are no duplicate lesson ids.
- **Tests:** 180 files, 715 tests, 0 failures, 0 errors, 0 timeouts.

  | Topic | Tests | Skipped |
  |---|---|---|
  | quantum-computing | 130 | 58 (SDK) |
  | cryptography | 73 | 2 |
  | ai-agents | 100 | 5 |
  | distributed-systems | 62 | 0 |
  | application-architecture | 147 | 3 |
  | microbit | 101 | 0 |
  | simulation | 101 | 10 |
  | shared helper | 1 | 0 |

- **Cross-platform:** pathlib is used throughout; subprocesses use `sys.executable`; servers bind 127.0.0.1; environment-variable syntax is given for both zsh and PowerShell where it differs.
- **Safety:** all 14 `agent_assist.py` scripts state and implement "model proposes, code decides".
  - Policy tables, linters, numpy recomputation, range checks and caps decide every outcome.
  - Tests use only the fake server.
  - Cautions say never send secrets to a model.
  - Simulation scope is civilian: queues, clinics, inventory, physics, Schelling.
- **No marketing:** commercial tools appear only as single `equivalents` lines.
- **Progression from L100 to L200:**
  - Each L200 lesson builds on named L100 prerequisites.
  - Notes grow from about 245 to about 395 words, and `codeWalkthrough` is new at L200.
  - Every buildTask is a real feature with a test that fails on the starter code and passes on the solution.
  - tryIt items are real experiments with observed numbers: no fencing, 3 vs 10 s visibility timeout, rtol sweeps, alg:none, and so on.

## Per-topic verdicts

| Topic | Verdict |
|---|---|
| **quantum-computing** | Strong teaching and correct versions and formulas: BV, Grover, QFT and transpiling build cleanly on L100. **It is the least proven topic:** all SDK code is unrun (F01). L100 `next` pointers are partly stale (F03), and L100 should prefer primitives over Aer (F25). Status `pending-ci` is honest. **Ready after one CI run.** |
| **cryptography** | Excellent and current. RFC test vectors match byte-for-byte, and it uses modern APIs (Argon2id, Ed25519, X25519+HKDF+AEAD, X.509 verification, mTLS). The agent assist has a secret gate. Fix: winget mirrors (F06), stale `next` (F03), and broaden the secret regex (F24). **Ready.** |
| **ai-agents** | Very good. It is vendor-neutral (Ollama, llama.cpp, vLLM), the MCP 2026-07-28 two-era client/server is accurate, and the guardrails lab shows the injection risk well. Fix: stale `next` (F03), the install path that differs from other topics (F05, F19), the MCP `supported` list detail (F12), and the experimental llama-server flag (F13). **Ready.** |
| **distributed-systems** | Excellent hands-on design: seeded, simulated clocks, so output repeats exactly. L200 picks the right patterns (leases + fencing, at-least-once delivery, consistent hashing, caching, rate limits). Lowest concept share (14% L100) and an oversized setup lesson (F09, F21). Five of six L100 `next` pointers are stale (F03). **Ready after the `next` fix.** |
| **application-architecture** | Strong. Hexagonal → aggregates → outbox + AsyncAPI 3.1.0 → OIDC+PKCE → measured pyramid is a coherent path, and Node is pinned correctly. Minor: vendor sources (F15), the OpenAPI 3.1 rationale (F11), L100 verbosity (F22). Link to cryptography #11 and distributed-systems #8 (F08). **Ready.** |
| **microbit** | Good lessons, and `next` pointers are correct. **The validation label overstates what ran** (stub only, F02), and Node is unpinned on Windows (F04). The simulator harness must run before the content can be called validated. **Needs a CI/simulator run.** |
| **simulation** | Excellent and rigorous: Erlang C/B, Welch warm-up, common random numbers, adaptive RK45 with SciPy's tableau. Agent assist has strong range checks. Civilian scope. Fix: the NPTEL mirror source (F10), the dangling Mesa `next` (F03), and mixed status labels (F07). **Ready.** |
