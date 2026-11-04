"""The same propagation with the OpenTelemetry SDK (pending-ci: not run in the sandbox, no PyPI access).
    pip install -r requirements-otel.txt        (opentelemetry-api/sdk/exporter-otlp-proto-http 1.45.1)
    python otel_equivalent.py                   # checks OTel <-> this lab's traceparent, both directions
    python otel_equivalent.py --otlp            # also exports the spans to Jaeger (OTLP/HTTP, localhost:4318)
Ends with 'otel equivalent OK'."""
import sys

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

import tracing

memory = InMemorySpanExporter()
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(memory))
if "--otlp" in sys.argv:
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")))
trace.set_tracer_provider(provider)
tracer, propagator = trace.get_tracer("lesson15"), TraceContextTextMapPropagator()

# 1) OTel -> lab: the header OTel injects is accepted by the lab's parser, same ids
with tracer.start_as_current_span("gateway GET /checkout") as span:
    carrier = {}
    propagator.inject(carrier)
    ctx = span.get_span_context()
parsed = tracing.parse_traceparent(carrier["traceparent"])
assert parsed[:2] == (format(ctx.trace_id, "032x"), format(ctx.span_id, "016x")), (carrier, parsed)
print("OTel injected:", carrier["traceparent"], "-> lab parser:", parsed)

# 2) lab -> OTel: a header in the lab's format becomes the parent of an OTel span (the W3C example ids)
header = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
with tracer.start_as_current_span("orders GET /create", context=propagator.extract({"traceparent": header})) as child:
    with tracer.start_as_current_span("payments GET /authorize"):
        pass
spans = {s.name: s for s in memory.get_finished_spans()}
create = spans["orders GET /create"]
assert format(create.context.trace_id, "032x") == "4bf92f3577b34da6a3ce929d0e0e4736"
assert format(create.parent.span_id, "016x") == "00f067aa0ba902b7"
assert spans["payments GET /authorize"].parent.span_id == create.context.span_id
print("lab header -> OTel child span in trace", format(create.context.trace_id, "032x"))

# 3) an invalid header (all-zero trace id) starts a new trace in both implementations
bad = "00-00000000000000000000000000000000-00f067aa0ba902b7-01"
assert tracing.parse_traceparent(bad) is None
assert not trace.get_current_span(propagator.extract({"traceparent": bad})).get_span_context().is_valid
provider.shutdown()
print("otel equivalent OK")
