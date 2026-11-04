# L200 research evidence – AI Agents

Method: SPEC "Research method" (questions → candidates → screen → score ≥ 8/12 → cross-check with ≥ 2 sources, one official). Retrieval date for every URL: 2026-10-28 (web_fetch / web_search). Score order: implementable / current / authoritative / open / transferable / right depth. Worked-example numbers in the concept notes come from `research/L200_concept_examples.py` (output: `L200_concept_examples.out.txt`, re-checked in CI).

---
## Lesson 7 – Retrieval-augmented answers
**Questions**
1. Which embeddings endpoint is portable across Ollama, llama.cpp and vLLM, and what does it return?
2. Which small open embedding model can the Mac mini / Windows PC run, and how is it pulled?
3. How do sqlite-vec and pgvector express cosine top-k, and which versions are current?

| source | decision | score | reason |
|---|---|---|---|
| docs.ollama.com/capabilities/embeddings | kept | 2/2/2/2/1/2 = 11 | `/api/embed` with string or array input; "/api/embed returns L2-normalized vectors"; use cosine; same model for indexing and querying |
| docs.ollama.com/api/embed | kept | 2/2/2/2/1/1 = 10 | response shape `{"model", "embeddings": [[...]]}`, `truncate`, `dimensions` |
| docs.ollama.com/api/openai-compatibility | kept | 2/2/2/2/2/1 = 11 | `/v1/embeddings` supported fields: model, input (string / array), encoding format, dimensions |
| llama.cpp tools/server/README.md | kept | 2/2/2/2/2/1 = 11 | "OpenAI API compatible chat completions, responses, and embeddings routes"; `--embedding`, `--pooling`, `--embd-normalize` (default 2 = euclidean), `--embd-gemma-default` |
| docs.vllm.ai/en/latest/models/pooling_models/ | kept | 2/2/2/2/1/1 = 10 | OpenAI-compatible Embeddings API (/v1/embeddings) for the embed task; `--runner pooling` auto-detected |
| ollama.com/library/embeddinggemma | kept | 2/2/1/1/1/1 = 8 | 300M params, 622 MB, 2K context, requires Ollama ≥ 0.11.10, `ollama pull embeddinggemma` |
| arxiv.org/abs/2005.11401 (Lewis et al.) | kept (concept) | 1/1/2/2/2/1 = 9 | defines RAG: parametric + non-parametric (dense vector index) memory |
| alexgarcia.xyz/sqlite-vec (python, knn) | kept | 2/2/2/2/1/1 = 10 | `sqlite_vec.load(db)`, numpy float32 arrays bind directly, `vec0(... distance_metric=cosine)`, `MATCH ? AND k = n`; macOS system Python cannot load extensions |
| pypi.org/project/sqlite-vec | kept (version) | 2/2/1/2/1/1 = 9 | 0.1.9 (2026-03-31), wheels for macOS arm64 and Windows x86-64 |
| github.com/pgvector/pgvector | kept | 2/2/2/2/2/1 = 11 | v0.8.7; `<=>` cosine distance; `CREATE EXTENSION vector`; Docker tag `0.8.7-pg18` |
| pypi.org/project/numpy | kept (version) | 2/2/1/2/1/1 = 9 | 2.5.4 latest (2026-10-10), requires Python ≥ 3.12 |

**Key facts** (cross-checked)
- `/v1/embeddings` exists on Ollama (openai-compatibility page), llama.cpp (server README features) and vLLM (pooling models page) → the lab uses it; Ollama's native `/api/embed` is shown as the alternative and the fake server serves both shapes.
- Cosine similarity for semantic search and "same model for indexing and querying" – Ollama embeddings page; pgvector README offers `<=>` cosine distance and `1 - (a <=> b)` as similarity.
- sqlite-vec cosine KNN: `distance_metric=cosine` in the vec0 definition (sqlite-vec KNN docs).

## Lesson 8 – Agents with several tools
**Questions**
1. Which JSON Schema keywords are needed for tool arguments and how do integer/boolean edge cases behave?
2. How should argument errors be reported back to the model?
3. Which full validator should the small one be checked against?

