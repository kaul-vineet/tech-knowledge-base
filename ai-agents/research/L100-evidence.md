# L100 research evidence – AI Agents

Method: SPEC "Research method". Retrieval date for every URL: 2026-10-28 (web_fetch/web_search). Score order: implementable / current / authoritative / open / transferable / right depth.

---
## Lesson 1 – Set up your environment
**Questions**
1. Which small open-weight model with tool support runs on CPU via Ollama, and what is its current tag?
2. How is Ollama installed/pinned on Linux, and where does it listen?
3. How do I build a minimal stdlib HTTP server that speaks the same JSON?

**Candidates**
| source | decision | score | reason |
|---|---|---|---|
| docs.ollama.com/linux | kept | 2/2/2/2/1/1 = 10 | install script, `OLLAMA_VERSION=` pinning, `ollama serve` |
| github.com/ollama/ollama/releases | kept | 2/2/2/2/1/1 = 10 | current version v0.40.12 (released 2026-10-27) |
| ollama.com/library/qwen2.5/tags | kept | 2/2/2/1/1/1 = 9 | tag `qwen2.5:1.5b` (= `1.5b-instruct-q4_K_M`, 986 MB, digest 65ec06548149), `tools` capability |
| docs.python.org http.server | kept | 2/2/2/2/2/1 = 11 | `ThreadingHTTPServer`, `do_POST`, "not recommended for production" |
| docs.ollama.com/faq | kept (supporting) | 2/2/2/2/0/1 = 9 | binds 127.0.0.1:11434 by default; `OLLAMA_HOST` |
| ollama.com/library/qwen3 | considered, not main | – | tags 0.6b/1.7b with `tools thinking`; thinking output adds complexity at L100 |
| HF Qwen/Qwen2.5-1.5B-Instruct-GGUF | kept (equivalent) | 2/1/2/2/1/1 = 9 | Apache-2.0, Q4_K_M 1.12 GB for llama.cpp |

**Key facts**
- Install: `curl -fsSL https://ollama.com/install.sh | sh`; specific version via `OLLAMA_VERSION=...` – https://docs.ollama.com/linux
- Latest release v0.40.12 – https://github.com/ollama/ollama/releases
- `qwen2.5:1.5b` 986 MB, 32K context; Apache-2.0 for all sizes except 3B and 72B – https://ollama.com/library/qwen2.5 , https://ollama.com/library/qwen2.5/tags
- Ollama binds 127.0.0.1:11434 by default – https://docs.ollama.com/faq ; `/v1` base URL `http://localhost:11434/v1/` – https://docs.ollama.com/api/openai-compatibility
- `ThreadingHTTPServer` handles requests in threads; http.server not for production – https://docs.python.org/3/library/http.server.html

## Lesson 2 – Call a model over HTTP
**Questions**
1. What is the minimal request body and where is the reply in the response?
2. Which servers accept the same request, and which fields are supported?
3. What does the native (non-/v1) API look like for comparison?

| source | decision | score | reason |
|---|---|---|---|
| docs.ollama.com/api/openai-compatibility | kept | 2/2/2/2/2/2 = 12 | curl example for `/v1/chat/completions`; supported fields incl. temperature, max_tokens, tools, response_format; api_key "required but ignored" |
| llama.cpp tools/server/README.md | kept | 2/2/2/2/2/1 = 11 | compatible chat-completions route; quick start; `/health`; default 127.0.0.1:9931 |
| vLLM online serving (docs.vllm.ai/en/latest/serving/online_serving/) | kept | 2/2/2/2/2/0 = 10 | `/v1/chat/completions` supported; `user` ignored; parallel_tool_calls note; `/v1/models`, `/health` |
| Ollama API /api/chat | kept (new 2026-10-28) | 2/2/2/2/1/1 = 10 | native shape: `message`, `done_reason`, `format`, `tools`, `options` |

