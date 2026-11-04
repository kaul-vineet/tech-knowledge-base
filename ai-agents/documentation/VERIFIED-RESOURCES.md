# Verified resources – AI Agents (L100 + L200 + L300 + L400 + L500)

All URLs were retrieved with web_fetch on 2026-10-28. Score = implementable + current + authoritative + open + transferable + right depth (0-2 each). Kept only if ≥ 8/12.
One row per document (duplicates merged on 2026-10-28, review F16). Vendor-hosted guides appear only as one-line `equivalents` in lessons, never as sources; blogs and overview pages are marked "background".

## Sources

| title | url | type | licence | version-or-date checked | score/12 | used in lesson(s) |
|---|---|---|---|---|---|---|
| Ollama docs – OpenAI compatibility (/v1 chat completions, /v1/embeddings fields, context size) | https://docs.ollama.com/api/openai-compatibility | docs | MIT (ollama/ollama repo) | re-fetched 2026-10-28 (mentions v0.40.12) | 12 | 1, 2, 3, 7, 9, primer |
| Ollama docs – Structured outputs | https://docs.ollama.com/capabilities/structured-outputs | docs | MIT | 2026-10-28 | 11 | 4 |
| Ollama docs – Tool calling | https://docs.ollama.com/capabilities/tool-calling | docs | MIT | 2026-10-28 | 11 | 5, 6 |
| Ollama docs – Linux install | https://docs.ollama.com/linux | docs | MIT | 2026-10-28 | 10 | 1 |
| Ollama releases | https://github.com/ollama/ollama/releases | repo | MIT | v0.40.12 (latest, released 2026-10-27) | 10 | 1 |
| Ollama library – qwen2.5 tags (sizes) | https://ollama.com/library/qwen2.5/tags | docs (model registry) | model: Apache-2.0 (all sizes except 3B/72B) | 2026-10-28; qwen2.5:1.5b = digest 65ec06548149, 986 MB | 10 | 1, HARDWARE |
| Ollama docs – FAQ (bind 127.0.0.1:11434, OLLAMA_HOST, OLLAMA_MODELS, model paths, ollama ps, memory scaling) | https://docs.ollama.com/faq | docs | MIT | 2026-10-28 (no per-size RAM table) | 12 | 1, 9, HARDWARE |
| llama.cpp – llama-server README (host/port 127.0.0.1:9931, --api-key, --jinja, --json-schema, embeddings, ctx-size, MCP servers – experimental) | https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md | repo | MIT | master, commit 1b4554e, re-fetched 2026-10-28 | 12 | 1, 2, 4, 7, 9, 10, 11 |
| llama.cpp – Function calling | https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md | repo | MIT | master, commit b42b7e6 (port 9931 default) | 10 | 5 |
| Hugging Face – Qwen2.5-1.5B-Instruct-GGUF | https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF | repo (model card) | Apache-2.0 | Q4_K_M 1.12 GB | 9 | 1 (llama.cpp equivalent) |
| vLLM – Online serving (chat completions server, chat templates) | https://docs.vllm.ai/en/latest/serving/online_serving/ | docs | Apache-2.0 | page dated 2026-10-27 (the older serving URL redirects here) | 10 | 2, primer |
| Hugging Face Transformers – Chat templates | https://huggingface.co/docs/transformers/main/en/chat_templating | docs | Apache-2.0 | re-fetched 2026-10-28 | 10 | 3 |
| Python docs – http.server | https://docs.python.org/3/library/http.server.html | docs | PSF-2.0 | Python 3.15 docs (API used exists since 3.7) | 11 | 1 |
| OWASP GenAI – LLM06:2025 Excessive Agency | https://genai.owasp.org/llmrisk/llm062025-excessive-agency/ | spec/standard | CC BY-SA 4.0 | 2025 edition | 11 | 5, 6 |
| ReAct: Synergizing Reasoning and Acting in Language Models (Yao et al.) | https://arxiv.org/abs/2210.03629 | paper | arXiv preprint; licence not shown in fetched text | v3, 2023-03-10 (ICLR); re-fetched 2026-10-28 | 9 | 6, primer |
| Model Context Protocol – specification (overview) | https://modelcontextprotocol.io/specification/latest | spec (background) | open specification (MCP project) | redirected to 2026-07-28 page; page says a newer "latest" exists | 10 | background only |
| Understanding JSON Schema – What is a schema? | https://json-schema.org/understanding-json-schema/about | docs | open documentation (JSON Schema project) | 2026-10-28 | 10 | 4 |
| Python docs – json | https://docs.python.org/3/library/json.html | docs | PSF-2.0 | Python 3.15 docs | 11 | 4 |
| The Curious Case of Neural Text Degeneration (Holtzman et al., ICLR 2020) | https://arxiv.org/abs/1904.09751 | paper (primary) | arXiv | v2 2020-02-14, fetched 2026-10-28 | 10 | 2 (replaces the Hugging Face blog, R3-13; blog kept as a one-line equivalent) |
| vLLM – Tool calling | https://docs.vllm.ai/en/latest/features/tool_calling/ | docs | Apache-2.0 | page dated 2026-10-26 | 11 | 5 (wire format: `tool_calls[].function.arguments` parsed with `json.loads`; caller handles the calls) |
| MCP 2026-07-28 – Tools (human in the loop, tool execution errors, timeouts, audit logs) | https://modelcontextprotocol.io/specification/2026-07-28/server/tools | spec | open specification (MCP project) | 2026-07-28 (re-fetched) | 12 | 5, 6, 8, 10, 11, primer |
| llama.cpp – GBNF guide (JSON Schema → grammar) | https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md | repo | MIT | master, commit acecd56 | 11 | 4 (`response_format` schema constrains output; schema not injected into the prompt) |
| JSON Schema reference – object | https://json-schema.org/understanding-json-schema/reference/object | docs | open documentation (JSON Schema project) | 2026-10-28 | 11 | 4 (`required`, `additionalProperties: false`) |
| Hugging Face Transformers – Prompt engineering | https://huggingface.co/docs/transformers/main/en/tasks/prompting | docs | Apache-2.0 | main (v5.20.1 stable), 2026-10-28 | 10 | 3 (separate instructions from data; few-shot via chat template) |
| Ollama API – Generate a chat message | https://docs.ollama.com/api/chat | docs | MIT | 2026-10-28 | 10 | 2 (native `/api/chat` shape, `format`, `tools`) |
| Ollama docs – macOS | https://docs.ollama.com/macos | docs | MIT (ollama/ollama) | 2026-10-28 (macOS 14+, M-series CPU+GPU, `~/.ollama`) | 11 | 1, HARDWARE |
| Ollama docs – Windows | https://docs.ollama.com/windows | docs | MIT | 2026-10-28 (content via search result; Win 10 22H2+, NVIDIA 551.61+, ROCm v7 / Vulkan, OllamaSetup.exe) | 11 | 1, HARDWARE |
| Ollama docs – Hardware support | https://docs.ollama.com/gpu | docs | MIT | 2026-10-28 (NVIDIA CC 5.0+, AMD ROCm v7, Metal, Vulkan) | 11 | 1, HARDWARE |
| Homebrew cask `ollama-app` | https://formulae.brew.sh/cask/ollama-app | registry | BSD-2 (Homebrew) | 0.40.12, macOS >= 14 | 10 | 1 |
| Homebrew formula `ollama` | https://formulae.brew.sh/formula/ollama | registry | MIT | 0.40.11, `brew services start ollama` | 9 | 1 |
| winget-pkgs – `Ollama.Ollama` manifests | https://github.com/microsoft/winget-pkgs/tree/master/manifests/o/Ollama/Ollama | registry | MIT | latest manifest 0.34.2 (lags 0.40.12) | 9 | 1 |
| llama.cpp – install pre-built (brew, winget) | https://github.com/ggml-org/llama.cpp/blob/master/docs/install.md | docs | MIT | 2026-10-28 | 11 | 1 |
| llama.cpp README (backends: Metal, CUDA, HIP, Vulkan) | https://github.com/ggml-org/llama.cpp/blob/master/README.md | repo | MIT | 2026-10-28 | 10 | HARDWARE |
| Python docs – venv (activation, ExecutionPolicy) | https://docs.python.org/3/library/venv.html | docs | PSF | 3.15 docs, 2026-10-28 | 11 | 1 |
| Homebrew formula `python@3.12` | https://formulae.brew.sh/formula/python@3.12 | registry | PSF | 3.12.16 | 9 | 1 |
| Ollama docs – Embeddings | https://docs.ollama.com/capabilities/embeddings | docs | MIT (ollama/ollama) | 2026-10-28 | 11 | 7 |
| Ollama API – Generate embeddings (/api/embed) | https://docs.ollama.com/api/embed | docs | MIT | 2026-10-28 | 10 | 7 |
| Ollama library – embeddinggemma | https://ollama.com/library/embeddinggemma | docs (model registry) | model licence not shown on page | 300m, 622 MB, 2K context, Ollama ≥ 0.11.10 | 8 | 7 |
| vLLM – Pooling models (/v1/embeddings) | https://docs.vllm.ai/en/latest/models/pooling_models/ | docs | Apache-2.0 | page dated 2026-10-22 | 10 | 7 |
| Lewis et al. – Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks | https://arxiv.org/abs/2005.11401 | paper | arXiv preprint | v4, 2021-04-12 (NeurIPS 2020) | 9 | 7 |
| sqlite-vec – Python | https://alexgarcia.xyz/sqlite-vec/python.html | docs | MIT / Apache-2.0 | 2026-10-28 | 10 | 7 |
| sqlite-vec – KNN queries | https://alexgarcia.xyz/sqlite-vec/features/knn.html | docs | MIT / Apache-2.0 | 2026-10-28 | 10 | 7 |
| sqlite-vec on PyPI | https://pypi.org/project/sqlite-vec/ | registry | MIT / Apache-2.0 | 0.1.9 (2026-03-31) | 9 | 7 (CI pin) |
| pgvector README | https://github.com/pgvector/pgvector | repo | see repo LICENSE (not checked) | v0.8.7, image tag 0.8.7-pg18 | 11 | 7 (CI job) |
| numpy on PyPI | https://pypi.org/project/numpy/ | registry | BSD-3-Clause and others | 2.5.4 (2026-10-10), Python ≥ 3.12 | 9 | 7 (pin) |
| JSON Schema reference – numeric types | https://json-schema.org/understanding-json-schema/reference/numeric | docs | open documentation (JSON Schema project) | 2026-10-28 | 12 | 8 |
| jsonschema on PyPI | https://pypi.org/project/jsonschema/ | registry | MIT | 4.26.0 (2026-01-07) | 10 | 8 (CI pin) |
| Python docs – sqlite3 | https://docs.python.org/3/library/sqlite3.html | docs | PSF-2.0 | Python 3.15.2 docs | 11 | 9, platform |
| Packer et al. – MemGPT: Towards LLMs as Operating Systems | https://arxiv.org/abs/2310.08560 | paper | arXiv preprint | v2, 2024-02-12 | 9 | 9 |
| MCP specification 2026-07-28 – overview + security principles | https://modelcontextprotocol.io/specification/2026-07-28 | spec | open specification (MCP project) | 2026-07-28 (current per the versioning page) | 11 | 10, 11 |
| MCP 2026-07-28 – Base protocol | https://modelcontextprotocol.io/specification/2026-07-28/basic | spec | open specification | 2026-07-28 | 11 | 10 |
| MCP 2026-07-28 – Versioning and compatibility | https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning | spec | open specification | 2026-07-28 | 12 | 10 |
| MCP – Versioning ("current protocol version is 2026-07-28") | https://modelcontextprotocol.io/docs/learn/versioning | docs | open specification | redirected to the 2026-07-28 page | 11 | 10 |
| MCP 2026-07-28 – Transports | https://modelcontextprotocol.io/specification/2026-07-28/basic/transports | spec | open specification | 2026-07-28 | 11 | 10 |
| MCP 2026-07-28 – stdio binding (spec repo source, via web_search) | https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/main/docs/specification/2026-07-28/basic/transports/stdio.mdx | spec | open specification | main branch | 10 | 10 |
| MCP 2026-07-28 – server/discover (spec repo source, via web_search) | https://raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/main/docs/specification/2026-07-28/server/discover.mdx | spec | open specification | main branch | 10 | 10 |
| MCP 2026-07-28 – Key changes (via web_search) | https://modelcontextprotocol.io/specification/2026-07-28/changelog | spec | open specification | 2026-07-28 | 9 | 10 |
| MCP 2025-11-25 – Lifecycle (legacy initialize) | https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle | spec | open specification | 2025-11-25 | 11 | 10 |
| MCP Python SDK on PyPI | https://pypi.org/project/mcp/ | registry | MIT | 2.3.0 (2026-10-02) | 10 | 10 (CI pin) |
| MCP Python SDK – Client API reference | https://py.sdk.modelcontextprotocol.io/api/mcp/client/client/ | docs | MIT | v2.3.0 | 10 | 10 |
| MCP Python SDK – MCPServer API reference | https://py.sdk.modelcontextprotocol.io/api/mcp/server/mcpserver/server/ | docs | MIT | v2.3.0 | 10 | 10 |
| OWASP GenAI – LLM01:2025 Prompt Injection | https://genai.owasp.org/llmrisk/llm01-prompt-injection/ | spec/standard | CC BY-SA 4.0 | 2025 edition | 11 | 11 |
| OWASP GenAI – LLM02:2025 Sensitive Information Disclosure | https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/ | spec/standard | CC BY-SA 4.0 | 2025 edition | 10 | 11 |
| Greshake et al. – Not what you've signed up for (indirect prompt injection) | https://arxiv.org/abs/2302.12173 | paper | arXiv preprint | v2, 2023-05-05 | 9 | 11 |

