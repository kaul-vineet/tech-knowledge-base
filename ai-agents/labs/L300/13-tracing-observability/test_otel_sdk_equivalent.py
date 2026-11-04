"""pending-ci: the official OpenTelemetry SDK records the same span names and attribute keys as Tracer."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import traced_agent as ta  # noqa: E402
from fake_server_l300 import start_in_thread  # noqa: E402

TASK = 'What is the weather in Paris? Also search docs for "rate limits" and compute 17*23.'


def _has_sdk():
    try:
        return importlib.util.find_spec("opentelemetry.sdk") is not None
    except ModuleNotFoundError:
        return False


@unittest.skipUnless(_has_sdk(), "opentelemetry-sdk not installed (CI equivalents job)")
class OTelEquivalent(unittest.TestCase):
    def test_same_spans(self):
        from otel_sdk_equivalent import OTelTracer
        server, url = start_in_thread()
        try:
            with tempfile.TemporaryDirectory(dir=HERE) as d:
                path = Path(d) / "t.jsonl"
                ta.run(TASK, ta.Tracer(path), base_url=url, model="fake-model")
                ours = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]
            otel = OTelTracer()
            ta.run(TASK, otel, base_url=url, model="fake-model")
        finally:
            server.shutdown()
            server.server_close()
        key = lambda s: (s["name"], s["kind"], sorted(s["attributes"]))
        self.assertEqual(sorted(map(key, ours)), sorted(map(key, otel.finished())))


if __name__ == "__main__":
    unittest.main()
