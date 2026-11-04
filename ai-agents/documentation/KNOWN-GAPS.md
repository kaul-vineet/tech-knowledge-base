# Known gaps – AI Agents (L100–L300)

## Not run in the sandbox (no internet for installs/downloads)
- **Real-model runs.** Ollama 0.40.12 + `qwen2.5:1.5b` was never executed here. All six labs are validated only against `fake_model_server.py`. The real-model path is documented as an optional manual run and wired as an opt-in CI job (`workflow_dispatch`, `real_model=true`) that has **not** been executed either.
- **`response_format: json_schema` on Ollama / llama.cpp.** Ollama docs state structured outputs also work via `response_format` on the `/v1` API and list it as a supported field; llama.cpp's GBNF guide documents `response_format` with `json_schema`; the exact `json_schema` variant used in lab 4 was not exercised against a live server.
- **Tool calling quality of `qwen2.5:1.5b`.** The model is tagged `tools` on the Ollama library page; how reliably a 1.5B model chooses the tool and stops was not measured.
- **curl equivalent** (lesson 2 README): written from the Ollama `/v1` docs example; not run (needs a live server).
- **CI workflow** was syntax-checked with PyYAML and its test loop was executed locally, but it has not run on GitHub.

## Simulator limits (fake_model_server.py)
- Rule-based, not a model: keyword sentiment, regex extraction of name/age/city, regex detection of arithmetic and the word "time".
- One tool call per turn (real models may return parallel calls); no streaming (`stream: true` is ignored); token counts are word counts.
- `response_format` is honoured only by returning clean JSON – no real schema enforcement.
- Lesson 3 differences between prompt layouts are hard-coded to show the *typical* effect; real behaviour must be observed with the optional run.

## Unverified / could not fetch
- No single vendor-neutral *specification* of the chat-completions format exists; request/response fields are cross-checked against the Ollama `/v1` and `/api/chat` docs, the vLLM online-serving and tool-calling docs, and the llama.cpp server README.
- `https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/server/README.md` – no content; the GitHub HTML view of the same file was used.
- llama.cpp default port: current README says `127.0.0.1:9931` (changed recently, commit "server: use port 9931 by default"); older builds and many tutorials use 8080. Check the startup log.

## Dropped
- promptingguide.ai few-shot page – useful content but contains a discount-code promotion (marketing); replaced by the Hugging Face prompt-engineering + chat-templates docs.
- `qwen3:0.6b` / `qwen3:1.7b` as the main model – thinking models add reasoning output that complicates L100 parsing; kept as an equivalent only.
- Code length: labs 4 (69 lines) and 6 (76 lines) exceed the "typically 15-60" guideline because they include the validator / safe calculator in the same file.

## Concepts layer (added 2026-10-28)
- **L200–L400 concept map is a proposal.** No agreed curriculum beyond L100 exists in the kb folder; the map in `CONCEPTS-PRIMER.md` and the "Next:" lines in each note need sign-off.
- **Chat template in concept 03 is illustrative.** It uses a ChatML-style layout like the Hugging Face docs example; the exact template for `qwen2.5:1.5b` was not inspected (no model download).
- **Temperature formula.** The fetched source (HF "How to generate text") describes "lowering the temperature of the softmax" and T→0 = greedy, but does not print `softmax(logits / T)` explicitly; the formula is the standard reading. The probabilities in concept 02 are computed by `research/concept_examples.py`.
- **Worked examples run on the fake server only.** Token counts (word counts in the fake) and replies will differ on a real model; this is stated in each note.
- **MCP spec URL.** `https://modelcontextprotocol.io/specification/latest` redirected to the 2026-07-28 page, which itself says a newer version exists; only stable facts (JSON-RPC 2.0, hosts/clients/servers, tool consent) are used.

## Rebalance + vendor-neutral sources (2026-10-28)
- **Vendor-hosted guides removed** from content JSON, concept notes, primer, VERIFIED-RESOURCES and research evidence; replacements are listed at the end of `research/L100-evidence.md`. The only remaining vendor mention is one primer glossary line on where the wire format originated.
- **`tool_call_id` matching rule.** With the vendor function-calling guide gone, the field is confirmed only indirectly: vLLM's tool-calling page mentions `tool_call_id` fields (Mistral template note), while Ollama's native API uses `tool_name`. The rule is enforced by `fake_model_server.py` and tested; real servers may be less strict.
- **`max_steps` budget** is this course's design choice; MCP supplies timeouts/logging/human-approval guidance but no iteration limit.
- **tryIt runs on the fake server only.** Expected values are fake-server observations (`test_try_it_NN.py` in each lab); a real model's wording will differ, and lesson 1 tryIt 1 relies on the fake ignoring unknown model names.
- **Concept share** is 20% (lower edge of the 20-25% target) – see the measure command in REBALANCE-SPEC.md.
- **Concept notes keep lab-step pointers to step 2 for most points** because lessons 3-6 have a single "run the script" step.