## Learning tools (facts from the shared catalog)

Facts, versions and URLs below are copied from `../../shared/LEARNING-TOOLS-CATALOG.md` (checked 2026-10-28 against official sites); exercises and installs per lesson: `LEARNING-TOOLS.md`.

| tool | url | licence (OSI) | version checked | used in lesson(s) |
|---|---|---|---|---|
| MCP Inspector | https://github.com/modelcontextprotocol/inspector | MIT + Apache-2.0 (yes) | 2.12.0 (use ≥ 2.12.0) | 10 |
| promptfoo | https://github.com/promptfoo/promptfoo/releases | MIT (yes) | 0.125.1 | 4, 5, 11 |
| promptfoo – Ollama provider | https://www.promptfoo.dev/docs/providers/ollama/ | MIT (yes) | 2026-10-28 | 4, 5, 11 |
| Langflow – Ollama bundle | https://docs.langflow.org/bundles-ollama | MIT (yes) | 1.13.0 | 6, 7 |
| AnythingLLM | https://github.com/Mintplex-Labs/anything-llm/releases | MIT (yes); optional paid Pro tier | v1.19.0 | 10 |
| Open WebUI – quick start | https://docs.openwebui.com/getting-started/quick-start/ | Open WebUI License (**no**) | v0.12.4 | 11 |
| Ollama download | https://ollama.com/download | MIT (yes) | v0.40.12 | 1, 2 |
| Orange Data Mining | https://github.com/biolab/orange3 | GPL-3.0-or-later (yes) | 3.40.0 | 7 |
| KNIME – local model via Ollama | https://docs.knime.com/ap/latest/ai/local-model-ollama | GPL-3.0 + KNIME permissions (yes) | 5.12 (LTS 5.8.4) | 2 |