**Key facts** (cross-checked in ≥2 sources)
- Response text at `choices[0].message.content` – Ollama /v1 example (docs.ollama.com/api/openai-compatibility) + vLLM tool-calling example (`response.choices[0].message.tool_calls`); Ollama native `/api/chat` returns `message` at top level with `done_reason: "stop"` – docs.ollama.com/api/chat.
- Same endpoint on Ollama (`localhost:11434/v1`), llama.cpp (`/v1/chat/completions`, default 127.0.0.1:9931) and vLLM – respective docs above.

## Lesson 3 – Prompt structure
**Questions**
1. What do system vs user roles mean in practice?
2. How should few-shot examples and input data be laid out?
3. Why does the role layout matter to the model?

| source | decision | score | reason |
|---|---|---|---|
| HF Transformers prompt engineering (tasks/prompting) | kept (new 2026-10-28) | 2/2/2/2/1/1 = 10 | "Clearly separate instructions from the text of interest"; few-shot gives the output format; few-shot as user/assistant turns via the chat template |
| HF Transformers chat templates | kept | 2/2/2/2/2/0 = 10 | messages → one token sequence via chat template; roles user/assistant/system |
| Ollama /v1 compatibility | kept (supporting) | 12 | role-based messages accepted by local server |
| promptingguide.ai few-shot | dropped | – | discount-code promotion on page (marketing); content duplicated by kept sources |

**Key facts**
- "Clearly separate instructions from the text of interest"; few-shot "explicit examples give the model a better understanding of the task and the output format"; few-shot can be structured as user/assistant turns – HF prompt engineering guide.
- Message lists are converted to a token sequence with control tokens by the chat template; `system` = directives, usually first – HF chat templates.

## Lesson 4 – Structured output
**Questions**
1. Does Ollama constrain output to a JSON schema, and through which field?
2. What is the difference between JSON mode and schema-constrained output?
3. What still needs validating on the client?

| source | decision | score | reason |
|---|---|---|---|
| Ollama structured outputs | kept | 2/2/2/2/1/2 = 11 | `format: "json"` or a JSON schema on `/api/chat`; also works via `response_format` on the /v1 API; lower temperature |
| llama.cpp GBNF guide (grammars/README.md) | kept (new 2026-10-28) | 2/2/2/2/1/2 = 11 | JSON Schema → grammar; `/chat/completions` takes it in `response_format` (`json_object`+`schema` or `json_schema`); schema is not injected into the prompt; `additionalProperties` defaults to false there |
| JSON Schema reference – object | kept (new 2026-10-28) | 2/2/2/2/2/1 = 11 | properties optional unless `required`; extra properties allowed unless `additionalProperties: false` |
| llama.cpp server README | kept | 11 | "Schema-constrained JSON response format"; `--json-schema` |

**Key facts**
- Ollama: provide a JSON schema to `format`; also pass the schema in the prompt; temperature 0 – https://docs.ollama.com/capabilities/structured-outputs
- Constraint ≠ correctness: vLLM guarantees "a validly-parsable function call - not a high-quality one" (vLLM tool calling); Ollama pairs `format` with Pydantic `model_validate_json` on the reply (Ollama structured outputs) – so validate in code.
- llama.cpp: the schema "is only used to constrain the model output and is not injected into the prompt" – describe it in the prompt too (GBNF guide); Ollama: "also pass the JSON schema as a string in the prompt".
- llama.cpp server supports schema-constrained JSON – llama.cpp README.

## Lesson 5 – Your first tool call
**Questions**
1. What is the exact tools definition and tool_call/tool-result message shape?
2. How do local servers differ (argument type, flags needed)?
3. What safety rules apply to tools?