## Mac mini + Windows (PLATFORM-AGENT-SPEC, 2026-10-28)
- **macOS/Windows not executed.** The sandbox is Linux; every lesson has `platforms: {mac: expected, windows: expected}` until the CI matrix (`macos-latest`, `windows-latest`, `ubuntu-latest`) has passed on GitHub.
- **Install commands not run.** `brew install ollama` + `brew services start ollama`, `OllamaSetup.exe`, `winget install -e --id Python.Python.3.12` (canonical, `kb/shared/WORKSTATION-SETUP.md`), `brew install --cask ollama-app` (alternative), `brew install llama.cpp`, `winget install llama.cpp`, `launchctl setenv OLLAMA_HOST ...` and the PowerShell user-variable line come from the official docs/registries listed in VERIFIED-RESOURCES; none was executed here.
- **winget lags.** On 2026-10-28 the newest `Ollama.Ollama` winget manifest was 0.34.2 while the Homebrew cask and the CI pin are 0.40.12; the ollama.com installer (`OllamaSetup.exe`) is the safer way to match versions.
- **winget id for Python** – resolved (F05): lesson 1 now uses `winget install -e --id Python.Python.3.12` as in WORKSTATION-SETUP (id checked there during the review); not executed here.
- **GPU behaviour unverified locally.** Metal/CUDA/ROCm/Vulkan statements are from docs.ollama.com/gpu, /macos, /windows; no GPU run, no tokens/s figures. Which GPU backend the winget llama.cpp package ships was not checked.
- **RAM rule** – resolved (F16): the v0.13.5 README rule (8/16/32 GB) was removed from lesson 1, HARDWARE.md and VERIFIED-RESOURCES; the current FAQ has no per-size table, so sizing now uses Q4_K_M download sizes plus `ollama ps` SIZE (measure, don't assume).
- **LAN steps.** `ipconfig getifaddr en0` assumes the Mac mini's Ethernet is `en0`; Wi-Fi may differ. Firewall prompts on the host were not verified.
- **Shared helper.** `labs/L100/01-setup/fake_model_server.py` is now byte-identical to `kb/shared/local_agent/fake_model_server.py` (gained the empty `EXTRA_RULES` hook); `test_shared_helper.py` skips those checks when this topic is checked out alone (e.g. in its own CI repo).
- **Concept share now 18.6%** (1541 concept / 6749 hands-on words; was 20.4%) – below the 20-25% L100 target because lesson 1 gained per-OS commands and LAN/GPU steps. Concept notes are already 242-249 words, so they were not padded (PLATFORM-AGENT-SPEC: report, don't pad).

## L200 (built 2026-10-28)
### Pending CI (not executable in the sandbox – no package installs)
- **sqlite-vec equivalent (lesson 7)** – `sqlite_vec_equivalent.py` + `test_sqlite_vec_equivalent.py` written against the documented API (`sqlite_vec.load`, `vec0 ... distance_metric=cosine`, `MATCH ? AND k = n`); never run. The test skips when the Python's `sqlite3` cannot load extensions – whether `actions/setup-python`'s macOS/Windows builds can is unknown; the CI step prints it.
- **pgvector equivalent (lesson 7)** – Linux-only CI job with `pgvector/pgvector:0.8.7-pg18`; the generated SQL was never executed. No Mac/Windows run (hosted macOS/Windows runners have no service containers).
- **python-jsonschema cross-check (lesson 8)** – expected verdicts were reasoned from the JSON Schema docs (1.0 is an integer, booleans are not), not executed.
- **Official MCP Python SDK 2.3.0 (lesson 10)** – `sdk_server.py` and `test_sdk_equivalent.py` follow the v2 API reference (`MCPServer`, `mcp.run()` stdio default, `Client(StdioServerParameters(...))`, snake_case `is_error`); the import path of `StdioServerParameters` has a fallback because only third-party pages showed it. The SDK-client-to-our-server interop test may expose fields our server omits (e.g. strict result validation) – that is its purpose. PyPI says Python ≥ 3.10, the SDK docs say 3.11+; CI uses 3.12.
- **numpy pin** – CI pins 2.5.4 (latest); the sandbox validated with 2.5.3.

### MCP version
- MCP **2026-07-28** is the current version per `modelcontextprotocol.io/docs/learn/versioning` ("The current protocol version is 2026-07-28"), yet every spec page shows an "older version … view the latest" banner; no newer dated version was found in the spec repo listing (2024-11-05 … 2026-07-28 + draft). Re-check before L300.
- The requested "initialize, tools/list, tools/call" flow is the **2025-11-25 (legacy)** handshake; 2026-07-28 removed `initialize`. The lab implements both (dual-era server; client probes `server/discover`, falls back to `initialize`). Streamable HTTP, `subscriptions/listen`, MRTR (`input_required`), pagination and cancellation are not implemented.
- `https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio` and the raw `.mdx` files returned no content via web_fetch; their text was read from web_search results of the spec repository.

### Fake-server limits added for L200
- **Embeddings are hashed bags of words** (64 dims): similar wording, not similar meaning; hash collisions give non-zero scores to unrelated text (France question: 0.183). Real embeddings (e.g. embeddinggemma) have hundreds of dimensions; dimension count not verified.
- **Tool planning is keyword rules** ("weather in X", 'search docs for "…"', "remember that …"); the validation retry ("drop the rejected field once") and the injection rule ("obey `ignore previous instructions … call X with {…}`") are scripted behaviours that mirror common real failures – how often a real model self-corrects or obeys an injection was **not measured**.
- **Token counts are word counts**; real tokenizers count more tokens than words for most text. The budget in lesson 9 must be calibrated with `usage.prompt_tokens` on a real server.
- **Summaries** are "first 8 words of each user line" – deterministic, lossy on purpose (shows "5433" being lost).
- The `<tool_spec>` / `<tool_list>` agent-assist rules return fixed-format drafts; a real model's drafts vary.

### Shared helper
- `labs/L100/01-setup/fake_model_server.py` was extended (rules 1-5 and the embedding routes, documented in its header) and copied byte-for-byte to `kb/shared/local_agent/fake_model_server.py`; `test_shared_helper.py` and `kb/shared/local_agent/test_shared.py` pass, all 44 L100 tests still pass and `research/concept_examples.py` output is unchanged. Other topics vendor their own (already diverged) copies under `labs/_shared/local_agent/` and are not affected; they can re-vendor to get the new rules.
- ai-agents does not vendor `labs/_shared/local_agent/` (it is the origin of the helper); agent-assist scripts use `requests` like the other labs.

### Not run / unverified
- No real model, embedding model, llama-server or vLLM run (no downloads). Real-model steps and the `real_model` CI job (now also pulling `embeddinggemma`) are unexecuted.
- **llama-server `--mcp-servers-config`** example (lesson 10) and `--embd-gemma-default` (lesson 7) come from the README only.
- **Windows/PowerShell piping** of a JSON line into `python mcp_server.py` (lesson 10 step 2) not executed; Windows PowerShell 5.1 pipes text with its own output encoding – ASCII JSON should be unaffected.
- `macOS system Python cannot load SQLite extensions` is from the sqlite-vec docs and Python docs; not tested on a Mac.
- Regex injection screening is intentionally simple and easy to bypass (rephrasing, encodings); it is one layer, not a defence on its own.

### Sizes (measured with the REBALANCE-SPEC script on content/L200.json)
- Concept notes 377-397 words (`wc -w`), all ≤ 400.
- **Concept share 18.6 % (2,050 concept / 8,959 hands-on words; target 25-30 %).** Notes are at the 400-word ceiling; the hands-on side is dominated by the required `code` field (~2,190 words for 5 files of 72-91 lines), steps with per-OS `mac`/`windows` commands, `codeWalkthrough`, `buildTask` and two `agentAssist` blocks. Reaching 25 % would need ~3,000 fewer hands-on words; not done (SPEC: report, never pad notes past 400).
- Main lab files 72-91 lines; `memory_agent.py` is 91 lines (1 over the ~90 guideline).

## Update pass: learning tools + review fixes (2026-10-28, UPDATE-TOOLS-REVIEW-SPEC)
### Learning tools
- **All tool exercises are pending a manual run** (no GUI, Node packages or downloads in the sandbox). `expected` values quote the lab's real output to compare against; only `export_embeddings.py` (lesson 7 helper for Orange/KNIME) was run here, against the fake server.
- Install commands and versions are copied from `kb/shared/LEARNING-TOOLS-CATALOG.md` / `WORKSTATION-SETUP.md`. Not verified by the catalogue and therefore not stated as fact: KNIME winget id, MCP Inspector stdio-command arguments (the exercise uses the web UI's server form), exact promptfoo provider id syntax beyond "ollama:", whether the OpenAI–promptfoo deal has closed, AnythingLLM Pro limits, Open WebUI setting names beyond "ask first".
- Orange's Text add-on licence is unverified and its Document Embedding is remote – the exercise uses the lab's own CSV instead.

### Review findings
Fixed here:
- **F01** – topic README states "not yet run on macOS or Windows; CI matrix pending".
- **F02/F07** – every lesson has `validation.pendingCi` (files/variants not run: real model, sqlite-vec, pgvector, jsonschema, MCP SDK, experimental llama-server MCP, manual installs); README defines the key.
- **F03** – L100 `next` now names real L200 lessons (#7–#11); L200 `next` = "L300 (planned): …".
- **F05/F04** – lesson 1, lab 1 README, topic README and HARDWARE use the canonical WORKSTATION-SETUP commands (brew `ollama` + `brew services`, `OllamaSetup.exe`, winget `Python.Python.3.12`, `PYTHONUTF8`) and link to it. Node is not used by the labs (only by optional tools: Node 24 from the shared page).
- **F19** – every lab reads `LOCAL_MODEL_URL` / `LOCAL_MODEL` first and falls back to `BASE_URL` / `MODEL`; tests set the new names; `test_setup.test_cli_old_env_names_still_work` proves the fallback; docs updated. `.github/workflows/labs.yml` (not edited here – the root CI job is built separately) still sets `BASE_URL`/`MODEL`; this works through the fallback, but the root job should switch to the new names.
- **F12** – the -32022 error now lists only versions accepted in `_meta` (`["2026-07-28"]`); 2025-11-25 is reachable only through `initialize` (documented in lab, README, tryIt, concept note; `research/L200_concept_examples.out.txt` regenerated).
- **F13** – `llama-server --mcp-servers-config` marked experimental with a link to the llama-server README.
- **F15/F16/F17** – LangGraph (vendor docs) removed from lesson 6 sources and VERIFIED-RESOURCES (kept as an `equivalents` line); duplicates merged (one row per URL); raw `windows.mdx` and the v0.13.5 README dropped; HF blog and MCP "latest" page marked background. No localhost URLs or unofficial mirrors in this topic (F06/F14 n/a).
- **F08** – `seeAlso`: lesson 10 ↔ application-architecture L100 #4, lesson 11 ↔ distributed-systems L200 #11.
- **F20** – `projectFiles` globs replaced by the real files.
- **F27** – `__pycache__` folders deleted; topic `.gitignore` added (pycache, logs, `*.db`, generated `embeddings.csv`).
Recorded, not fixed:
- **F09** – concept share fell further because `learningTools`, `seeAlso` and `pendingCi` count as hands-on words: L100 18.6 % → 17.2 % (1,541 / 7,437), L200 18.6 % → 17.2 % (2,050 / 9,850), measured with the REBALANCE-SPEC script. Notes unchanged in size (L100 242–249, L200 377–397 words); not padded.
- **F01** – macOS/Windows runs still need the root CI workflow.

### L300 candidates (from former L100 `next` lines, F03)
Streaming responses (`stream: true`); prompt evaluation sets (measure a prompt change); workflow patterns (chaining, routing) vs agents; schema design for extraction pipelines and extraction accuracy.

## L300 (built 2026-10-28, L300-SPEC "Harden it")
### Pending CI / manual (not executable in the sandbox – no package installs, no Node packages)
- **promptfoo equivalent (lesson 12)** – `promptfooconfig.yaml` + generated `promptfoo_tests.jsonl` were written from the configuration guide and the OpenAI-provider page (`openai:chat:<model>`, `apiBaseUrl`, `apiKeyRequired: false`, `useDefaultApiKey: false`, `tests: file://…jsonl`, `-p` prompt override); never run. Expected exit codes (0 for v1, 100 for v2) come from issue #741 and a tutorial, not from a run. The CI `promptfoo` job uses `actions/setup-node` pinned to the SHA shown in promptfoo's CI/CD docs (# v6) – not checked against the action's own releases.
- **OpenTelemetry SDK equivalent (lesson 13)** – `otel_sdk_equivalent.py` uses `TracerProvider`, `SimpleSpanProcessor`, `InMemorySpanExporter`, `start_as_current_span(kind=…)` from opentelemetry-sdk 1.45.1; written from long-standing SDK API knowledge, not from a fetched API page; never run (`test_otel_sdk_equivalent` skips).
- **Learning-tool exercises** – promptfoo (12, 16), Orange and Jaeger (13), Toxiproxy (14), Open WebUI (15), garak (16) are pending a manual run; `expected` quotes the lab's real output.
- **promptfoo red team / garak (lesson 16)** – commands from docs/README only; need a generator model and network.
- **Real-model runs** of every L300 script (CI `real_model` job, exit codes only). How often a real model obeys injected text, how its scores compare with the fake's golden-set results, and real timeout/latency behaviour were **not measured**.
- **macOS / Windows** – `platforms: expected` for all five lessons. Lesson 14 asserts wall-clock bounds (naive > 4 s, hardened < 3 s); margins are wide but untested on Windows timer resolution or slow runners.

### Unverified / partly verified facts
- **OTel execute_tool attributes.** `gen_ai.tool.name` and `gen_ai.tool.call.id` are corroborated (official repo commit message + a practitioner write-up); the execute-tool attribute table itself was truncated in every fetch. `gen_ai.tool.type` was not seen in fetched text. INTERNAL span kind for in-process tools is this course's choice.
- **`gen_ai.provider.name` for Ollama.** Not in the well-known list fetched on 2026-10-28; the labs use the custom value `ollama` (allowed by the conventions), overridable with `GENAI_PROVIDER`.
- **GenAI conventions status** is Development; names may still change. Instrumentations on v1.36.0 or older use `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` to switch.
- **RFC 9110 wording.** The fetch returned only the document start; 503/Retry-After and "idempotent methods" statements are cross-checked via urllib3's documented defaults and the IETF idempotency draft's citation of RFC 9110.
- **IETF Idempotency-Key** is an active Internet-Draft (-08), not an RFC; the 422 response for a reused key with a different body follows the draft's error-handling section headings and common practice – the section text was not fetched in full.
- **garak version** 0.17.1 (2026-10-16) is from piwheels; pypi.org was withheld by the fetch tool. garak is now in the catalogue (0.17.1, GitHub releases ≈2026-10-21) and is a lesson-16 `learningTools` entry (update pass below).
- **promptfoo.dev red-team pages** were withheld by the fetch tool; the GitHub source of the same doc (search result) and the red-teaming guide snippet were used.
- **MCP tool-annotation defaults** (readOnly false, destructive true, idempotent false, openWorld true) are from the MCP C# SDK reference and the MCP project blog; the schema page itself was not fetched.

### Fake-server limits added for L300 (`labs/L300/fake_server_l300.py`)
- **Shared helper untouched.** `labs/L100/01-setup/fake_model_server.py` stays byte-identical to `kb/shared/local_agent/` (`test_shared_helper.py` passes); L300 rules live in a wrapper (subclassed handler + `l300_reply`), documented in its header and tested by `labs/L300/test_fake_server_l300.py`.
- **Rule T (tickets)** classifies by keyword and only into categories named in the prompt – this is what makes the v2 "cleanup" break exactly t07 and t15. Real models degrade less predictably.
- **Rule A1/A2 (injection, exfiltration)** obey any matching injected instruction and substitute `$SECRET` with the first `sk-…` string seen – scripted worst cases, not measured model behaviour.
- **Rule F (faults)** draws one seeded number per request in arrival order; concurrency changes the sequence. 503 carries `Retry-After: 0`; the hardened client does not read Retry-After (urllib3 does) – noted as an improvement.
- **Token counts are word counts**; tool-call turns report 0 completion tokens. Costs in lesson 14 use illustrative prices.
- **payments_service.py** is a stdlib stand-in (SQLite in memory); real payment APIs differ in key lifetime, concurrency (409 while in flight) and error bodies.

### Sizes (measured)
- Concept notes 483–548 words (`wc -w`), within 450–550.
- **Concept share 17.6 %** (2,725 concept / 12,783 hands-on words with the REBALANCE-SPEC script on content/L300.json; target 30–35 %). Notes were not padded past 550 and labs were not cut (L300-SPEC: report the share). The hands-on side is dominated by the required `code` field, steps with mac/windows commands, 7-item `codeWalkthrough`s, `failureLab`, `tradeOffs` and test cases.
- Main lab files 92–120 lines (`traced_agent.py` 120, `resilient_agent.py` 116).
- Lesson 14's tests take about 45 s (the failure-lab test runs both loops against 2 s stalls).

## L300 update pass (2026-10-28, UPDATE-L300-SPEC: review fixes + learning tools)
### Fixed
- **R3-02** – lesson 13 `test_build_task` no longer depends on wall-clock time: it swaps `traced_agent.time` for a fake clock (time moves only in the cold-index sleep, exactly 600 ms; HTTP calls 0 ms), counts the 8 spans and asserts the exact violation line. The failure-lab trace test uses the same clock. 5/5 runs OK.
- **R3-06** – every L300 build task now has a learner file shipped **unfixed** in the lab folder (`category_gate.py`, `latency_budget.py`, `circuit_breaker.py`, `resumable_gate.py`, `refund_session.py`; the fix lives only in `solution/`). `BUILD_TARGET=mine` (the distributed-systems switch) points `test_build_task` at it; fail-before / pass-after observed for all 5 and pasted in the READMEs.
- **R3-07** – lesson 16 promptfoo red team is local-first: `promptfoo-redteam-local.yaml` (target, attacker and grader = Ollama; `excessive-agency` + one `policy`; strategies `basic`, `base64` – none on the remote-only list) plus `PROMPTFOO_DISABLE_TELEMETRY=1`, `PROMPTFOO_DISABLE_REMOTE_GENERATION=true`, `PROMPTFOO_DISABLE_UPDATE=1` (zsh + PowerShell); `test_promptfoo_local_config.py` keeps it that way. What still leaves the machine is stated (npm download, account/licence/probe-usage checks, sharing). Lesson 12 and the CI promptfoo job set the telemetry variable. garak added as the alternative that talks only to Ollama.
- **R3-18** – `agent_assist.validate()` never raises: per-variant `try/except`, returns `(accepted, rejected)`; a non-JSON reply gives `([], ['reply is not JSON'])` (new test cases).
- **R3-04** – seeAlso added: #13 → distributed-systems L300 #15; #14 → application-architecture L300 #13 (one term: circuit breaker); #15 → distributed-systems L300 #14; #16 → cryptography L300 #16. Titles copied from those topics' JSON.
- **R3-05** – L200 #7–10 `next` now name L300 #12, #15, #15, #14 with exact titles.
- **R3-13** – L100 #2: Hugging Face blog replaced by Holtzman et al. (arXiv 1904.09751); the blog stays as a one-line equivalent.
- **R3-14** – concept share reported in `documentation/README.md` for all three levels.

### Recorded, not fixed
- **R3-06 (scope)** – the failure lab itself still ships both sides as a worked example (`naive_agent.py` / `resilient_agent.py`, `untraced_run.py` / `traced_agent.py`, `naive_refund.py` / `safe_tools.py`, unprotected / protected run): the lesson shows the fault and fix; the learner's own hardening change is the build task.
- **R3-04 (back-links)** – the reverse links (distributed-systems L100 #4 and L300 #14/#15, application-architecture L300 #13, cryptography L300 #16 → ai-agents) live in those topics' files and were not edited in this pass.
- **R3-05 (L400 candidates)** – hybrid search and re-ranking with retrieval eval sets; tool routing and parallel calls at scale; per-user memory and retention policies; remote MCP over Streamable HTTP (authorization, caching).
- **R3-07 (unverified)** – promptfoo local config not run; `policy`, `excessive-agency`, `basic`, `base64` ids come from promptfoo's docs pages/examples; which endpoint the account/usage check calls was not documented. The promptfoo.dev red-team configuration page was withheld by the fetch tool (GitHub source used).
- **garak** – the Ollama generator (`--target_type ollama`, default host 127.0.0.1:11434) is from the reference docs, not run; whether `probes.promptinject` detectors download data on first use and whether garak makes any other network call were not verified; no Windows run.
- **Jaeger / Toxiproxy** – `otel_sdk_equivalent.py --otlp` (needs `opentelemetry-exporter-otlp-proto-http==1.45.1`, verified on PyPI 2026-10-06) and the Toxiproxy proxy were not run. The Toxiproxy Mac command is copied from the catalogue (includes `brew tap shopify/shopify`; review R3-20 says the formula is in homebrew-core).
- **R3-01** – `platforms` stay `expected`; no macOS/Windows run.
- **Concept share** (REBALANCE script): L100 17.1 %, L200 17.1 %, L300 16.3 % (was 17.6 %; learningTools, seeAlso and build-task text add hands-on words). Notes not padded.


## L400 + capstone (built 2026-10-28, L400-SPEC "Design it")
### Pending CI / manual (not executable in the sandbox – no package installs, no model download)
- **Temporal equivalent** (lesson 18): `temporal_equivalent.py` + `test_temporal_equivalent.py` against temporalio 1.34.0 (PyPI, verified); `WorkflowEnvironment.start_local()` downloads a dev server at test time – never run here; CI job `temporal` (RUN_TEMPORAL=1). The SDK licence was not shown in the fetched PyPI text (the repo is MIT per the catalogue's Temporal entry, not re-fetched).
- **Real hardware** (lesson 19): `real_model_probe.py` (Ollama /api/chat timings and `prompt_eval_cached_count`) on a Mac mini (Metal) and a Windows PC (CUDA/CPU) – manual. Until then the sizing table's decode speeds, OS reserves, prefill speed-up and cached-token discount are labelled ASSUMPTIONS in `cost_model.py`.
- **Real model runs** of patterns.py, durable.py, route_cost.py, edge.py (CI `real_model` job, exit codes only) and of the capstone (needs an embedding model; manual).
- **Learning-tool exercises** (Langflow 17; Temporal Web UI and Toxiproxy 18; Ollama 19; promptfoo 20/21; garak 21; MCP Inspector and Orange 22) – manual, expected values written from the lab output.
- **platforms** stay `expected` (R3-01 still open for every level).

### Unverified / partly verified facts
- **Chi-square critical values** 13.277 (df 4) and 6.635 (df 1) at α = 0.01 are standard table values; the NIST handbook's table page itself was not fetched (the test page was).
- **Mac mini line-up** is from apple.com/mac-mini/specs on 2026-10-28 (M6 and M5 Pro); configurations change – re-check before buying. No Windows GPU bandwidths were used (card-specific).
- **Qwen2.5 sizes** combine Ollama download sizes (L100 HARDWARE.md, Q4_K_M) with Hugging Face config.json (bf16 originals); the KV formula assumes Ollama's default f16 KV cache.
- **SRE fast-burn 14.4** is reused from application-architecture L300 #15 (verified there, review R3); not re-fetched for the capstone.

### Fake-server limits added for L400 (`labs/L400/fake_server_l400.py`)
- Wraps L300 (which wraps L100); `kb/shared/local_agent/` and the L100/L300 files are untouched. Rules K, P, G, S, V, M, M2–M5, W, D, I, J are documented in the header and tested by `labs/L400/test_fake_server_l400.py`.
- **Tokens are words**, now including tool schemas and tool-call JSON (L400 only); the context limit (rule K) rejects with HTTP 400 like vLLM/OpenAI – Ollama truncates instead.
- **Prefix cache (rule P)** is one slot per model with word-level prefix matching; real servers cache in token blocks and per slot. `route_cost.run()` warms the slot so results do not depend on run order.
- **Scripted model differences:** fake-small (long tickets → prose-wrapped JSON; only "outage" is high priority) and fake-model:v2 (urgent/asap/immediately → normal) are documented rules, not measured model behaviour. Rule D and rule I obey steering text every time – worst cases.
- **Cost and latency** in lesson 19 are a model (≈2 × parameters per token; decode ≤ bandwidth ÷ weights × 50 %), not measurements.

### Found while building (recorded, not fixed – outside L400 scope)
- **L200 `mcp_client.StdioClient` matches replies by arrival order, not by id.** If the server starts slower than the client timeout (10 s default), `connect()` falls back to the legacy handshake and every later reply is shifted by one (seen on the sandbox's slow network mount: KeyError 'structuredContent'). The capstone uses `timeout=60` (`triage.start_mcp`); a fix in lesson 10 would key replies by id.
- **ResourceWarning: unclosed file** from `StdioClient.close()` (stdout pipe not closed) – harmless, visible in verbose capstone test runs.
- **Slow SQLite on network mounts:** lessons 18/21 and the capstone commit every step; on the sandbox mount a full L400 run takes ~10 minutes (local SSDs and CI are much faster). No timing assertions depend on it.

### Sizes (measured)
- Concept notes (wc -w, UTF-8 locale): 17–21 694–750 (target 600–750); capstone 510 (target 400–600).
- **Concept share L400 + capstone 18.0 %** (4,164 concept / 19,012 hands-on; REBALANCE-SPEC script on content/L400.json; target 35–40 %). Notes are at full length; labs were not cut (L400-SPEC: report it).
- Main lab files: patterns.py 133, durable.py 148, route_cost.py 92, edge.py 99, governance.py 130, triage.py 139 lines (helpers allowed).

### L400 candidates (for further study – where Capstone #22 `next` points)
- Hybrid search and re-ranking with retrieval eval sets (from L200 #7).
- Remote MCP over Streamable HTTP with authorization and caching (from L200 #10).
- Sandboxed execution for code-running tools (containers / WASM) with resource limits.
- Quantization choice (Q4_K_M vs Q8_0, KV cache q8_0) measured against the golden set on Metal and CUDA.
- Multi-tenant serving: per-tenant budgets, rate limits and isolation of memories; per-user memory with retention (from L200 #9).
- Online labelled evaluation and human feedback loops; shadow/canary model rollout with automatic rollback.
- OTLP export of the capstone's spans to Jaeger; a Temporal deployment of the capstone workflow.

## L500 "Theory & Rigour" (built 2026-10-30, L500-SPEC)
### Not run yet
- **macOS / Windows.** `labs/L500/*` ran only in the Linux sandbox (Python 3.12.15, numpy 2.5.3). Output is printed to 4 decimals from seeded generators (numpy PCG64, `random.Random`) so it should match on every OS, but `platforms` stays `expected` until the CI matrix (which now runs the L500 tests and `research/l500_checks.py`) has passed.
- No real model is used in L500 (the labs check mathematics), so there is no `agentAssist` and no pending real-model job.

### Unverified / partly verified facts
- **Paywalled originals.** McNemar (1947) and Hart, Nilsson & Raphael (1968): only landing/abstract pages were retrieved; Wilson (1927) and Brown, Cai & DasGupta (2001) are cited through the NIST e-Handbook (the Project Euclid page returned no document). The proofs in lessons 24-25 are self-contained and checked numerically, so nothing depends on unread text.
- **Moffatt v. Air Canada.** CanLII returned no document; the reasons were read from a copy hosted by The Sedona Conference (identical case number, date, member and paragraph structure). In that copy, paragraph 38's components (380 + 62.12 + 22.11) sum to 464.23 while the paragraph states 474.23; the stated totals (979.48, damages 650.88, award 812.02) are used in problem 26-p4 and the discrepancy was not checked against the official CanLII text.
- **EU AI Act article text.** The EUR-Lex page was fetched (recitals, consolidated-version list 27/07/2026), but the long HTML truncates before the articles; the wording of Art. 14 and Art. 50 was read on artificialintelligenceact.eu (a non-official mirror that shows amended application dates) and the omnibus dates were cross-checked with the European Parliament Legislative Train and the OJ title of Regulation (EU) 2026/1744. One summary notes an exception to the 2 August 2026 transparency date for certain systems (text truncated in the search result); the lessons only rely on Art. 50(1), whose date the mirror shows as 2 August 2026.
- **NIST AI RMF 1.0 is under revision** (NIST page, retrieved 2026-10-30). Lesson 26 quotes 1.0; re-check when a revision is published.
- **ABET.** L500-SPEC asks for "ABET student outcomes 1-7"; those are the *engineering* (EAC) outcomes. Computing (CAC) programmes have outcomes 1-5 plus a programme outcome (6 for computer science). The syllabus maps to both; the mapping is the course team's proposal, not an ABET determination.
- **14-week plan.** The spec says the plan comes "from the review"; no 14-week plan was found in kb/REVIEW-*.md, so `content/assessment/syllabus.md` proposes one.

### Design limits (stated in the lessons)
- Theorem checks are numerical *illustrations* of proved results, not proofs. T4 in lesson 25 cannot "check" undecidability; its check demonstrates the reduction (a budgeted checker answers "unknown") and the conservative allow-list.
- The concept inventory uses `lesson: 23` for every item, as the spec requires; the lesson that addresses each misconception is in the extra `targets` field.
- `kb/tools/check_qbank.py` still reads only L100-L400 (the spec forbids editing kb/tools); `research/check_l500_qbank.py` applies the same rules to `content/qbank/L500.json` and the concept inventory, and `research/qbank_checks.py` now recomputes L500 calculations and runs L500 code-reading snippets.
- Exam model answers: every number is recomputed by `research/l500_checks.py`; the prose parts are not machine-checked.

### Sizes (measured, wc -w)
- Concept notes: 23 – 1,161; 24 – 1,094; 25 – 1,138 (target 900-1,300); 26 – 938 (700-1,000); 27 – 604 (500-800).
- 12 theorems (4 + 4 + 4), 37 problems (9 + 8 + 8 + 6 + 6; 19 calculations recomputed), 45 qbank questions (9 per lesson), 15 concept-inventory items.

## Found while writing the explanations (Nov 2026)
- **L200 #10:** the MCP client does not match replies to requests by id. On slow storage a late reply was read as the answer to the next request. Fix: match on the JSON-RPC id and drop unknown ids (the explanation uses this as a 'what would look wrong' example).
- **L200 #8:** the try-it said notes are joined by ' / '; the code uses ' | '. Fixed in the README.
