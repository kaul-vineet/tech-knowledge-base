# AI Agents – concepts primer

Read once before lesson 1; each lesson then has a short concept note in `content/concepts/`.

## What agents are for
An "agent" here is a program that lets a language model decide which of *your* functions to call, runs them, and feeds the results back until the task is done. The model proposes; your code executes and enforces the rules. Typical uses: data extraction into validated JSON (lesson 4), read-only internal lookups ("what is the status of X?"), coding helpers that run tests, and private assistants on a local open-weight model served by Ollama or llama.cpp.

## One mental model
A language model is a **stateless text function**: messages in, one message out. Memory, tools, loops and safety are ordinary code around it.

```
            ┌─────────────── your program (deterministic) ───────────────┐
 task ──►   │ build messages ─► POST /v1/chat/completions ─► parse reply │
            │      ▲                                          │          │
            │      │ append tool result      tool_calls? ─yes─┤          │
            │   run allowed tool ◄── validate / approve ◄─────┘          │
            │                                no tool_calls ─► answer ───│──► user
            │   budget: stop after max_steps                             │
            └────────────────────────────────────────────────────────────┘
                     model server: Ollama / llama.cpp / vLLM / fake
```

## Concept map (proposed – see KNOWN-GAPS)
- **L100 – run it:** HTTP call · prompt roles, examples, delimiters · validated JSON · one tool round trip · a bounded loop.
- **L200 – build it (built):** retrieval with cited chunks · several tools with JSON Schema checks · state, summaries and SQLite memory · an MCP server and client · guardrails.
- **L300 – harden it (built):** golden-set regression gate · GenAI tracing · timeouts, retries, budgets, fallbacks · approval queue with idempotency keys · prompt-injection red-team suite.
- **L400 – design it (built):** agent topologies · durable workflows · model routing and sizing · code decides, model at the edge · governance · triage capstone.
- *Local agents, L200:* the model drafts a tool schema and proposes risk labels; code validates and the policy table decides.
- *Local agents, L300 (built):* the model proposes attack paraphrases; the suite and the policy layer decide; approvals, keys and budgets stay in code.
- *Local agents, L400 (built):* the model proposes triage, explains and drafts records; code decides and checks every number.

## Glossary
| term | meaning |
|---|---|
| token | Chunk of text the model reads and writes; limits and usage are counted in tokens. |
| inference server | Loads a model and serves it over HTTP (Ollama, llama.cpp `llama-server`, vLLM). |
| chat-completions API | `POST /v1/chat/completions` JSON format; it originated with OpenAI's API and is implemented by Ollama, llama.cpp and vLLM. |
| chat template | Server-side rule that turns the message list into one token sequence. |
| temperature | Sampling knob; lower = more repeatable. |
| structured output | Reply that must match a schema (usually JSON Schema). |
| tool call | Model's request to run a named function with JSON arguments; your code runs it. |
| agent loop | Model → tool calls → results → model, until a final answer or a budget stop. |
| MCP | Model Context Protocol: JSON-RPC protocol for listing (`tools/list`) and calling (`tools/call`) tools. |
| excessive agency | OWASP risk: an LLM system has too much functionality, permission or autonomy. |

## Common misconceptions
1. **"The model remembers the conversation."** The client resends the history on every call (lesson 2).
2. **"The model runs my tools."** It only asks; your code decides whether to run them – MCP says a human SHOULD be able to deny tool invocations (lesson 5).
3. **"Schema-valid JSON is correct data."** It can still hold wrong values; validate in code (lesson 4).

## Sources
- Ollama – /v1 chat-completions compatibility: https://docs.ollama.com/api/openai-compatibility
- vLLM – Online serving: https://docs.vllm.ai/en/latest/serving/online_serving/
- Model Context Protocol – Tools: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
- ReAct (Yao et al.): https://arxiv.org/abs/2210.03629
- OWASP LLM06:2025 Excessive Agency: https://genai.owasp.org/llmrisk/llm062025-excessive-agency/
