"""Build task (lesson 8): add a 4th tool, get_time. Proves solution/get_time_tool.py works."""
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "solution"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "L100", "01-setup"))
import get_time_tool  # noqa: E402,F401  (registers get_time)
import multi_tool_agent as agent  # noqa: E402
from fake_model_server import start_in_thread  # noqa: E402


def tearDownModule():
    agent.REGISTRY.pop("get_time", None)  # keep other test modules' tool list unchanged


class BuildTask(unittest.TestCase):
    def test_get_time_is_selected_with_calculator(self):
        server, url = start_in_thread()
        try:
            result = agent.run_agent("What time is it? Also compute 2+3.", base_url=url, model="fake-model")
        finally:
            server.shutdown()
        self.assertEqual(result["stopped"], "final_answer")
        self.assertRegex(result["answer"], r"get_time\(\) = \d{4}-\d\d-\d\dT")
        self.assertIn("2+3 = 5", result["answer"])

    def test_no_parameter_schema_rejects_arguments(self):
        self.assertIn("additional property not allowed", agent.execute("get_time", '{"tz": "UTC"}'))
        self.assertTrue(re.match(r"\d{4}-", agent.execute("get_time", "{}")))


if __name__ == "__main__":
    unittest.main()
