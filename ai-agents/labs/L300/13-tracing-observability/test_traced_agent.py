"""Lesson 13 tests: GenAI span names/attributes, failureLab (log can't find the slow tool, trace can), CLI."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import traced_agent as ta  # noqa: E402
import untraced_run  # noqa: E402
from fake_server_l300 import start_in_thread  # noqa: E402

TASK = 'What is the weather in Paris? Also search docs for "rate limits" and compute 17*23.'


class TracedAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.url = start_in_thread()
        cls.kw = {"base_url": cls.url, "model": "fake-model"}

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        ta._INDEX.clear()  # every test starts cold, like a fresh process
        self.tmp = tempfile.TemporaryDirectory(dir=HERE)
        self.path = Path(self.tmp.name) / "trace.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def spans(self):
        return [json.loads(l) for l in self.path.read_text(encoding="utf-8").splitlines()]

    def test_span_per_model_and_tool_call_with_genai_names(self):
        answer = ta.run(TASK, ta.Tracer(self.path), **self.kw)
        self.assertIn("17*23 = 391", answer)
        spans = self.spans()
        self.assertEqual(sorted(s["name"] for s in spans), ["chat fake-model"] * 4 + [
            "execute_tool calculator", "execute_tool get_weather", "execute_tool search_docs", "invoke_agent support-agent"])
        root = next(s for s in spans if s["parent_span_id"] is None)
        self.assertTrue(all(s["trace_id"] == root["trace_id"] for s in spans))
        self.assertTrue(all(s["parent_span_id"] == root["span_id"] for s in spans if s is not root))
        chat = next(s for s in spans if s["name"].startswith("chat"))
        for key in ("gen_ai.operation.name", "gen_ai.provider.name", "gen_ai.request.model", "gen_ai.response.model",
                    "gen_ai.usage.input_tokens", "gen_ai.usage.output_tokens", "gen_ai.response.finish_reasons",
                    "server.address", "server.port"):
            self.assertIn(key, chat["attributes"])
        tool = next(s for s in spans if s["name"] == "execute_tool search_docs")
        self.assertEqual(tool["attributes"]["gen_ai.tool.call.id"], "call_3")
        self.assertEqual(sum(r["tokens"] for r in ta.summarize(self.path)), sum(
            s["attributes"]["gen_ai.usage.input_tokens"] + s["attributes"]["gen_ai.usage.output_tokens"] for s in spans if s["kind"] == "CLIENT"))

    def test_failure_lab_one_log_line_cannot_find_the_slow_tool(self):
        untraced_run.run_with_log(TASK, self.path, **self.kw)  # before: "the agent is slow" (one duration)
        self.assertGreater(json.loads(self.path.read_text(encoding="utf-8"))["duration_ms"], 600)
        self.assertIsNone(ta.diagnose(self.path))

    def test_failure_lab_trace_names_the_slow_tool(self):
        clock = {"now": 0.0}  # fake clock: only the cold index moves time, so a loaded runner cannot flip the answer
        fake = SimpleNamespace(perf_counter=lambda: clock["now"], sleep=lambda s: clock.update(now=clock["now"] + s))
        with mock.patch.object(ta, "time", fake):
            ta.run(TASK, ta.Tracer(self.path), **self.kw)  # after: spans per call
        self.assertEqual(ta.diagnose(self.path), "execute_tool search_docs")
        self.assertGreaterEqual(next(r for r in ta.summarize(self.path) if r["name"] == "execute_tool search_docs")["ms"], 590)

    def test_error_span(self):
        tracer = ta.Tracer(self.path)
        with self.assertRaises(ZeroDivisionError):
            with tracer.span("execute_tool calculator", "INTERNAL", **{"gen_ai.operation.name": "execute_tool"}):
                ta.TOOLS["calculator"]("1/0")
        self.assertEqual((self.spans()[0]["status"], self.spans()[0]["attributes"]["error.type"]), ("ERROR", "ZeroDivisionError"))

    def test_cli_runs(self):
        env = dict(os.environ, LOCAL_MODEL_URL=self.url, LOCAL_MODEL="fake-model", PYTHONIOENCODING="utf-8")
        out = subprocess.run([sys.executable, "traced_agent.py", str(self.path)], cwd=HERE, env=env,
                             capture_output=True, encoding="utf-8", check=True).stdout
        self.assertIn("slowest below the root: execute_tool search_docs", out)
        csv_path = Path(self.tmp.name) / "spans.csv"  # learning-tools helper (Orange / spreadsheet)
        subprocess.run([sys.executable, "spans_to_csv.py", str(self.path), str(csv_path)], cwd=HERE, check=True,
                       capture_output=True, encoding="utf-8")
        rows = csv_path.read_text(encoding="utf-8").splitlines()
        self.assertEqual((len(rows), rows[0].split(",")[:3]), (9, ["name", "operation", "kind"]))


if __name__ == "__main__":
    unittest.main()