## Removed in the 2026-10-28 review pass
- LangGraph quickstart (docs.langchain.com) – vendor docs; LangGraph stays only as a one-line `equivalents` entry in lesson 6 (F15).
- Ollama README at tag v0.13.5 (RAM rule) – the rule is no longer in the current README and not in the FAQ; HARDWARE.md now sizes by download size + `ollama ps` (F16).
- Raw `windows.mdx` copy of the Ollama Windows page – one URL per document (F16).

## Tooling versions used by CI (checked 2026-10-28)
| item | url | version pinned |
|---|---|---|
| requests | https://pypi.org/project/requests/ | 2.34.2 (2026-05-14) |
| actions/checkout | https://github.com/actions/checkout/releases | v7.0.1 |
| actions/setup-python | https://github.com/actions/setup-python/releases | v7.1.0 |
| Ollama (optional job) | https://github.com/ollama/ollama/releases | 0.40.12 |
| numpy | https://pypi.org/project/numpy/ | 2.5.4 (sandbox validated with 2.5.3) |
| jsonschema | https://pypi.org/project/jsonschema/ | 4.26.0 |
| sqlite-vec | https://pypi.org/project/sqlite-vec/ | 0.1.9 |
| mcp (official Python SDK) | https://pypi.org/project/mcp/ | 2.3.0 |
| pgvector service image | https://github.com/pgvector/pgvector | pgvector/pgvector:0.8.7-pg18 |