| source | decision | score | reason |
|---|---|---|---|
| json-schema.org reference – numeric | kept | 2/2/2/2/2/2 = 12 | `minimum`/`maximum`; "Numbers with a zero fractional part are considered integers" (1.0 is an integer) |
| json-schema.org reference – object (L100) | kept | 2/2/2/2/2/1 = 11 | `required`, `additionalProperties: false` |
| MCP 2026-07-28 – Tools | kept | 2/2/2/2/2/1 = 11 | tool execution errors (incl. input validation) go in the result with `isError: true` so models can self-correct; protocol errors for unknown tools |
| pypi.org/project/jsonschema | kept | 2/2/2/2/1/1 = 10 | 4.26.0 (2026-01-07); full Draft 2020-12 support |
| vLLM tool calling, Ollama tool calling (L100) | kept (supporting) | 11 / 11 | `tools[].function.parameters` is JSON Schema; arguments arrive as a JSON string |

**Key facts**: integer accepts 1.0 (JSON Schema numeric page); booleans are not numbers in JSON Schema – python-jsonschema treats `True` as non-integer, so `schema_check.py` excludes Python bools; the agreement is asserted in `test_jsonschema_equivalent.py` (pending-ci).

## Lesson 9 – State and memory
**Questions**
1. What is the default context window of a local server and how is it changed on each OS?
2. How should token use be measured?
3. How is persistent memory stored safely?

| source | decision | score | reason |
|---|---|---|---|
| docs.ollama.com/faq | kept | 2/2/2/2/1/1 = 10 | default context 4096 tokens; `OLLAMA_CONTEXT_LENGTH`; `num_ctx` option; RAM scales with `OLLAMA_NUM_PARALLEL × OLLAMA_CONTEXT_LENGTH`; env vars via launchctl (macOS) / user environment variables (Windows) |
| docs.ollama.com/api/openai-compatibility | kept | 11 | the OpenAI API has no way to set context size; use a Modelfile with `PARAMETER num_ctx` |
| llama.cpp server README | kept | 11 | `-c, --ctx-size` (0 = from model), `--context-shift` |
| docs.python.org/3/library/sqlite3.html | kept | 2/2/2/2/2/1 = 11 | "Always use placeholders instead of string formatting ... to avoid SQL injection"; connection context manager commits |
| arxiv.org/abs/2310.08560 (MemGPT) | kept (concept) | 1/1/2/2/2/1 = 9 | virtual context management: memory tiers moved in/out of the limited window |

**Key facts**: token counts in the lab are word counts (fake server counts words; `usage.prompt_tokens` from lesson 2 is the ground truth for real models) – stated in the note and KNOWN-GAPS.

## Lesson 10 – MCP server and client
**Questions**
1. What is the current MCP protocol version, and does it still use `initialize`?
2. What exactly must a stdio server read/write, and how do clients detect older servers?
3. What is the current official Python SDK API for stdio servers and clients?

