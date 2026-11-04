# 15 · Distributed tracing with W3C traceparent

Three stdlib HTTP services on `127.0.0.1` (OS-chosen ports): **gateway** `/checkout` calls **orders** `/create`, which calls **payments** `/authorize`; then the gateway calls **payments** `/receipt`. Each service has **server middleware** (`Service.do_GET`): it reads the incoming `traceparent` header (W3C Trace Context: `00-<trace-id 32 hex>-<parent-id 16 hex>-<flags>`), starts a span with a new span id, makes it the current context, and records the span as a JSON line. Outgoing calls made with `traced_call()` send `00-<same trace-id>-<my span id>-<flags>`: the incoming trace-flags pass on unchanged (`01` = sampled for a trace this service starts), so the caller's sampling decision holds downstream (W3C §3.2.2.5.1). The parser rejects uppercase hex, all-zero ids, version `ff` and extra fields on version 00; a higher version keeps its first four fields (§3.2.4). `analyze.py` reads the spans like a tracing backend: groups them into traces, rebuilds the tree from parent ids, finds the **critical path** and reports broken traces.

Fault: `orders` calls payments with a raw `call()` written before tracing existed — **one hop drops the header**. Payments starts a new trace; the request now shows up as two traces, and the 60 ms spent in payments is invisible: the critical path blames `orders` for it.

Files: `tracing.py` (lesson: `parse_traceparent`, `traced_call`, `Service` middleware, the three services) · `analyze.py` (traces, critical path, problems) · `helpers.py` (plumbing: quiet JSON handler, `call()`, `serve()`) · `try_it.py` · `test_tracing.py` · build task: `solution_tracing.py` + `test_build_task.py` · `otel_equivalent.py` + `requirements-otel.txt` (the same with the OpenTelemetry SDK; CI only).

## Run (Mac mini: `python3` inside the venv is `python`; Windows: same commands in PowerShell)
```bash
python tracing.py
```

## Expected output (real run, Python 3.12.15, Linux)
Ids are seeded, so they repeat; **times are real and vary** from run to run (about 100 ms for `/checkout`: 5 + 20 + 60 + 10 ms of simulated work plus HTTP overhead).
```
spans (JSON lines, one per request):
  {"trace_id": "8575062102fbcd4f357fbc5af71a1bfc", "span_id": "0942dc06bc69f265", "parent_id": null, "service": "gateway", "name": "GET /checkout", "start": 0.0, "end": 114.4}
  {"trace_id": "8575062102fbcd4f357fbc5af71a1bfc", "span_id": "e9bb466a28738582", "parent_id": "0942dc06bc69f265", "service": "orders", "name": "GET /create", "start": 10.5, "end": 98.0}
  {"trace_id": "0e11160004524a7c3d2bd371fc80be13", "span_id": "ce0c3f08e12656f1", "parent_id": null, "service": "payments", "name": "GET /authorize", "start": 37.4, "end": 97.5}
  {"trace_id": "8575062102fbcd4f357fbc5af71a1bfc", "span_id": "25b2116aae6cff55", "parent_id": "0942dc06bc69f265", "service": "payments", "name": "GET /receipt", "start": 103.9, "end": 114.0}
trace 85750621..: 3 span(s): gateway GET /checkout, orders GET /create, payments GET /receipt
trace 0e111600..: 1 span(s): payments GET /authorize
critical path: gateway GET /checkout self 17 ms | orders GET /create self 88 ms | payments GET /receipt self 10 ms
trace problems:
  2 trace ids for one request (a hop did not propagate traceparent)
  extra root span: payments GET /authorize started a new trace
```
Read it like an on-call engineer: one request, two trace ids; `payments GET /authorize` has `parent_id: null` (it started its own trace); `orders GET /create` shows 88 ms of "self time" in this run — 20 ms of its own work plus the invisible ~60 ms payments call (compare 28 ms after the fix).

## Test
```bash
python -m unittest -v     # Ran 11 tests ... OK  (7 lesson tests, incl. sampled-flag propagation + 4 build-task tests against the solution)
```