## L300 sources (added 2026-10-28; all retrieved with web_fetch / web_search that day)

| title | url | type | licence | version-or-date checked | score/12 | used in lesson(s) |
|---|---|---|---|---|---|---|
| promptfoo – Configuration guide | https://www.promptfoo.dev/docs/configuration/guide/ | docs | MIT (promptfoo repo) | updated 2026-10-26 | 12 | 12 |
| promptfoo – OpenAI provider (openai:chat, apiBaseUrl, apiKeyRequired) | https://www.promptfoo.dev/docs/providers/openai/ | docs | MIT | updated 2026-10-25 | 11 | 12 |
| promptfoo – CI/CD integration | https://www.promptfoo.dev/docs/integrations/ci-cd/ | docs | MIT | 2026-10-28 (search result text) | 10 | 12 |
| promptfoo issue #741 – exit code 100 on failed tests | https://github.com/promptfoo/promptfoo/issues/741 | repo (issue) | MIT | closed by #751 (PROMPTFOO_FAILED_TEST_EXIT_CODE) | 9 | 12 |
| promptfoo – red team configuration (docs source) | https://github.com/promptfoo/promptfoo/blob/main/site/docs/red-team/configuration.md | repo (docs) | MIT | main, 2026-10-28 (promptfoo.dev page withheld by the fetch tool) | 10 | 16 |
| Zheng et al. – Judging LLM-as-a-Judge (MT-Bench) | https://arxiv.org/abs/2306.05685 | paper | arXiv | v4, 2023-12-24 | 9 | 12 |
| OpenTelemetry semantic-conventions-genai – GenAI spans | https://raw.githubusercontent.com/open-telemetry/semantic-conventions-genai/main/docs/gen-ai/gen-ai-spans.md | spec | Apache-2.0 | main, status Development | 12 | 13, 14 |
| OpenTelemetry semantic-conventions-genai – agent spans | https://raw.githubusercontent.com/open-telemetry/semantic-conventions-genai/main/docs/gen-ai/gen-ai-agent-spans.md | spec | Apache-2.0 | main, status Development | 11 | 13 |
| OpenTelemetry semantic-conventions-genai repository | https://github.com/open-telemetry/semantic-conventions-genai | repo | Apache-2.0 | main (2026-10-28) | 10 | 13 |
| opentelemetry.io – GenAI conventions "moved" notice | https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/ | spec (status) | OpenTelemetry docs | semconv 1.44.0 site | 10 | 13 |
| PyPI – opentelemetry-sdk | https://pypi.org/project/opentelemetry-sdk/ | registry | Apache-2.0 | 1.45.1 (2026-10-06) | 10 | 13 |
| urllib3 – Retry and Timeout reference | https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html | docs | MIT | 2.8.0 | 12 | 14 |
| RFC 9110 – HTTP Semantics | https://www.rfc-editor.org/rfc/rfc9110.html | spec | IETF Trust (BSD for code) | June 2022, Internet Standard | 11 | 14 |
| IETF draft – The Idempotency-Key HTTP Header Field | https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/ | spec (draft) | IETF Trust | -08, 2026-10-22 (active WG draft) | 11 | 15 |
| MCP blog – Tool annotations as risk vocabulary | https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/ | article (background) | MCP project | 2026-03-16 | 9 | 15 |
| OWASP Cheat Sheet – LLM Prompt Injection Prevention | https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html | docs | CC BY-SA 4.0 | 2026-10-28 | 12 | 16 |
| Debenedetti et al. – Defeating Prompt Injections by Design (CaMeL) | https://arxiv.org/abs/2503.18813 | paper | arXiv | v2, 2025-06-24 | 10 | 16 |
| Debenedetti et al. – AgentDojo | https://arxiv.org/abs/2406.13352 | paper | arXiv | v3, 2024-11-24 | 10 | 16 |
| garak – LLM vulnerability scanner (README: --target_type/--target_name, --spec, JSONL report) | https://github.com/NVIDIA/garak | repo | Apache-2.0 | 0.17.1 (GitHub releases ≈2026-10-21; piwheels showed 2026-10-16) | 10 | 16 (learningTools) |
| garak – releases (0.16.0 unified --spec syntax; 0.17.0 Ollama options/auth; 0.17.1 Python 3.14) | https://github.com/NVIDIA/garak/releases | repo (releases) | Apache-2.0 | v0.17.1, fetched 2026-10-28 | 10 | 16 |
| garak reference – generators.ollama (OllamaGenerator / OllamaGeneratorChat; default host 127.0.0.1:11434) | https://reference.garak.ai/en/latest/garak.generators.ollama.html | docs | Apache-2.0 | latest, 2026-10-28 | 10 | 16 |
| garak FAQ (detectors local or via API; ~9 GB of dependencies; report location) | https://github.com/NVIDIA/garak/blob/main/FAQ.md | docs | Apache-2.0 | main, 2026-10-28 | 9 | 16 |
| promptfoo – Data handling and privacy (red team: what leaves the machine, remote-only plugins, PROMPTFOO_DISABLE_REMOTE_GENERATION) | https://www.promptfoo.dev/docs/red-team/troubleshooting/data-handling/ | docs | MIT | updated 2026-10-22, fetched 2026-10-28 | 12 | 16 |
| promptfoo – Configuring inference (hosted by default; local Ollama providers; usage limits still apply) | https://www.promptfoo.dev/docs/red-team/troubleshooting/inference-limit/ | docs | MIT | updated 2026-10-26, fetched 2026-10-28 | 11 | 16 |
| promptfoo – Telemetry (PROMPTFOO_DISABLE_TELEMETRY=1, PROMPTFOO_DISABLE_UPDATE=1) | https://www.promptfoo.dev/docs/configuration/telemetry/ | docs | MIT | updated 2026-10-26, fetched 2026-10-28 | 11 | 12, 16 |
| promptfoo – Excessive Agency plugin (docs source; id excessive-agency) | https://github.com/promptfoo/promptfoo/blob/main/site/docs/red-team/plugins/excessive-agency.md | repo (docs) | MIT | main, 2026-10-28 | 9 | 16 |
| promptfoo – Basic strategy (docs source; basic + base64 example) | https://github.com/promptfoo/promptfoo/blob/main/site/docs/red-team/strategies/basic.md | repo (docs) | MIT | main, 2026-10-28 | 9 | 16 |
| PyPI – opentelemetry-exporter-otlp-proto-http (OTLPSpanExporter) | https://pypi.org/project/opentelemetry-exporter-otlp-proto-http/ | registry | Apache-2.0 | 1.45.1 (2026-10-06) | 10 | 13 (Jaeger exercise) |