| source | decision | score | reason |
|---|---|---|---|
| modelcontextprotocol.io/specification/2026-07-28/basic/versioning | kept | 2/2/2/2/2/2 = 12 | "There is no negotiation handshake"; per-request version; `UnsupportedProtocolVersionError` -32022 example; dual-era rules; compatibility matrix |
| modelcontextprotocol.io/docs/learn/versioning (redirected to 2026-07-28) | kept | 11 | "The current protocol version is 2026-07-28" |
| modelcontextprotocol.io/specification/2026-07-28/basic | kept | 2/2/2/2/2/1 = 11 | required `_meta` keys (protocolVersion, clientCapabilities required; clientInfo optional); missing → -32602; `resultType` required; error code ranges |
| modelcontextprotocol.io/specification/2026-07-28/basic/transports | kept | 11 | stdio = newline-delimited messages over a client-launched subprocess; UTF-8; servers do not initiate requests |
| stdio binding + server/discover pages (2026-07-28) – text via web_search results of the spec repo (raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/main/docs/specification/2026-07-28/basic/transports/stdio.mdx and .../server/discover.mdx) | kept | 10 | no embedded newlines; stdout only MCP messages; stderr for logs; shutdown = close stdin; probe with server/discover, any non-modern error → legacy; DiscoverResult fields |
| modelcontextprotocol.io/specification/2026-07-28/server/tools | kept | 12 | tools/list and tools/call shapes, `ttlMs`/`cacheScope`, deterministic order, isError vs protocol errors, security considerations |
| modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle | kept | 11 | legacy `initialize` request/response and `notifications/initialized` |
| changelog + blog for 2026-07-28 (web_search result text) | kept (supporting) | 9 | "remove the initialize/notifications/initialized handshake"; `server/discover` MUST be implemented |
| pypi.org/project/mcp | kept | 2/2/2/2/1/1 = 10 | mcp 2.3.0 (2026-10-02), MIT, `from mcp.server import MCPServer`, `from mcp import Client` |
| py.sdk.modelcontextprotocol.io API reference (client, MCPServer) | kept | 2/2/2/2/1/1 = 10 | `Client(StdioServerParameters(...), mode="auto")` probes server/discover then falls back; `MCPServer.run(transport="stdio")` default |
| llama.cpp server README – MCP servers | kept (equivalent) | 10 | `--mcp-servers-config`, stdio only, tools exposed as `<server>_<tool>` |
| Third-party tutorials (milos-mitrovic.online, mcpstepbystep.com, mcpbundles.com) | dropped | – | not official; used only to locate the official API pages |

**Key facts** (cross-checked): handshake removal – versioning page + changelog + blog; stdio framing – transports overview + stdio binding; SDK era fallback – SDK API reference (`mode="auto"`) + spec stdio backward-compatibility section.

## Lesson 11 – Guardrails basics
**Questions**
1. What does indirect prompt injection look like and which mitigations do standards list?
2. How should risky tools be gated?
3. How are secrets kept out of outputs?

| source | decision | score | reason |
|---|---|---|---|
| genai.owasp.org LLM01:2025 Prompt Injection | kept | 2/2/2/2/2/1 = 11 | direct vs indirect injection; "unclear if there are fool-proof methods of prevention"; mitigations: constrain behaviour, validate output formats with deterministic code, least privilege, human approval for high-risk actions, segregate external content |
| genai.owasp.org LLM02:2025 Sensitive Information Disclosure | kept | 2/2/2/2/1/1 = 10 | system-prompt restrictions may be bypassed by injection; redaction via pattern matching; least privilege |
| genai.owasp.org LLM06:2025 Excessive Agency (L100) | kept | 11 | minimise functionality, permissions and autonomy |
| arxiv.org/abs/2302.12173 (Greshake et al.) | kept (concept) | 1/1/2/2/2/1 = 9 | indirect prompt injection via data likely to be retrieved; retrieved prompts "can act as arbitrary code execution" |
| MCP 2026-07-28 – Tools + overview (security principles) | kept | 11 | human in the loop SHOULD be able to deny; servers MUST validate inputs, rate limit, sanitize outputs; hosts must obtain consent before invoking tools |
| llama.cpp server README (`--tools` warnings) | kept (supporting) | 10 | built-in tools "do not enable in untrusted environments"; CORS limited to localhost when enabled |

**Key facts**: the build task (per-session rate limit) implements MCP's "Rate limit tool invocations"; delimiters alone are not a control – the fake model obeys injected text inside `<untrusted_data>` by rule, mirroring OWASP's "no fool-proof prevention" (real-model behaviour not measured).

## Platform facts (Mac mini + Windows)
- `ollama pull embeddinggemma` is identical on both; the Windows check uses `Invoke-RestMethod` or `curl.exe` (curl.exe "should be available in the base OS" – llama.cpp server README).
- Context window: macOS app → `launchctl setenv OLLAMA_CONTEXT_LENGTH ...` then restart; Windows → user environment variable, quit and restart Ollama (Ollama FAQ).
- sqlite-vec wheels exist for macOS 11+ arm64 and Windows x86-64 (PyPI); macOS system Python cannot load SQLite extensions (sqlite-vec docs; Python sqlite3 docs: extension loading is not built by default on some platforms, notably macOS).
- numpy 2.5.4 needs Python ≥ 3.12 (PyPI) – lesson 1's venv already uses 3.12.
