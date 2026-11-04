"""Same spans through the official OpenTelemetry Python SDK (pending-ci: pip install opentelemetry-sdk==1.45.1).

OTelTracer has the same span() interface as traced_agent.Tracer, so traced_agent.run() is unchanged.
Default exporter: InMemorySpanExporter (tests). Jaeger (learning tool, manual):
    python otel_sdk_equivalent.py --otlp   -> OTLP/HTTP to http://localhost:4318/v1/traces, then open http://localhost:16686
    (needs opentelemetry-exporter-otlp-proto-http==1.45.1 from ../requirements-equivalents.txt and LOCAL_MODEL_URL set)
"""
import sys
from contextlib import contextmanager

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import SpanKind, Status, StatusCode

KINDS = {"CLIENT": SpanKind.CLIENT, "INTERNAL": SpanKind.INTERNAL}


class OTelTracer:
    def __init__(self, exporter=None):
        self.exporter = exporter or InMemorySpanExporter()
        self.provider = TracerProvider(resource=Resource.create({"service.name": "support-agent"}))
        self.provider.add_span_processor(SimpleSpanProcessor(self.exporter))
        self.tracer = self.provider.get_tracer("traced_agent")

    @contextmanager
    def span(self, name, kind, **attributes):
        with self.tracer.start_as_current_span(name, kind=KINDS[kind]) as span:
            try:
                yield attributes
            except Exception as e:
                attributes["error.type"] = type(e).__name__
                span.set_status(Status(StatusCode.ERROR))
                raise
            finally:
                span.set_attributes({k: v for k, v in attributes.items() if v is not None})

    def finished(self):
        return [{"name": s.name, "kind": s.kind.name, "attributes": dict(s.attributes)} for s in self.exporter.get_finished_spans()]


if __name__ == "__main__" and "--otlp" in sys.argv:
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

    import traced_agent
    tracer = OTelTracer(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces"))
    print("answer:", traced_agent.run('What is the weather in Paris? Also search docs for "rate limits" and compute 17*23.', tracer))
    tracer.provider.shutdown()  # flush, then search service "support-agent" in Jaeger