Also used again in L300 (rows above): MCP 2026-07-28 Tools (lessons 14, 15), OWASP LLM01:2025 (16), OWASP LLM06:2025 (15), Greshake et al. (16), Python sqlite3 docs (15).

| tool | url | licence (OSI) | version checked | used in lesson(s) |
|---|---|---|---|---|
| promptfoo (eval + red team) | https://github.com/promptfoo/promptfoo/releases | MIT (yes) | 0.125.1 | 12, 16 |
| Orange Data Mining | https://github.com/biolab/orange3 | GPL-3.0-or-later (yes) | 3.40.0 | 13 |
| Open WebUI – quick start | https://docs.openwebui.com/getting-started/quick-start/ | Open WebUI License (**no**) | v0.12.4 | 15 |
| Jaeger | https://www.jaegertracing.io/docs/latest/getting-started/ | Apache-2.0 (yes) | v2.22.0 | 13 |
| Toxiproxy | https://github.com/Shopify/toxiproxy | MIT (yes) | v2.13.0 | 14 |
| garak (NVIDIA) | https://github.com/NVIDIA/garak/releases | Apache-2.0 (yes) | v0.17.1 | 16 |

| item (CI, L300) | url | version pinned |
|---|---|---|
| opentelemetry-sdk | https://pypi.org/project/opentelemetry-sdk/ | 1.45.1 |
| opentelemetry-exporter-otlp-proto-http (installed by the equivalents job; used only by the manual --otlp run) | https://pypi.org/project/opentelemetry-exporter-otlp-proto-http/ | 1.45.1 |
| promptfoo (npx) | https://github.com/promptfoo/promptfoo/releases | 0.125.1 |
| actions/setup-node | https://www.promptfoo.dev/docs/integrations/ci-cd/ | SHA 48b55a011bda9f5d6aeb4c2d9c7362e8dae4041e (# v6), copied from promptfoo's CI/CD example – not checked against the action's release page |

