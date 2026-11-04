# L400 research evidence – AI Agents

Method: SPEC "Research method" (questions → candidates → screen → score ≥ 8/12 → cross-check with ≥ 2 sources, one official). Retrieval date for every URL: 2026-10-28 (web_fetch). Score order: implementable / current / authoritative / open / transferable / right depth. Vendor-neutral: papers, specs, official docs and maintained OSS repos only; vendor pages appear only as one-line equivalents. Worked-example numbers in the L400 concept notes come from `research/L400_concept_examples.py` (output: `L400_concept_examples.out.txt`, re-checked in CI; no wall-clock values).

---
## Lesson 17 – Multi-agent patterns
**Questions** 1. Is there primary evidence on when multi-agent systems beat a single agent, and how they fail? 2. What do planner/executor (plan without observations) and interleaved ReAct each cost? 3. Which primary sources define supervisor/worker and router (controller) designs?

| source | decision | score | reason |
|---|---|---|---|
| arxiv.org/abs/2503.13657 (Cemri et al., v3 2025-10-26) | kept | 2/2/2/2/2/2 = 12 | 1,600+ traces, 7 MAS frameworks; "performance gains … often minimal"; 14 failure modes in 3 categories (system design, inter-agent misalignment, task verification) |
| arxiv.org/abs/2210.03629 (ReAct) | kept | 2/1/2/2/2/2 = 11 | interleaved reasoning and acting; the single-agent baseline |
| arxiv.org/abs/2305.18323 (ReWOO) | kept | 2/1/2/2/2/2 = 11 | "detaches the reasoning process from external observations"; 5x token efficiency on HotpotQA |
| arxiv.org/abs/2308.08155 (AutoGen) | kept | 1/1/2/2/2/1 = 9 | multi-agent conversation framework (supervisor/worker, group chat) |
| arxiv.org/abs/2303.17580 (HuggingGPT) | kept | 1/1/2/2/2/1 = 9 | LLM as controller: plan, select model, execute, summarise (planner + router) |
| vendor "building agents" blog posts | dropped | – | vendor pages; not primary |

**Key facts:** the lab reproduces both sides of ReWOO (planner: fewest calls/tokens, 1,937; fails the observation-dependent t09) and Cemri et al.'s failure classes (router: missing tool = system design; supervisor: lost hand-off = inter-agent misalignment). Context overflow behaviour: vLLM/OpenAI-style servers reject (the fake returns HTTP 400 `context_length_exceeded`), Ollama truncates to `num_ctx` (Ollama FAQ: default 4096) – recorded as a simulator difference.

## Lesson 18 – Durable agent workflows
**Questions** 1. How does Temporal make workflows durable, and what must workflow code avoid? 2. What does SQLite guarantee about a commit interrupted by a crash? 3. Which Python SDK version/API is current for the Temporal equivalent?

| source | decision | score | reason |
|---|---|---|---|
| docs.temporal.io/workflows | kept | 2/2/2/2/2/2 = 12 | Event History is "the source of truth"; replay re-runs code using recorded events; activities run once, results reused; determinism constraints |
| pypi.org/project/temporalio (1.34.0) | kept | 2/2/2/2/1/2 = 11 | signals (`@workflow.signal`), `workflow.wait_condition(..., timeout=)` raising `asyncio.TimeoutError`, `WorkflowEnvironment` (time-skipping env "does not work on ARM" → the lab uses `start_local()`), `activity.info()` |
| sqlite.org/atomiccommit.html | kept | 2/2/2/2/2/1 = 11 | "transactions appear to be atomic even if the transaction is interrupted by an operating system crash or power failure" |
| github.com/temporalio/cli (catalogue) | kept (tool) | 2/2/2/2/1/1 = 10 | `temporal server start-dev`, Web UI :8233, MIT |
| IETF draft-ietf-httpapi-idempotency-key-header (L300) | reused | 11 | key reuse → replay; different body → 422 |