| source | decision | score | reason |
|---|---|---|---|
| vLLM tool calling | kept (new 2026-10-28) | 2/2/2/2/2/1 = 11 | `tools` list with JSON-schema `parameters`; reply `tool_calls[0].function.arguments` parsed with `json.loads`; "caller's responsibility to … handle the tool calls in your application logic" |
| MCP spec – Tools (2026-07-28) | kept (new 2026-10-28) | 2/2/2/2/2/1 = 11 | `inputSchema` is JSON Schema; human in the loop SHOULD be able to deny invocations; servers MUST validate inputs |
| Ollama tool calling | kept | 2/2/2/2/1/2 = 11 | native `/api/chat` shape (`arguments` object, `tool_name`) – differs from /v1 |
| llama.cpp function-calling | kept | 2/2/2/2/1/1 = 10 | `--jinja` needed; Qwen 2.5 native format; parallel calls off by default |
| OWASP LLM06:2025 | kept | 2/2/2/2/2/1 = 11 | excessive functionality/permissions/autonomy; require user approval |

**Key facts**
- On `/v1`, `function.arguments` is a JSON string (vLLM example: `json.loads(tool_call.arguments)`); Ollama's native `/api/chat` sends `arguments` as an object and answers with `{"role": "tool", "tool_name": …}` – Ollama tool-calling doc. `tool_call_id` matching is enforced by the lab fake server and documented in the lab.
- Code handles both string and object arguments because Ollama's native API returns an object – Ollama tool-calling doc vs vLLM tool-calling doc.
- "Utilise human-in-the-loop control to require a human to approve high-impact actions" – OWASP LLM06.

## Lesson 6 – A minimal agent loop
**Questions**
1. What is the minimal loop and its stop condition?
2. Why add a max-steps budget and approval gate?
3. What does a framework add on top?

| source | decision | score | reason |
|---|---|---|---|
| ReAct (arXiv 2210.03629) | kept | 1/1/2/1/2/2 = 9 | interleave reasoning and actions that query external sources (the pattern behind the loop) |
| MCP spec – Tools (2026-07-28) | kept (new 2026-10-28) | 11 | tool execution errors SHOULD go back to the model for self-correction; clients SHOULD implement timeouts and log tool usage; human can deny invocations |
| Ollama tool calling – agent loop | kept | 11 | `while True` loop, break when no tool_calls |
| OWASP LLM06:2025 | kept | 11 | minimise tools/permissions; approval; complete mediation in code |
| LangGraph quickstart | kept (equivalent only) | 2/2/2/2/1/0 = 9 | same loop as StateGraph with conditional edge ending on no tool_calls; example uses a hosted API key, so not used as main example |

**Key facts**
- Loop ends when there are no more tool calls – Ollama agent-loop example and LangGraph `should_continue`.
- "Clients SHOULD provide tool execution errors to language models to enable self-correction"; "Implement timeouts for tool calls"; "Log tool usage for audit purposes" – MCP Tools spec. The `max_steps` budget is this course's design choice, enforced and tested in code (no external source needed).
- "Implement authorization in downstream systems rather than relying on an LLM to decide if an action is allowed" – OWASP LLM06.

---
# Concepts layer (CONCEPTS-SPEC.md) – evidence

Worked-example numbers in every concept note come from running `research/concept_examples.py`
(output saved in `research/concept_examples.out.txt`), which uses the lab fake server and lab code. No value was computed by hand.

## Primer
**Questions:** What are agents used for in practice? What is the minimal mental model? What protocol standardises tools?
| source | decision | score | key fact used |
|---|---|---|---|
| MCP specification | kept (new) | 2/2/2/2/1/1 = 10 | JSON-RPC 2.0 between hosts, clients, servers; servers offer resources, prompts, tools; hosts must obtain user consent before invoking any tool |
| OWASP LLM06:2025 | kept (re-used) | 11 | excessive functionality / permissions / autonomy (misconception 5) |

## Concept 01 – toolchain
Facts: Ollama default bind 127.0.0.1:11434 (FAQ) and `/v1` base URL (Ollama /v1 compatibility page); `qwen2.5:1.5b` 986 MB (library tags); http.server not for production (Python docs). Computed: request = 103 bytes; fake usage 6/11/17.