## L400 additions (retrieved 2026-10-28)

| title | url | type | licence | version-or-date checked | score/12 | used in lesson(s) |
|---|---|---|---|---|---|---|
| Cemri et al. – Why Do Multi-Agent LLM Systems Fail? | https://arxiv.org/abs/2503.13657 | paper | arXiv | v3, 2025-10-26 | 12 | 17 |
| Yao et al. – ReAct | https://arxiv.org/abs/2210.03629 | paper | arXiv | v3, 2023-03-10 | 11 | 17 |
| Xu et al. – ReWOO: Decoupling Reasoning from Observations | https://arxiv.org/abs/2305.18323 | paper | arXiv | v1, 2023-05-23 | 11 | 17 |
| Wu et al. – AutoGen: Multi-Agent Conversation | https://arxiv.org/abs/2308.08155 | paper | arXiv | v2, 2023-10-03 | 9 | 17 |
| Shen et al. – HuggingGPT | https://arxiv.org/abs/2303.17580 | paper | arXiv | v4, 2023-12-03 | 9 | 17 |
| Temporal docs – Workflows (Event History, replay, determinism) | https://docs.temporal.io/workflows | docs | MIT (temporalio/documentation) | 2026-10-28 | 12 | 18 |
| PyPI – temporalio (Python SDK: signals, wait_condition, WorkflowEnvironment) | https://pypi.org/project/temporalio/ | registry | MIT (repo; not re-fetched) | 1.34.0 | 11 | 18 |
| Temporal CLI (dev server + Web UI) | https://github.com/temporalio/cli | repo | MIT | CLI v1.9.1 (catalogue) | 10 | 18 (learningTools) |
| SQLite – Atomic Commit In SQLite | https://www.sqlite.org/atomiccommit.html | docs | public domain | 2026-10-28 | 11 | 18 |
| Chen, Zaharia, Zou – FrugalGPT | https://arxiv.org/abs/2305.05176 | paper | arXiv | v1, 2023-05-09 | 11 | 19 |
| Ong et al. – RouteLLM | https://arxiv.org/abs/2406.18665 | paper | arXiv | v4, 2025-02-23 | 11 | 19 |
| llama.cpp server README (cache-prompt, parallel slots, continuous batching, ctx-size) | https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md | repo (docs) | MIT | master, 2026-10-28 | 11 | 19 |
| vLLM – Automatic Prefix Caching | https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html | docs | Apache-2.0 | 2026-10-13 page date | 12 | 19 |
| Ollama FAQ (context 4096, NUM_PARALLEL x context, KV f16, ollama ps) | https://docs.ollama.com/faq | docs | MIT | 2026-10-28 | 12 | 17, 19 |
| Ollama API – /api/chat (prompt_eval_cached_count, eval_duration) | https://docs.ollama.com/api/chat | docs | MIT | 2026-10-28 | 11 | 19 |
| Ollama API – /api/tags (name, digest) | https://docs.ollama.com/api/tags | docs | MIT | 2026-10-28 | 11 | 21 |
| Ollama – Hardware support (NVIDIA cc 5.0+, driver 550+; Metal; Vulkan) | https://docs.ollama.com/gpu | docs | MIT | 2026-10-28 | 10 | 19 |
| Apple – Mac mini technical specifications (M6, M5 Pro) | https://www.apple.com/mac-mini/specs/ | vendor spec (hardware facts only) | – | 2026-10-28 | 10 | 19 |
| Qwen2.5-1.5B / 7B / 14B-Instruct config.json | https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/blob/main/config.json | model repo | Apache-2.0 | main (1.5B: 775b11a, 7B: a306ca6, 14B: 76ca6ba) | 11 | 19 |
| Beurer-Kellner et al. – Design Patterns for Securing LLM Agents against Prompt Injections | https://arxiv.org/abs/2506.08837 | paper | arXiv | v3, 2025-06-27 | 12 | 20 |
| JSON Schema Draft 2020-12 | https://json-schema.org/draft/2020-12 | spec | BSD/AFL (json-schema.org) | published 2022-06-16 | 11 | 20 |
| NIST AI 600-1 – Generative AI Profile | https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence | standard | US gov | 2024-07-26 (updated 2026-04-08) | 11 | 21 |
| NIST/SEMATECH e-Handbook – Chi-Square Goodness-of-Fit Test | https://www.itl.nist.gov/div898/handbook/eda/section3/eda35f.htm | docs | US gov | 2026-10-28 | 12 | 21 |
| Nygard – Documenting Architecture Decisions | https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions | primary (format origin) | public domain dedication | 2011-11-15 | 11 | 17-22 (ADRs) |
| Regulation (EU) 2016/679 (GDPR) – Art. 5(1)(e), recital 39 | https://eur-lex.europa.eu/eli/reg/2016/679/oj | law | EU | OJ L 119, 2016-05-04 | 9 | 21 |
| Google SRE book – Managing Incidents | https://sre.google/sre-book/managing-incidents/ | book chapter | CC BY-NC-ND 4.0 | 2026-10-28 | 11 | 22 |
| Mermaid – Flowchart syntax | https://mermaid.js.org/syntax/flowchart.html | docs | MIT | 2026-10-28 (redirects to mermaid.ai/open-source) | 9 | 22 |

