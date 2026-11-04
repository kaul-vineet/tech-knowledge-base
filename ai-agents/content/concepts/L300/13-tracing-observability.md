**Concept: tracing an agent – a span for every model call and tool call**

## Why it matters
"The agent is slow" is a symptom, not a diagnosis. An agent run is a chain of model calls and tool calls; any one of them can be the slow, failing or expensive part. A single log line with the total time cannot say which. Everyone blames the model, someone buys a bigger GPU, and the real culprit – a tool that loads an index on first use – stays hidden.

## Mental model
A trace is an itemised receipt instead of a total. Each line (span) has a name, a start, a duration, a parent and tags (attributes). Summing the lines by name shows where the time and tokens went.

```
invoke_agent support-agent ─────────────────────────────── 100 %
 ├ chat fake-model ▏  ├ execute_tool calculator ▏
 ├ chat fake-model ▏  ├ execute_tool get_weather ▏
 ├ chat fake-model ▏  └ execute_tool search_docs ████████████ ← the hidden cost
 └ chat fake-model ▏
```

## How it works
1. **Before: one log line.** `untraced_run.py` logs `{"event": "agent_run", "duration_ms": …}`; `diagnose()` returns `None` because nothing below the run is recorded. → see lab step 2
2. **A span per operation.** `Tracer.span()` is a context manager: it records start, duration, status and parent, and writes one JSON line when the block ends – even when it raises (`status: ERROR`, `error.type`). → see lab step 3
3. **Standard names.** The attributes follow the OpenTelemetry GenAI semantic conventions (status: Development): span name `"{gen_ai.operation.name} {gen_ai.request.model}"`, `gen_ai.operation.name` = `chat` / `execute_tool` / `invoke_agent`, plus `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.usage.input_tokens` / `output_tokens`, `gen_ai.response.finish_reasons`, `gen_ai.tool.name`, `gen_ai.tool.call.id`, `server.address`. Standard names let any backend group and chart them. → see lab step 4
4. **Worked example.** One question produces 8 spans: 1 agent, 4 chat, 3 tools; 109 tokens in total. Grouped by name, `execute_tool search_docs` takes about 600 ms – more than half of the run – while the four model calls are a few milliseconds each. → see lab step 3
5. **Budgets from traces.** The build task checks each span against a latency budget per operation (`execute_tool` ≤ 200 ms) and fixes the cold index with a warm-up at process start. → see lab step 6
6. **Same spans, real SDK.** The OpenTelemetry Python SDK accepts the same names and attributes; swap the JSON-lines writer for an OTLP exporter and the spans appear in Jaeger or Grafana. → see lab step 7

## Failure modes
- **Missing context:** spans without a shared trace id or parent cannot be stitched together; you see orphan spans in the backend.
- **Leaking content:** prompts and tool arguments are opt-in attributes in the conventions because they carry personal data; recording them by default puts secrets in the log store.
- **Cardinality explosion:** putting user ids or full URLs into span names creates millions of distinct names; dashboards slow down and costs rise.
- **Sampling blind spots:** dropping 99 % of traces hides the rare slow path; keep all error traces.

## Common mistakes
- Timing only the model call and never the tools.
- Inventing attribute names per team instead of using the GenAI conventions.
- Logging the total and guessing the cause.