## Concept 02 – stateless call, temperature
| source | decision | score | key fact |
|---|---|---|---|
| HF blog "How to generate text" | kept (new) | 1/1/2/1/2/2 = 9 | lowering the temperature of the softmax sharpens the distribution; T→0 equals greedy decoding |
| HF generation strategies docs | considered | – | greedy vs sampling defined, but no temperature definition → not cited |
Cross-check: temperature as a server knob in llama.cpp README (`--temp`) and Ollama compat (`temperature` field). The `softmax(logits / T)` form is the standard reading of "temperature of the softmax"; probabilities computed in the script (0.659/0.242/0.099 at T=1; 0.864/0.117/0.019 at T=0.5; 0.993/0.007/0.000 at T=0.2).

## Concept 03 – chat templates
HF chat templates: message list → token sequence with control tokens; ChatML-style `<|im_start|>` example shown there. HF prompt engineering: separate instructions from data; few-shot as chat turns. Computed: rendered string 195 characters; lab 3 word counts A=23, B=1, C=1.

## Concept 04 – validation
| source | decision | score | key fact |
|---|---|---|---|
| json-schema.org "What is a schema?" | kept (new) | 2/2/2/2/2/0 = 10 | schema validates structure; semantic checks need general-purpose code |
| Python json docs | kept (new) | 2/2/2/2/1/2 = 11 | JSONDecodeError has msg, pos, lineno, colno |
Computed: fenced reply → "Expecting value: line 1 column 1 (char 0)"; `isinstance(True, int)` is True; validator outputs.

## Concept 05 – tool calls
vLLM tool calling (arguments are a JSON string parsed with json.loads) cross-checked with Ollama tool-calling page (native API uses object arguments and tool_name) and MCP spec (consent before tool invocation). Computed: assistant tool_call JSON, 3 messages on second call, HTTP 400 for unknown tool_call_id.

## Concept 06 – loop
| source | decision | score | key fact |
|---|---|---|---|
| ReAct (arXiv 2210.03629) | kept (new) | 1/1/2/1/2/2 = 9 | interleaving reasoning traces and actions that query external sources |
Cross-check: loop ends when no tool calls – Ollama agent-loop example and LangGraph `should_continue`. Computed: messages 2 → 4 → 6 → 7.

---
# Vendor-neutral rebalance (REBALANCE-SPEC + user request, 2026-10-28)
**Questions:** Which open-source / standards sources state (1) the `/v1` request/response shape, (2) role layout, few-shot and delimiters, (3) schema-constrained output and its limits, (4) the tool-call shape and who executes it, (5) loop safety (errors, timeouts, human approval)?

| replaced vendor source | replaced by (fetched 2026-10-28) | score |
|---|---|---|
| vendor prompt-engineering guide (lesson 3) | HF Transformers prompt engineering + HF chat templates | 10, 10 |
| vendor structured-outputs guide (lesson 4) | llama.cpp GBNF guide + JSON Schema object reference (+ Ollama structured outputs, kept) | 11, 11 |
| vendor function-calling guide (lesson 5) | vLLM tool calling + MCP Tools spec (+ Ollama, llama.cpp, kept) | 11, 11 |
| vendor engineering article on agents (lesson 6, primer) | ReAct paper + MCP Tools spec + Ollama agent-loop example | 9, 11, 11 |

Re-fetched and still current: Ollama /v1 compatibility (v0.40.12 noted; fields incl. `tools`, `response_format`, `temperature`, `max_tokens`), llama.cpp server README (default `127.0.0.1:9931`; `--jinja` enabled by default; `-j/--json-schema`), vLLM online serving (now at `/serving/online_serving/`), Ollama tool calling (agent loop breaks when no tool calls remain), Ollama structured outputs.
Could not fetch: the raw.githubusercontent.com copy of the llama.cpp server README (empty response); the GitHub page view was used.
One-line provenance fact (primer glossary): the chat-completions format originated with OpenAI's API – vLLM lists `/v1/chat/completions` among the "OpenAI APIs" it supports and Ollama "supports a subset of the OpenAI API".