Also used again in L400 (rows above): IETF Idempotency-Key draft (18), MCP 2026-07-28 Tools (22), OWASP LLM01/LLM06:2025 (20, 21), CaMeL (20), SRE Workbook alerting on SLOs (22, via application-architecture), Python sqlite3 docs (18).

| tool (L400) | url | licence (OSI) | version checked | used in lesson(s) |
|---|---|---|---|---|
| Langflow | https://github.com/langflow-ai/langflow/releases | MIT (yes) | 1.13.0 | 17 |
| Temporal CLI dev server + Web UI | https://github.com/temporalio/cli | MIT (yes) | CLI v1.9.1 | 18 |
| Toxiproxy | https://github.com/Shopify/toxiproxy | MIT (yes) | v2.13.0 | 18 |
| Ollama (supporting runtime) | https://github.com/ollama/ollama/releases | MIT (yes) | v0.40.12 | 19 |
| promptfoo | https://github.com/promptfoo/promptfoo/releases | MIT (yes) | 0.125.1 | 20, 21 |
| garak (NVIDIA) | https://github.com/NVIDIA/garak/releases | Apache-2.0 (yes) | v0.17.1 | 21 |
| MCP Inspector | https://github.com/modelcontextprotocol/inspector | MIT + Apache-2.0 (yes) | 2.12.0 | 22 |
| Orange Data Mining | https://github.com/biolab/orange3 | GPL-3.0-or-later (yes) | 3.40.0 | 22 |

| item (CI, L400) | url | version pinned |
|---|---|---|
| temporalio (Temporal Python SDK; CI temporal job only) | https://pypi.org/project/temporalio/ | 1.34.0 |

## L500 additions (retrieved 2026-10-30; research trail in `research/L500-evidence.md`)
Primary papers, standards, statutes and a tribunal decision for the theory, ethics and reading lessons (23-27) and the assessment pack. Papers on arXiv are summarised, never reproduced. Paywalled originals (McNemar, Hart et al.) are cited for priority; the lessons' proofs are self-contained.

