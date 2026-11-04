# L300 research evidence – AI Agents

Method: SPEC "Research method" (questions → candidates → screen → score ≥ 8/12 → cross-check with ≥ 2 sources, one official). Retrieval date for every URL: 2026-10-28 (web_fetch / web_search). Score order: implementable / current / authoritative / open / transferable / right depth. Vendor-neutral: vendor-hosted guides are not used as sources; promptfoo and garak are open-source projects (catalogued / equivalents). Worked-example numbers in the concept notes come from `research/L300_concept_examples.py` (output: `L300_concept_examples.out.txt`, re-checked in CI; wall-clock timings are excluded because they vary by machine).

---
## Lesson 12 – Evaluating agents with a golden set
**Questions**
1. What is the current promptfoo config format (prompts, providers, tests from files, assertions) and how does it fail a CI job?
2. How do you point promptfoo at an OpenAI-compatible local server without a key?
3. What are the known limits of model-graded (judge) rubrics?

| source | decision | score | reason |
|---|---|---|---|
| promptfoo.dev/docs/configuration/guide | kept | 2/2/2/2/2/2 = 12 | `prompts: file://…`, `providers`, `tests: file://…` (YAML/JSON, JSONL, CSV, TS/JS), `assert` types incl. `javascript`, `contains-json`, `llm-rubric`, `defaultTest`; `promptfoo eval -c`; `-p prompt.txt -c config`; page updated 2026-10-26 |
| promptfoo.dev/docs/providers/openai | kept | 2/2/2/2/2/1 = 11 | `openai:chat:<model>` for Chat Completions; `apiBaseUrl` incl. `/v1`; `apiKeyRequired: false` + `useDefaultApiKey: false` for unauthenticated compatible servers; `PROMPTFOO_RETRY_5XX`; updated 2026-10-25 |
| promptfoo.dev/docs/integrations/ci-cd (search result text) | kept | 2/2/2/2/1/1 = 10 | eval in CI with `-o results.json`, quality gate on `stats.failures`; Node ≥ 22.22 (24 recommended) |
| github.com/promptfoo/promptfoo/issues/741 | kept (behaviour) | 2/1/2/2/1/1 = 9 | `promptfoo eval` exits 100 when ≥ 1 test fails; `PROMPTFOO_FAILED_TEST_EXIT_CODE` (#751) |
| arxiv.org/abs/2306.05685 (Zheng et al.) | kept (concept) | 1/1/2/2/2/1 = 9 | LLM-as-a-judge: position, verbosity, self-enhancement biases; >80 % agreement with humans for strong judges |
| krishnaik.in promptfoo tutorial (exit codes) | dropped | 1/2/0/1/1/1 = 6 | course page with gamification; used only to corroborate exit code 100 |

**Key facts** (cross-checked): exit code 100 on failed tests – issue #741 + tutorial; promptfoo version 0.125.1 (2026-10-25) and MIT licence – learning-tools catalogue; JSONL test files – configuration guide.

## Lesson 13 – Tracing and observability
**Questions**
1. Where do the OpenTelemetry GenAI semantic conventions live now, what is their status, and what are the current span and attribute names?
2. Which attributes carry token usage, and what about content capture?
3. Which OpenTelemetry Python SDK version is current?

| source | decision | score | reason |
|---|---|---|---|
| opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/ | kept (status) | 2/2/2/2/1/1 = 10 | semconv 1.44.0 site: "GenAI semantic conventions have moved to the OpenTelemetry GenAI semantic conventions repository" |
| raw.githubusercontent.com/open-telemetry/semantic-conventions-genai/main/docs/gen-ai/gen-ai-spans.md | kept | 2/2/2/2/2/2 = 12 | Status Development; span name `{gen_ai.operation.name} {gen_ai.request.model}`; CLIENT kind; Required `gen_ai.operation.name`, `gen_ai.provider.name`; `gen_ai.usage.input_tokens/output_tokens`, `gen_ai.response.finish_reasons`, `server.address/port`, `error.type`; operation values chat, execute_tool, invoke_agent …; content attributes Opt-In; spans cover retries of the logical operation |
| raw…/gen-ai-agent-spans.md | kept | 2/2/2/2/2/1 = 11 | `invoke_agent {gen_ai.agent.name}`; agent attributes; well-known provider list (no Ollama → custom value allowed) |
| raw.githubusercontent.com/open-telemetry/semantic-conventions/main/docs/gen-ai/gen-ai-agent-spans.md (search result) | kept (transition) | 2/1/2/2/1/1 = 9 | `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` transition for instrumentations on v1.36.0 or earlier |
| github.com/open-telemetry/semantic-conventions-genai | kept | 2/2/2/2/1/1 = 10 | Apache-2.0 repo with spans, metrics, events, MCP conventions |
| pypi.org/project/opentelemetry-sdk | kept (version) | 2/2/2/2/1/1 = 10 | 1.45.1 (2026-10-06), Apache-2.0, Python ≥ 3.10 |

**Key facts**: execute_tool attributes – the attribute table of the execute-tool section was truncated in every fetch. Cross-check: the official repo's latest commit is "feat(gen-ai): require provider-supplied tool call ID on execute_tool" (GitHub page, search result), and a practitioner write-up (hashspan.dev, 2026-10-04, background, score 7 – not a source) lists `gen_ai.tool.name` (Required) and `gen_ai.tool.call.id` (Recommended) on execute_tool. `gen_ai.tool.type` (value `function`) was **not** seen in fetched text – recorded in KNOWN-GAPS. The lab's own CLIENT/INTERNAL kinds: CLIENT for the model call is from the spans doc; INTERNAL for in-process tools is this course's choice.

## Lesson 14 – Reliability
**Questions**
1. Which failures should be retried, with what backoff, and how do mature HTTP clients express it?
2. What does HTTP say about 503 and Retry-After, and about retrying non-idempotent methods?

| source | decision | score | reason |
|---|---|---|---|
| urllib3.readthedocs.io – Retry / Timeout (2.8.0) | kept | 2/2/2/2/2/2 = 12 | default `allowed_methods` = idempotent verbs (no POST); `backoff_factor * 2**retries`, `backoff_jitter` uniform, `backoff_max` 120; `RETRY_AFTER_STATUS_CODES` {413, 429, 503}; read errors "may have side-effects" |
| rfc-editor.org/rfc/rfc9110.html | kept | 2/2/2/2/2/1 = 11 | Internet Standard; sections 9.2.2 idempotent methods, 10.2.3 Retry-After, 15.6.4 503 (the fetch returned the document start and table of contents; the section wording is cross-checked via urllib3 + the IETF idempotency draft, which cites RFC 9110 for POST/PATCH being non-idempotent) |
| MCP 2026-07-28 Tools – security considerations | kept | 12 (L200) | clients SHOULD implement timeouts for tool calls |
| GenAI spans doc | kept | 12 | a span covers the logical operation with all retries (used for lesson 13/14 link) |

## Lesson 15 – Safe tool execution
**Questions**
1. What is the current standard for idempotency keys on HTTP APIs (fingerprint, errors)?
2. What does MCP say about human approval, audit logs and tool annotations?

| source | decision | score | reason |
|---|---|---|---|
| datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/ | kept | 2/2/2/2/2/1 = 11 | -08 (2026-10-22, active WG draft, expires 2027-04-25): key generated by the client, fingerprint, error handling; POST/PATCH not idempotent per RFC 9110; timeout scenario in the introduction |
| MCP 2026-07-28 Tools | kept | 12 | human in the loop SHOULD be able to deny; clients SHOULD log tool usage for audit; annotations untrusted unless from trusted servers |
| blog.modelcontextprotocol.io – Tool annotations as risk vocabulary (2026-03-16, search result) | kept (background) | 1/2/2/2/1/1 = 9 | readOnlyHint / destructiveHint / idempotentHint / openWorldHint are hints; "clients should ignore annotations from untrusted servers" |
| MCP C# SDK ToolAnnotations reference | kept (cross-check) | 1/2/2/2/1/1 = 9 | defaults: readOnly false, destructive true, idempotent false, openWorld true |
| marcnuri.com / allmcps.com blog posts | dropped | ≤ 7 | blogs; facts already covered by the MCP project blog + SDK reference |
| docs.python.org/3/library/sqlite3.html | kept | 11 (L200) | placeholders, connection commit |

## Lesson 16 – Red-teaming prompt injection
**Questions**
1. What do current, vendor-neutral sources recommend against indirect injection and exfiltration?
2. Which open tools generate attacks (licence, status)?
3. How do research benchmarks structure attack suites?

| source | decision | score | reason |
|---|---|---|---|
| cheatsheetseries.owasp.org – LLM Prompt Injection Prevention | kept | 2/2/2/2/2/2 = 12 | screening "is not a security boundary"; Markdown/HTML image exfiltration (`<img src=…?data=SECRET>`); enforce permissions at the tool boundary; output as untrusted; smoke-test with instrumented tool substitutes and benign controls; report false positives |
| genai.owasp.org LLM01:2025 | kept | 11 (L200) | direct/indirect injection, mitigations |
| arxiv.org/abs/2503.18813 (CaMeL) | kept | 1/2/2/2/2/1 = 10 | control/data flow from the trusted query; capabilities at tool calls; 77 % vs 84 % AgentDojo tasks |
| arxiv.org/abs/2406.13352 (AgentDojo) | kept | 1/2/2/2/2/1 = 10 | 97 tasks, 629 security test cases; extensible environment |
| github.com/NVIDIA/garak | kept (equivalent) | 2/2/2/2/1/1 = 10 | Apache-2.0; probes (promptinject, encoding, xss …) and detectors; REST/OpenAI-compatible generators; JSONL reports |
| piwheels.org/project/garak | kept (version) | 1/2/1/2/1/1 = 8 | 0.17.1 released 2026-10-16 (pypi.org was withheld by the fetch tool) |
| github.com/promptfoo/promptfoo – site/docs/red-team/configuration.md (search result) | kept | 2/2/2/2/1/1 = 10 | `redteam` section: plugins, strategies, purpose; `redteam init / run / report` (promptfoo.dev page withheld by the fetch tool) |
| promptfoo.dev/docs/guides/llm-redteaming (search result) | kept (background) | 2/2/1/2/1/1 = 9 | Node ≥ 22.22; `npx promptfoo@latest redteam init`; targets incl. ollama |

**Not catalogued:** garak is not in the learning-tools catalogue, so it appears only as an `equivalents` line (licence and status verified above).

## Update pass 2026-10-28 (UPDATE-L300-SPEC) – research for R3-07 and the new learning tools
Questions: (1) What does `promptfoo redteam` send off the machine, and how is it run with a local model only? (2) How is garak pointed at Ollama, and what leaves the machine? (3) Which exporter sends the lesson-13 spans to Jaeger?
- promptfoo data-handling page (updated 2026-10-22): target evaluation is always local; without an API key, generation and grading use hosted inference at api.promptfoo.app (purpose, plugin config, prompts and target responses for grading, email). `PROMPTFOO_DISABLE_REMOTE_GENERATION=true` "is not a network isolation guarantee" and does not disable telemetry, account/license checks, sharing or setup/test helpers; remote-only plugins listed (harmful:*, bias, ssrf, bola, bfla, indirect-prompt-injection, ascii-smuggling, competitors, hijacking, off-topic, system-prompt-override) and strategies (jailbreak:composite, jailbreak:meta, goat, gcg, …). https://www.promptfoo.dev/docs/red-team/troubleshooting/data-handling/ – kept 12/12.
- promptfoo "Configuring inference" (2026-10-26): local providers via `redteam.providers` / Ollama; "usage limits still apply for locally-hosted models". Kept 11/12. Red-team configuration (GitHub docs source): `redteam.provider` controls attack generation and grading; `ollama:chat:<model>` example; `PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION`. Telemetry page: `PROMPTFOO_DISABLE_TELEMETRY=1`, `PROMPTFOO_DISABLE_UPDATE=1`.
- Plugin/strategy ids: `excessive-agency` (plugin page), `policy` (configuration page), `basic` + `base64` (basic-strategy page example). The `prompt-injection` strategy page returned no text – not used.
- garak README/FAQ/releases: `--target_type`/`--target_name`, `--spec probes.promptinject`, JSONL report; 0.16.0 unified `--spec`; 0.17.1 latest ("last week"); ~9 GB dependencies; detectors keyword-based or classifiers "locally or via API". Reference docs: `garak.generators.ollama` (OllamaGenerator, OllamaGeneratorChat; default host 127.0.0.1:11434). Kept 9–10/12. No telemetry setting found in README/FAQ (absence not proven).
- PyPI opentelemetry-exporter-otlp-proto-http 1.45.1 (2026-10-06, Apache-2.0, `OTLPSpanExporter`) – same version as opentelemetry-sdk. Kept 10/12.
- R3-13: Holtzman et al., "The Curious Case of Neural Text Degeneration" (arXiv 1904.09751, ICLR 2020) replaces the Hugging Face blog in L100 #2.
