"""Build task (lesson 19): context-window budgeting. Default target = solution/budget.py.
Test YOUR budget.py (shipped unfixed: cuts the end, so the question disappears):
  BUILD_TARGET=mine python -m unittest -v test_build_task
  PowerShell: $env:BUILD_TARGET="mine"; python -m unittest -v test_build_task"""
import importlib.util
import os
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE if os.environ.get("BUILD_TARGET") == "mine" else HERE / "solution"
spec = importlib.util.spec_from_file_location("target_budget", TARGET / "budget.py")
budget = importlib.util.module_from_spec(spec)
spec.loader.exec_module(budget)

SYSTEM = "You triage incidents. Cite the runbook id."
QUESTION = "QUESTION: why is checkout slow?"
DOCS = [(0.91, "RB-3 " + "latency " * 300), (0.40, "RB-1 " + "unrelated " * 300), (0.85, "RB-7 " + "deploy " * 200)]
HISTORY = [f"turn{i} " + "chat " * 99 for i in range(10)]


class BuildTask(unittest.TestCase):
    def test_priority_not_position(self):
        out = budget.fit(SYSTEM, QUESTION, DOCS, HISTORY, num_ctx=1000, reserve=200).split()
        print(f"\nfit: {len(out)} words; question kept {QUESTION.split()[0] in out}; docs {[w for w in out if w.startswith('RB-')]}")
        self.assertLessEqual(len(out), 800)  # input never eats the output reserve
        self.assertEqual(out[:len(SYSTEM.split())], SYSTEM.split())
        self.assertEqual(out[-len(QUESTION.split()):], QUESTION.split())
        self.assertIn("RB-3", out)  # the best document survives
        self.assertNotIn("RB-1", out)  # the weakest one is dropped first
        self.assertIn("turn9", out)  # the newest history survives
        self.assertNotIn("turn0", out)


if __name__ == "__main__":
    unittest.main()
