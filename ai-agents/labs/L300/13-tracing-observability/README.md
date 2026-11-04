# 13 – Tracing and observability

An agent run is a tree of model calls and tool calls; a trace records each one as a span with duration, tokens and status, so you can see which part is slow, expensive or failing.

Concept note: `../../../content/concepts/L300/13-tracing-observability.md` · lesson object: `content/L300.json` #13

## Run (fake server – validated)
```bash
python ../fake_server_l300.py --port 8765   # terminal 1
export LOCAL_MODEL_URL=http://127.0.0.1:8765/v1 LOCAL_MODEL=fake-model   # terminal 2
python untraced_run.py
python traced_agent.py
python -m unittest -v
```
PowerShell (Windows 11):
```powershell
python ..\fake_server_l300.py --port 8765   # terminal 1
$env:LOCAL_MODEL_URL="http://127.0.0.1:8765/v1"; $env:LOCAL_MODEL="fake-model"   # terminal 2
python untraced_run.py
python traced_agent.py
python -m unittest -v
```

### Expected output (observed 2026-10-28)
Before (one log line per run):
```
{"event": "agent_run", "duration_ms": 611.0, "answer_chars": 171}
slowest below the root: None
```
After (spans; `GENAI_PROVIDER=fake` was set in terminal 2):
```
answer: Final answer: 17*23 = 391; get_weather(city=Paris) = Paris: 18 degrees celsius, light rain; search_docs(query=rate limits) = The API allows 60 requests per minute per key.
invoke_agent support-agent   x1    643.6 ms  share 100%  tokens 0
execute_tool search_docs     x1    600.2 ms  share 93%  tokens 0
chat fake-model              x4     21.7 ms  share 3%  tokens 109
execute_tool calculator      x1      0.2 ms  share 0%  tokens 0
execute_tool get_weather     x1      0.0 ms  share 0%  tokens 0
slowest below the root: execute_tool search_docs
```
Two lines of `trace.jsonl` (a tool span and the root):
```
{"trace_id": "cd18fc9fb6494384932af3bda6fe8102", "span_id": "d1347120363c2b31", "parent_span_id": "c0fa7a26774e22af", "name": "execute_tool get_weather", "kind": "INTERNAL", "status": "OK", "attributes": {"gen_ai.operation.name": "execute_tool", "gen_ai.tool.name": "get_weather", "gen_ai.tool.call.id": "call_2", "gen_ai.tool.type": "function"}, "start_ms": 28.9, "duration_ms": 0.0}
{"trace_id": "cd18fc9fb6494384932af3bda6fe8102", "span_id": "c0fa7a26774e22af", "parent_span_id": null, "name": "invoke_agent support-agent", "kind": "INTERNAL", "status": "OK", "attributes": {"gen_ai.operation.name": "invoke_agent", "gen_ai.provider.name": "fake", "gen_ai.agent.name": "support-agent"}, "start_ms": 1.7, "duration_ms": 643.6}
```
A chat span additionally carries `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.response.finish_reasons`, `server.address`, `server.port`. Durations vary by machine; ids are seeded.

Tests: `Ran 9 tests ... OK (skipped=1)` – the skipped test needs `opentelemetry-sdk==1.45.1` (`../requirements-equivalents.txt`, CI equivalents job).

## Failure lab
| | |
|---|---|
| Fault (seeded) | search_docs loads its index on first use (COLD_INDEX_S = 0.6 s, constant); the model server is fast. |
| Symptom | Users say 'the agent is slow'. The run log has one line: duration_ms 611 - and diagnose() cannot name a cause (None). |
| Fix | Add a span per agent run, model call and tool call with GenAI attribute names; group by span name. |
| Proof | test_failure_lab_one_log_line_cannot_find_the_slow_tool (diagnose -> None) vs test_failure_lab_trace_names_the_slow_tool (-> 'execute_tool search_docs', span >= 590 ms). |

## Trade-offs
| Option | Gains | Costs | Choose when |
|---|---|---|---|
| JSON-lines spans (this lab) | Zero dependencies, greppable, easy to test | No UI, no sampling, no context propagation across services | Learning, single-process tools, CI artefacts |
| OpenTelemetry SDK + OTLP exporter | Standard pipeline to Jaeger/Tempo/Grafana; context propagation; sampling | Dependencies and a collector to run | Anything other people operate |
| Capture prompts/outputs on spans (opt-in) | Debug wrong answers, not just slow ones | Personal data and secrets in the trace store; size | Short retention, access-controlled store, redaction in place |

## Build task
Start from the shipped latency_budget.py (unfixed: only the whole run is checked against 2 s, and warm_up() does nothing). Add a latency budget per operation (chat <= 500 ms, execute_tool <= 200 ms) checked from the trace, then fix the violation by warming the index at process start.

Hints:
- Read the JSON lines; look up the budget by attributes['gen_ai.operation.name'].
- Return one readable line per violation.
- warm_up() just calls load_index() before the first request.

