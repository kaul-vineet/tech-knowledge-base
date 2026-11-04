"""Build task (lesson 13): latency budget per operation; warm-up moves the cold index out of the request.
Deterministic: a fake clock replaces time in traced_agent, so the cold index costs exactly 600 ms and every
HTTP call 0 ms - no wall-clock budget can flake on a slow runner.
Default target = solution/latency_budget.py. Test YOUR latency_budget.py (shipped unfixed, so it fails first):
  BUILD_TARGET=mine python -m unittest -v test_build_task
  PowerShell: $env:BUILD_TARGET="mine"; python -m unittest -v test_build_task"""
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import traced_agent as ta  # noqa: E402
from fake_server_l300 import start_in_thread  # noqa: E402

TARGET = HERE if os.environ.get("BUILD_TARGET") == "mine" else HERE / "solution"
spec = importlib.util.spec_from_file_location("target_latency_budget", TARGET / "latency_budget.py")
lb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lb)
TASK = 'What is the weather in Paris? Also search docs for "rate limits" and compute 17*23.'


class FakeClock:
    """Time moves only when the code sleeps (the cold index); HTTP calls take 0 ms."""

    def __init__(self):
        self.now = 0.0

    def perf_counter(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def fake_time():
    clock = FakeClock()
    return mock.patch.object(ta, "time", SimpleNamespace(perf_counter=clock.perf_counter, sleep=clock.sleep))


class BuildTask(unittest.TestCase):
    def test_budget_violation_then_fixed_by_warm_up(self):
        server, url = start_in_thread()
        try:
            with tempfile.TemporaryDirectory(dir=HERE) as d, fake_time():
                cold, warm = Path(d) / "cold.jsonl", Path(d) / "warm.jsonl"
                ta._INDEX.clear()
                ta.run(TASK, ta.Tracer(cold), base_url=url, model="fake-model")
                spans = [json.loads(line) for line in cold.read_text(encoding="utf-8").splitlines()]
                violations = lb.check_budgets(cold)
                ta._INDEX.clear()
                lb.warm_up(ta)  # at process start
                ta.run(TASK, ta.Tracer(warm), base_url=url, model="fake-model")
                warm_violations = lb.check_budgets(warm)
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(len(spans), 8)  # 1 root + 4 chat + 3 execute_tool: the budget sees every span
        self.assertEqual(violations, ["execute_tool search_docs: 600 ms > 200 ms"])
        self.assertEqual(warm_violations, [])


if __name__ == "__main__":
    unittest.main()