## Build task: propagation as client middleware
Do not just fix the one call site. Replace `call` in `tracing.py` with a wrapper around `helpers.call` that injects the current context into **every** outgoing request (and make `traced_call` the same function), so a raw `call()` added later cannot break the trace again.
```bash
BUILD_TARGET=mine python -m unittest test_build_task -v                     # macOS (zsh)
$env:BUILD_TARGET="mine"; python -m unittest test_build_task -v             # Windows (PowerShell)
```
Before your change (real run): `Ran 4 tests ... FAILED (failures=3)` (`AssertionError: 2 != 1` trace ids; `None != 'e9bb466a28738582'` parent of `/authorize`). The reference `solution_tracing.py` prints (times vary):
```
spans (JSON lines, one per request):
  {"trace_id": "8575062102fbcd4f357fbc5af71a1bfc", "span_id": "0942dc06bc69f265", "parent_id": null, "service": "gateway", "name": "GET /checkout", "start": 0.0, "end": 121.3}
  {"trace_id": "8575062102fbcd4f357fbc5af71a1bfc", "span_id": "e9bb466a28738582", "parent_id": "0942dc06bc69f265", "service": "orders", "name": "GET /create", "start": 16.4, "end": 104.7}
  {"trace_id": "8575062102fbcd4f357fbc5af71a1bfc", "span_id": "3d2bd371fc80be13", "parent_id": "e9bb466a28738582", "service": "payments", "name": "GET /authorize", "start": 43.9, "end": 104.1}
  {"trace_id": "8575062102fbcd4f357fbc5af71a1bfc", "span_id": "0e11160004524a7c", "parent_id": "0942dc06bc69f265", "service": "payments", "name": "GET /receipt", "start": 110.6, "end": 120.9}
trace 85750621..: 4 span(s): gateway GET /checkout, orders GET /create, payments GET /authorize, payments GET /receipt
critical path: gateway GET /checkout self 23 ms | orders GET /create self 28 ms | payments GET /authorize self 60 ms | payments GET /receipt self 10 ms
trace problems:
  none
```

## Try it (real run — `python try_it.py`; percentages vary by a few points)
```
tryIt 1: 00-4bf92f3577b34da6a... -> gateway trace 4bf92f3577b3.., parent 00f067aa0ba902b7 | traces: 1
tryIt 1: 00-4BF92F3577B34DA6A... -> gateway trace 0e1116000452.., parent None | traces: 1
tryIt 1: 00-00000000000000000... -> gateway trace 77616364568c.., parent None | traces: 1
tryIt 2: authorize work 60 ms -> its span is 52% of the checkout, on the critical path: True
tryIt 2: authorize work 180 ms -> its span is 76% of the checkout, on the critical path: True
```
tryIt 1: a valid incoming header is continued (same trace id, the caller's span becomes the parent); uppercase hex or an all-zero trace id is invalid, so the gateway **restarts** the trace. tryIt 2: make `/authorize` 3x slower and its share of the checkout jumps; it stays on the critical path.

## Same thing with OpenTelemetry (pending-ci)
`otel_equivalent.py` checks both directions with the OpenTelemetry SDK 1.45.1: a header injected by `TraceContextTextMapPropagator` is accepted by this lab's parser with the same ids; this lab's header extracted by OTel becomes the parent of OTel spans; an all-zero trace id is rejected by both. `--otlp` also exports a trace to Jaeger (OTLP/HTTP on `localhost:4318`). Not run here (no PyPI access in the sandbox); the CI job `otel` installs `requirements-otel.txt` and runs it.
```bash
python -m pip install -r requirements-otel.txt      # macOS and Windows, inside the venv
python otel_equivalent.py                            # ends with: otel equivalent OK
```

## Platform notes
Servers bind `127.0.0.1` with OS-chosen ports; durations come from `time.perf_counter()` (fine on Windows). Windows timer resolution can add a few ms to each `time.sleep`; the analysis does not depend on exact times.