Your file: `latency_budget.py` (shipped unfixed) · solution: `solution/latency_budget.py` · the same test checks either one:
```bash
BUILD_TARGET=mine python -m unittest -v test_build_task   # YOUR file
python -m unittest -v test_build_task                     # the solution (default, what CI runs)
```
PowerShell: `$env:BUILD_TARGET="mine"; python -m unittest -v test_build_task` (`Remove-Item Env:BUILD_TARGET` to switch back).

Observed 2026-10-28 – shipped file (fail-before) vs solution (pass-after):
```
BUILD_TARGET=mine  -> AssertionError: Lists differ: [] != ['execute_tool search_docs: 600 ms > 200 ms']
                      FAILED (failures=1)
solution           -> Ran 1 test ... OK
```
The test is deterministic (review R3-02): it swaps `traced_agent.time` for a fake clock, so time moves only in the cold-index sleep (exactly 600 ms) and every HTTP call costs 0 ms; it also counts the 8 spans. No wall-clock budget is asserted, so a slow or busy runner cannot flip it (5 runs OK). The failure-lab trace test uses the same clock.

## Attribute names used (OpenTelemetry GenAI semantic conventions, status Development, checked 2026-10-28)
| Span | Name | Attributes |
|---|---|---|
| agent run | `invoke_agent {gen_ai.agent.name}` | gen_ai.operation.name=invoke_agent, gen_ai.provider.name, gen_ai.agent.name |
| model call | `chat {gen_ai.request.model}` (CLIENT) | gen_ai.operation.name=chat, gen_ai.provider.name, gen_ai.request.model, gen_ai.response.model, gen_ai.usage.input_tokens, gen_ai.usage.output_tokens, gen_ai.response.finish_reasons, server.address, server.port, error.type on failure |
| tool call | `execute_tool {gen_ai.tool.name}` | gen_ai.operation.name=execute_tool, gen_ai.tool.name, gen_ai.tool.call.id, gen_ai.tool.type |

`gen_ai.provider.name` has no well-known value for Ollama; a custom value is allowed (default here `ollama`, `GENAI_PROVIDER` overrides). Prompt and output content attributes are opt-in and deliberately not recorded.

## Equivalents
- OpenTelemetry Python SDK 1.45.1 (Apache-2.0): same span() shape, OTLP exporter to Jaeger/Tempo (otel_sdk_equivalent.py)
- OpenTelemetry GenAI instrumentation packages wrap popular client libraries automatically; check which convention version they emit (OTEL_SEMCONV_STABILITY_OPT_IN)
- Hosted LLM-observability services exist; prefer ones that accept OTLP so the instrumentation stays vendor-neutral

## Optional steps (not run in the sandbox)
**the same spans through the OpenTelemetry SDK** – OTelTracer has the same span() interface, so traced_agent.run() is unchanged; InMemorySpanExporter here, an OTLP exporter in production.
```
python -m pip install -r ../requirements-equivalents.txt
python -m unittest -v test_otel_sdk_equivalent
```
PowerShell:
```powershell
python -m pip install -r ..\requirements-equivalents.txt
python -m unittest -v test_otel_sdk_equivalent
```
Expected: Pending CI: same span names, kinds and attribute keys as trace.jsonl

**see the trace in Jaeger (learning tool, manual)** – start Jaeger 2.22.0 (UI :16686, OTLP/HTTP :4318), keep the fake server running, then send one run through the OTLP/HTTP exporter (`opentelemetry-exporter-otlp-proto-http==1.45.1`, in `../requirements-equivalents.txt`):
```
python -m pip install -r ../requirements-equivalents.txt
export LOCAL_MODEL_URL=http://127.0.0.1:8765/v1 LOCAL_MODEL=fake-model
python otel_sdk_equivalent.py --otlp
```
PowerShell:
```powershell
python -m pip install -r ..\requirements-equivalents.txt
$env:LOCAL_MODEL_URL="http://127.0.0.1:8765/v1"; $env:LOCAL_MODEL="fake-model"
python otel_sdk_equivalent.py --otlp
```
Expected (pending a manual run): service `support-agent`, one trace whose longest bar is `execute_tool search_docs` (~600 ms of ~644 ms), next to four short `chat fake-model` spans – the same story as the summarize() table above.


## Troubleshooting
| Symptom | Action |
|---|---|
| Spans appear but never nest | Open child spans inside the parent's with-block (or pass context explicitly across threads). |
| Token counts are 0 on tool-call turns | The fake counts words of the reply text; real servers report usage.completion_tokens for tool calls too. |
| Trace store grows fast | Do not record prompts by default; sample successful traces, keep all error traces. |

## Try it (validated, observed 2026-10-28)
Predict first, then run `python -m unittest -v test_try_it_13` (each test makes the change and prints what it observed).

| Change | Observed |
|---|---|
| Set COLD_INDEX_S = 0 (no cold index) and run the traced agent again. | [('invoke_agent support-agent', 1), ('chat fake-model', 4)] | slowest: chat fake-model - with the tool fixed, the 4 model calls are the biggest cost. |
| Keep the cold index but make every model call 250 ms slower (fake server slow_rate=1.0, slow_s=0.25). | [('invoke_agent support-agent', 1), ('chat fake-model', 4)] | slowest: chat fake-model - 4 x 250 ms beats one 600 ms tool; the trace tells the two stories apart. |