**tryIt validation:** each lab has `test_try_it_NN.py` (2 tests; unique names because every lab puts `01-setup` on `sys.path`) that makes the change and asserts the observed output; the `tryIt.expected` strings are copied from those runs.

# Mac mini + Windows hosting (PLATFORM-AGENT-SPEC, 2026-10-28)
**Questions:** (1) How is Ollama / llama.cpp installed on macOS and Windows today (app, brew, winget ids)? (2) Which GPUs accelerate it on Apple silicon and Windows, and what is the CPU fallback? (3) Where are models stored and how are they moved? (4) How is the server exposed to the other machine, and what are the risks? (5) What RAM does a model size need, per official sources?

| fact | source(s) |
|---|---|
| macOS: drag `Ollama.app` from `ollama.dmg`; macOS 14+; Apple M-series CPU+GPU, x86 CPU only; models/config in `~/.ollama` | docs.ollama.com/macos; brew cask `ollama-app` 0.40.12 (requires macOS >= 14, links the CLI) |
| macOS CLI-only alternative: `brew install ollama`, `brew services start ollama` | formulae.brew.sh/formula/ollama (0.40.11) |
| Windows: `OllamaSetup.exe`, no admin, installs in the home dir, Windows 10 22H2+, NVIDIA 551.61+, AMD ROCm v7 or Vulkan; `irm https://ollama.com/install.ps1 \| iex` also listed | docs.ollama.com/windows; ollama README (main) |
| winget id `Ollama.Ollama` (newest manifest 0.34.2) | microsoft/winget-pkgs manifests/o/Ollama/Ollama |
| GPU: NVIDIA compute capability 5.0+, AMD via ROCm v7, Apple via Metal, extra GPUs via Vulkan; `CUDA_VISIBLE_DEVICES=-1` forces CPU; Docker Desktop on macOS has no GPU | docs.ollama.com/gpu; docs.ollama.com/faq |
| `ollama ps` PROCESSOR column: 100% GPU / 100% CPU / split | docs.ollama.com/faq |
| Model paths: macOS `~/.ollama/models`, Windows `C:\Users\%username%\.ollama\models`; move with `OLLAMA_MODELS` | docs.ollama.com/faq; docs.ollama.com/windows |
| Bind `127.0.0.1:11434` by default; change with `OLLAMA_HOST`; macOS app: `launchctl setenv`, Windows: user env var, then restart | docs.ollama.com/faq |
| llama-server: default `--host 127.0.0.1`, port 9931, `--api-key`; install via `brew install llama.cpp` / `winget install llama.cpp`; backends Metal, CUDA, HIP, Vulkan | llama.cpp server README, docs/install.md, README |
| RAM: ≥ 8 GB for 7B, 16 GB for 13B, 32 GB for 33B | Ollama README @ v0.13.5 (official, tagged) |
| Memory scales with `OLLAMA_NUM_PARALLEL` × `OLLAMA_CONTEXT_LENGTH`; default context 4096 | docs.ollama.com/faq |
| Q4_K_M sizes: 1.5b 986 MB, 7b 4.7 GB, 14b 9.0 GB, 32b 20 GB | ollama.com/library/qwen2.5/tags |

Dropped (screened out): devtoolhub.com, localaimaster.com, convly.ai, lumadock.com, serverman.co.uk hardware-requirement articles – blogs with affiliate links / course funnels and unsourced tokens-per-second claims; the RAM rule was taken from the official README instead. ollama.readthedocs.io – unofficial mirror.
Cross-platform code review: labs already used `sys.executable`, `127.0.0.1`, no POSIX-only calls; fixed subprocess decoding (`encoding="utf-8"` + `PYTHONIOENCODING`) in six tests and `diff --strip-trailing-cr` + `PYTHONUTF8=1` in CI.