**Key facts:** the temporalio licence was not shown on the PyPI page text fetched (the SDK repo is MIT per its GitHub page – not re-fetched; KNOWN-GAPS). `WorkflowEnvironment.start_local()` downloads a dev server at test time – pending CI.

## Lesson 19 – Cost, latency and model choice
**Questions** 1. What is the primary evidence for cascades and routers? 2. How do llama.cpp, vLLM and Ollama expose prefix caching, parallel slots and context size? 3. Which official numbers size a Mac mini vs a Windows PC (memory, bandwidth, model size, KV per token, GPU support)?

| source | decision | score | reason |
|---|---|---|---|
| arxiv.org/abs/2305.05176 (FrugalGPT) | kept | 2/1/2/2/2/2 = 11 | LLM cascade; matches the best model with up to 98 % lower cost |
| arxiv.org/abs/2406.18665 (RouteLLM, v4 2025-02-23) | kept | 2/2/2/2/2/1 = 11 | strong/weak routers; "over 2 times" cost reduction |
| github.com/ggml-org/llama.cpp tools/server/README.md | kept | 2/2/2/2/2/1 = 11 | `--cache-prompt` (default enabled), `-np/--parallel`, continuous batching (default enabled), `cache_prompt` evaluates only the unseen suffix |
| docs.vllm.ai automatic_prefix_caching | kept | 2/2/2/2/2/2 = 12 | APC reuses KV of a shared prefix; helps prefill, not decode |
| docs.ollama.com/faq | kept | 2/2/2/2/2/2 = 12 | default context 4096; RAM scales with OLLAMA_NUM_PARALLEL x OLLAMA_CONTEXT_LENGTH; KV cache type default f16; `ollama ps` CPU/GPU split; GPU acceleration not available in Docker Desktop on macOS |
| docs.ollama.com/api/chat | kept | 2/2/2/2/1/2 = 11 | `prompt_eval_count`, `prompt_eval_cached_count`, `eval_count`, `eval_duration` (ns) – used by real_model_probe.py |
| docs.ollama.com/gpu | kept | 2/2/2/2/1/1 = 10 | NVIDIA compute capability 5.0+, driver 550+ (570+ for 5.0-6.2); Metal on Apple; Vulkan on Windows/Linux |
| apple.com/mac-mini/specs | kept (hardware facts) | 2/2/2/1/1/2 = 10 | M6: 16 GB (153 GB/s) or 24/32 GB (170 GB/s); M5 Pro: 24/48/64 GB, 307 GB/s |
| huggingface.co Qwen2.5-1.5B/7B/14B-Instruct config.json | kept | 2/2/2/2/1/2 = 11 | layers / KV heads / hidden size: 28/2/1536, 28/4/3584, 48/8/5120 → head_dim 128 |
| ollama.com library sizes (from HARDWARE.md, L100) | reused | 10 | qwen2.5 Q4_K_M 0.986 / 4.7 / 9.0 GB |

**Key facts / assumptions:** KV bytes per token = 2 x layers x kv_heads x head_dim x 2 (f16): 28.7 / 57.3 / 196.6 kB. "Decode ≤ bandwidth / weights" is a derivation (each token reads every weight once), not a vendor figure; the 50 % efficiency, 8x prefill speed-up, OS reserves and 10 % cached-token cost are labelled ASSUMPTIONS in cost_model.py, to be replaced by real_model_probe.py measurements. No GPU SKU bandwidths were used for Windows (card-dependent).

## Lesson 20 – Deterministic core, LLM at the edge
**Questions** 1. Which primary sources describe agent designs with provable resistance to prompt injection? 2. How do schema validation and allow-lists relate to (not replace) a decision boundary? 3. Where does "the model explains, code decides" come from in this KB?