| title | url | type | licence | version-or-date checked | score/12 | used in lesson(s) |
|---|---|---|---|---|---|---|
| Vaswani et al. – Attention Is All You Need (abstract + HTML full text) | https://arxiv.org/abs/1706.03762 · https://arxiv.org/html/1706.03762v7 | paper | arXiv perpetual non-exclusive licence (read there; summarised only) | v7, 2 Aug 2023 | 12 | 23, 27, qbank |
| Yao et al. – ReAct: Synergizing Reasoning and Acting in Language Models (abstract + PDF) | https://arxiv.org/abs/2210.03629 · https://arxiv.org/pdf/2210.03629v3 | paper (ICLR 2023) | arXiv (summarised only) | v3, 10 Mar 2023 | 12 | 25, 27, qbank |
| Holtzman et al. – The Curious Case of Neural Text Degeneration | https://arxiv.org/abs/1904.09751 | paper (ICLR 2020) | arXiv | v2, 14 Feb 2020 | 10 | 23 |
| Jurafsky & Martin – Speech and Language Processing, ch. 3 N-gram Language Models | https://web.stanford.edu/~jurafsky/slp3/3.pdf | textbook chapter (free draft) | all rights reserved; free to read | draft of 19 Aug 2026 | 11 | 23, 24 |
| NIST/SEMATECH e-Handbook §7.2.4.1 – Confidence intervals for proportions | https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm | standard reference (US gov.) | public domain (US government work) | page as retrieved 2026-10-30 | 12 | 24, assessment |
| McNemar (1947) – Note on the sampling error of the difference between correlated proportions, Psychometrika 12(2) | https://doi.org/10.1007/BF02295996 | paper | publisher copyright (landing page only) | 1947 | 9 | 24 |
| Sutton & Barto – Reinforcement Learning: An Introduction, 2nd ed. | http://incompleteideas.net/book/the-book-2nd.html | textbook (free PDF from the authors) | authors' free online edition | 2018 | 11 | 25 |
| Hart, Nilsson & Raphael (1968) – A Formal Basis for the Heuristic Determination of Minimum Cost Paths | https://ieeexplore.ieee.org/document/4082128 | paper | publisher copyright (abstract page via search) | 1968 | 9 | 25 |
| Rice (1953) – Classes of recursively enumerable sets and their decision problems, Trans. AMS 74 | https://www.ams.org/journals/tran/1953-074-02/S0002-9947-1953-0053041-6/home.html | paper | AMS (free PDF) | 1953 | 10 | 25 |
| ACM Code of Ethics and Professional Conduct | https://www.acm.org/code-of-ethics | professional code | may be published unchanged with copyright notice | adopted 22 Jun 2018 | 12 | 26, assessment |
| NIST AI 100-1 – AI Risk Management Framework (AI RMF 1.0) | https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf | standard / framework (US gov.) | public domain | Jan 2023 (page says 1.0 is under revision) | 12 | 26 |
| NIST – AI Risk Management Framework page | https://www.nist.gov/itl/ai-risk-management-framework | official page | public domain | retrieved 2026-10-30 | 10 | 26 |
| Regulation (EU) 2024/1689 – Artificial Intelligence Act (EUR-Lex) | https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng | statute | EU legal texts: free reuse | OJ 12.7.2024; consolidated version 27/07/2026 listed | 11 | 26, assessment |
| Regulation (EU) 2026/1744 – Digital Omnibus on AI (Official Journal PDF) | https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202601744 | statute (amending) | EU legal texts | 8 Jul 2026; OJ 24 Jul 2026 | 10 | 26 |
| European Parliament Legislative Train – Digital Omnibus on AI | https://www.europarl.europa.eu/legislative-train/spotlight-JD26/file-digital-omnibus-on-ai | official procedure summary | EP | updated 20/09/2026 | 10 | 26 |
| Regulation (EU) 2016/679 (GDPR) Art. 22 – as adopted (legislation.gov.uk mirror of the OJ text) | https://www.legislation.gov.uk/eur/2016/679/article/22/adopted | statute | Open Government Licence (mirror) / EU reuse | as adopted 27 Apr 2016 | 10 | 26 |
| Moffatt v. Air Canada, 2024 BCCRT 149 – reasons for decision | https://www.thesedonaconference.org/sites/default/files/meeting_paper/Moffet%20v%20AirCanada.pdf | tribunal decision (copy) | public court record | decided 14 Feb 2024 | 10 | 26, qbank, final |
| Parasuraman & Riley (1997) – Humans and Automation: Use, Misuse, Disuse, Abuse, Human Factors 39(2) | https://web.mit.edu/16.459/www/parasuraman.pdf | paper | publisher copyright (course-hosted copy) | 1997 | 9 | 26 |
| ABET – Criteria for Accrediting Computing Programs, 2025–2026 | https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-computing-programs-2025-2026/ | accreditation criteria | ABET | 2025–2026 cycle | 10 | assessment (syllabus) |
| ABET – Criteria for Accrediting Engineering Programs, 2025–2026 | https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-engineering-programs-2025-2026/ | accreditation criteria | ABET | 2025–2026 cycle | 10 | assessment (syllabus) |
| ACM/IEEE-CS/AAAI CS2023 – Knowledge Areas | https://csed.acm.org/knowledge-areas/ | curriculum guidelines | ACM/IEEE-CS/AAAI | endorsed Jan–Feb 2024 | 10 | assessment (syllabus) |

