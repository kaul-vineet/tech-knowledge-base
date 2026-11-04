"""Build task (lesson 17): a tool-result budget lets ONE agent solve t07 inside a 1000-token context.
Default target = solution/trim_results.py. Test YOUR trim_results.py (shipped unfixed, so it fails first):
  BUILD_TARGET=mine python -m unittest -v test_build_task
  PowerShell: $env:BUILD_TARGET="mine"; python -m unittest -v test_build_task"""
import importlib.util
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import fake_server_l400  # noqa: E402
import patterns  # noqa: E402

TARGET = HERE if os.environ.get("BUILD_TARGET") == "mine" else HERE / "solution"
spec = importlib.util.spec_from_file_location("target_trim", TARGET / "trim_results.py")
tr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tr)


class BuildTask(unittest.TestCase):
    def test_single_agent_with_result_budget(self):
        server, url = fake_server_l400.start_in_thread(context_limit=1000)
        try:
            rows = patterns.evaluate("single+trim", url, "fake-model", fn=lambda run, task: patterns.single(run, task, trim=tr.trim))
        finally:
            server.shutdown()
            server.server_close()
        s = patterns.summary(rows)
        print(f"\nsingle+trim: {s['passed']}/10, model calls {s['model_calls']}, tokens {s['tokens']}")
        self.assertEqual(s["passed"], 10)  # t07 now fits in one agent's context
        self.assertLess(s["tokens"], 4821)  # cheaper than the hybrid's supervisor escalation

    def test_trim_keeps_the_fact_line(self):
        out = tr.trim("head fact\n" + "w " * 200, max_words=60)
        self.assertEqual(out.splitlines()[0], "head fact")
        self.assertLessEqual(len(out.split()), 75)


if __name__ == "__main__":
    unittest.main()
