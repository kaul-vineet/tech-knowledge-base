import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "01-setup"))
import agent_loop  # noqa: E402
from fake_model_server import start_in_thread  # noqa: E402

TASK = "Use the calculator to compute 17*23 and (120-20)/4, then report both results."


class AgentLoopTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.base_url = start_in_thread()
        cls.kw = {"base_url": cls.base_url, "model": "fake-model"}

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_calculator_is_safe_and_correct(self):
        self.assertEqual(agent_loop.calculator("17*23"), 391)
        self.assertEqual(agent_loop.calculator("(120-20)/4"), 25.0)
        self.assertEqual(agent_loop.calculator("-2*3"), -6)
        with self.assertRaises(ValueError):
            agent_loop.calculator("__import__('os').getcwd()")

    def test_loop_reaches_final_answer(self):
        result = agent_loop.run_agent(TASK, max_steps=5, **self.kw)
        self.assertEqual(result["stopped"], "final_answer")
        self.assertEqual(result["steps"], 3)  # 2 tool steps + 1 final answer
        self.assertEqual(result["answer"], "Final answer: 17*23 = 391; (120-20)/4 = 25.0")

    def test_budget_stops_loop(self):
        result = agent_loop.run_agent(TASK, max_steps=1, **self.kw)
        self.assertEqual((result["stopped"], result["answer"]), ("max_steps", None))

    def test_tool_errors_are_returned_not_raised(self):
        self.assertTrue(agent_loop.execute("calculator", {"expression": "1/0"}).startswith("error:"))
        self.assertTrue(agent_loop.execute("rm_rf", {}).startswith("error: unknown tool"))

    def test_risky_tool_needs_approval(self):
        deleted = []
        agent_loop.REGISTRY["delete_file"] = (lambda path: deleted.append(path) or "deleted", True, {})
        try:
            self.assertIn("denied", agent_loop.execute("delete_file", {"path": "a.txt"}))
            self.assertEqual(deleted, [])  # default approver says no
            ok = agent_loop.execute("delete_file", {"path": "a.txt"}, approve=lambda n, a: True)
            self.assertEqual((ok, deleted), ("deleted", ["a.txt"]))
        finally:
            del agent_loop.REGISTRY["delete_file"]

    def test_cli_runs(self):
        env = dict(os.environ, LOCAL_MODEL_URL=self.base_url, LOCAL_MODEL="fake-model", PYTHONIOENCODING="utf-8")  # same pipe encoding on Windows
        out = subprocess.run([sys.executable, "agent_loop.py"], cwd=HERE, env=env,
                             capture_output=True, encoding="utf-8", check=True).stdout
        self.assertIn("'stopped': 'final_answer'", out)
        self.assertIn("'stopped': 'max_steps'", out)


if __name__ == "__main__":
    unittest.main()