| source | decision | score | reason |
|---|---|---|---|
| arxiv.org/abs/2506.08837 (Beurer-Kellner et al., v3 2025-06-27) | kept | 2/2/2/2/2/2 = 12 | "principled design patterns for building AI agents with provable resistance to prompt injection"; utility/security trade-offs |
| arxiv.org/abs/2503.18813 (CaMeL, L300) | reused | 10 | control/data flow separation |
| genai.owasp.org LLM06:2025 Excessive Agency (L300) | reused | 11 | limit functionality, permissions and autonomy |
| json-schema.org/draft/2020-12 | kept | 2/2/2/2/2/1 = 11 | enum, additionalProperties – the validation vocabulary of schema_check.py (lesson 8) |
| KB PLATFORM-AGENT-SPEC / LPC1768 guide rule | reused | – | "deterministic code decides; the agent only proposes/explains" |

**Key facts:** the lab's measured result (6 / 5 / 0 wrong decisions) shows the same ordering the papers argue: validation stops malformed or out-of-range answers only. Pattern names quoted in the concept note (action-selector, plan-then-execute, context-minimization) were checked in the paper's HTML v3 (§3.1 lists six: action-selector, plan-then-execute, LLM map-reduce, dual LLM, code-then-execute, context-minimization); its guiding principle - once untrusted input is ingested, it must be impossible for it to trigger consequential actions - is the lab's boundary.

## Lesson 21 – Governance and evaluation in production
**Questions** 1. Which public framework lists the controls for generative AI in production? 2. Which statistical test fits label-free drift on categorical outputs, and what are the critical values? 3. How do you pin a local model, and what must a decision record contain?

| source | decision | score | reason |
|---|---|---|---|
| nist.gov – NIST AI 600-1 Generative AI Profile (2024-07-26, updated 2026-04-08) | kept | 2/2/2/2/2/1 = 11 | companion to AI RMF 1.0 for generative AI |
| itl.nist.gov e-Handbook 1.3.5.15 Chi-Square Goodness-of-Fit | kept | 2/2/2/2/2/2 = 12 | statistic Σ(O−E)²/E, df = k − c, binned counts, sample-size caveat; critical values 13.277 (df 4) and 6.635 (df 1) at α = 0.01 from the standard chi-square table |
| docs.ollama.com/api/tags | kept | 2/2/2/2/1/2 = 11 | `models[].name`, `digest` (64 hex) |
| cognitect.com – Nygard, Documenting Architecture Decisions | kept | 2/1/2/2/2/2 = 11 | Title, Context, Decision, Status, Consequences |
| eur-lex.europa.eu GDPR 2016/679 | kept | 1/2/2/2/1/1 = 9 | Art. 5(1)(e) storage limitation; recital 39: time limits for erasure or periodic review |
| genai.owasp.org LLM01:2025 (L200) | reused | 11 | injection risk the red-team suite covers |

**Key facts:** the chi-square table page itself was not fetched (values are the standard table values; KNOWN-GAPS). Ollama pinning by digest is a lab convention; Ollama has no built-in lock file.

## Capstone 22 – Incident-triage agent
**Questions** 1. What does primary SRE guidance say about declaring and running incidents? 2. Which burn-rate threshold marks a fast burn? 3. How should an MCP host treat tools with side effects?

| source | decision | score | reason |
|---|---|---|---|
| sre.google/sre-book/managing-incidents | kept | 2/1/2/2/2/2 = 11 | roles, live incident document, "set clear conditions for declaring an incident" |
| sre.google/workbook/alerting-on-slos (L300 app-arch, reviewed R3) | reused | 11 | burn rate 14.4 fast-burn page |
| modelcontextprotocol.io 2026-07-28 Tools (L300) | reused | 12 | human in the loop; annotations untrusted |
| mermaid.js.org flowchart syntax | kept | 2/2/1/2/1/1 = 9 | diagram file format |
| vendor incident-tool docs (PagerDuty/Opsgenie) | dropped (one-line equivalent) | – | vendor pages |
