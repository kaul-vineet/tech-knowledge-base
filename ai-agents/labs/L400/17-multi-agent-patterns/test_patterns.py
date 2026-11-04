"""Lesson 17: every design on the fixed task set + the failure lab (python -m unittest -v test_patterns)."""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import fake_server_l400  # noqa: E402
import patterns  # noqa: E402


class Patterns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.url = fake_server_l400.start_in_thread(context_limit=1000)
        cls.s = {n: patterns.summary(patterns.evaluate(n, cls.url, "fake-model")) for n in patterns.PATTERNS}

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_measured_table(self):
        got = {n: (s["passed"], s["model_calls"], s["tokens"], s["failed"]) for n, s in self.s.items()}
        self.assertEqual(got, {"single": (9, 26, 4753, ["t07"]), "router": (6, 33, 2982, ["t05", "t06", "t07", "t09"]),
                               "planner": (9, 20, 1937, ["t09"]), "supervisor": (9, 52, 3977, ["t09"]),
                               "hybrid": (10, 30, 4821, [])})

    def test_failure_lab_single_overflows(self):
        row = patterns.evaluate("single", self.url, "fake-model", tasks=[patterns.ow.TASKS[6]])[0]
        self.assertFalse(row["pass"])
        self.assertTrue(row["error"].startswith("context_length_exceeded: 1137 prompt tokens > context 1000"))

    def test_failure_lab_hybrid_escalates(self):
        self.assertEqual((patterns.estimate(patterns.ow.TASKS[6][1]), patterns.estimate(patterns.ow.TASKS[0][1])), (1178, 143))
        row = patterns.evaluate("hybrid", self.url, "fake-model", tasks=[patterns.ow.TASKS[6]])[0]
        self.assertEqual((row["pass"], row["model_calls"], row["error"]), (True, 8, None))

    def test_planner_cannot_adapt_to_observations(self):
        row = patterns.evaluate("planner", self.url, "fake-model", tasks=[patterns.ow.TASKS[8]])[0]
        self.assertEqual((row["pass"], row["model_calls"]), (False, 2))  # deploys never checked: no observation

    def test_unknown_route_gets_no_tools(self):
        run = patterns.Run(self.url, "fake-model")
        self.assertEqual(patterns.loop(run, "Check metrics for checkout.", patterns.ow.SPECIALISTS.get("ghost", [])),
                         "Hello from fake-model! You said: 'Check metrics for checkout.'")
        self.assertEqual(run.world.calls, [])

    def test_world_refuses_unknown_tool(self):
        self.assertEqual(patterns.ow.World().run("rm_rf", {}), "error: unknown tool rm_rf")

    def test_cli(self):
        env = {**os.environ, "LOCAL_MODEL_URL": self.url, "LOCAL_MODEL": "fake-model"}
        out = subprocess.run([sys.executable, "patterns.py"], cwd=HERE, env=env, capture_output=True, text=True,
                             encoding="utf-8", timeout=120)
        self.assertIn("hybrid     10/10 passed", out.stdout)
        rows = [json.loads(x) for x in (HERE / "patterns.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(rows), 50)


if __name__ == "__main__":
    unittest.main()
