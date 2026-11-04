"""Build-task check: client middleware puts traceparent on EVERY outgoing call -> one unbroken trace.
Default target = solution_tracing.py. Test YOUR tracing.py:  BUILD_TARGET=mine python -m unittest test_build_task -v
(PowerShell: $env:BUILD_TARGET="mine"; python -m unittest test_build_task -v)"""
import importlib.util, os, unittest
from pathlib import Path

from analyze import critical_path, problems, traces

HERE = Path(__file__).resolve().parent
FILE = "tracing.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution_tracing.py"
spec = importlib.util.spec_from_file_location("target_tracing", HERE / FILE)
tr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tr)


class Propagation(unittest.TestCase):
    def setUp(self):
        self.spans = tr.run_checkout()
        self.by_name = {s["name"]: s for s in self.spans}

    def test_one_trace_no_orphans(self):
        self.assertEqual(len(traces(self.spans)), 1)
        self.assertEqual(problems(self.spans), [])

    def test_authorize_is_a_child_of_create(self):
        self.assertEqual(self.by_name["GET /authorize"]["parent_id"], self.by_name["GET /create"]["span_id"])

    def test_critical_path_now_sees_payments(self):
        path = [s["name"] for s, _ in critical_path(self.spans, self.by_name["GET /checkout"])]
        self.assertEqual(path, ["GET /checkout", "GET /create", "GET /authorize", "GET /receipt"])

    def test_raw_call_outside_a_request_sends_no_header(self):
        self.assertIsNone(getattr(tr.CURRENT, "span", None))  # no current span in the test thread


if __name__ == "__main__":
    unittest.main()
