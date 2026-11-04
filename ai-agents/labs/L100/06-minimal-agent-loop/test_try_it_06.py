"""Try it (lesson 6): two small changes, run against the fake server. Run: python -m unittest -v test_try_it_06"""
import contextlib
import io
import os
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "01-setup"))
import agent_loop  # noqa: E402
from fake_model_server import start_in_thread  # noqa: E402

TASK = "Use the calculator to compute 17*23 and (120-20)/4, then report both results."


class TryIt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.base_url = start_in_thread()
        cls.kw = {"base_url": cls.base_url, "model": "fake-model"}

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_1_budget_two(self):
        # change max_steps to 2
        with contextlib.redirect_stdout(io.StringIO()):
            result = agent_loop.run_agent(TASK, max_steps=2, **self.kw)
        print("\nobserved:", result)
        self.assertEqual(result, {"answer": None, "steps": 2, "stopped": "max_steps"})

    def test_2_calculator_needs_approval(self):
        # flip the calculator's "needs approval" flag to True and keep the default approver (deny)
        fn, _, schema = agent_loop.REGISTRY["calculator"]
        out = io.StringIO()
        with mock.patch.dict(agent_loop.REGISTRY, {"calculator": (fn, True, schema)}), \
                contextlib.redirect_stdout(out):
            result = agent_loop.run_agent(TASK, max_steps=5, **self.kw)
        print("\nobserved:", out.getvalue().strip().splitlines()[-1])
        self.assertEqual(result["stopped"], "final_answer")
        self.assertIn("denied", result["answer"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
