import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "L100", "01-setup"))
import multi_tool_agent as agent  # noqa: E402
from fake_model_server import start_in_thread  # noqa: E402
from schema_check import validate  # noqa: E402

TASK = 'Compute 12*7, tell me the weather in Paris in kelvin, and search docs for "context window" top 50.'


class MultiToolAgentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.base_url = start_in_thread()
        cls.kw = {"base_url": cls.base_url, "model": "fake-model"}

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_validator_rejects_before_running(self):
        self.assertEqual(agent.execute("get_weather", '{"city": "Paris"}'), "18 C")
        self.assertIn("is not one of", agent.execute("get_weather", '{"city": "Paris", "unit": "kelvin"}'))
        self.assertIn("$.city: is required", agent.execute("get_weather", "{}"))
        self.assertIn("additional property not allowed", agent.execute("get_weather", '{"city": "Oslo", "x": 1}'))
        self.assertIn("greater than the maximum of 5", agent.execute("search_docs", '{"query": "tokens", "top_k": 9}'))

    def test_errors_are_strings_not_exceptions(self):
        self.assertTrue(agent.execute("delete_all", "{}").startswith("error: unknown tool 'delete_all'"))
        self.assertIn("not valid JSON", agent.execute("calculator", "{expression: 1}"))
        self.assertEqual(agent.execute("get_weather", '{"city": "Rome"}'), "error: no data for Rome")
        self.assertEqual(agent.execute("calculator", '{"expression": "6*7"}'), "42")

    def test_integer_rules_follow_json_schema(self):
        schema = {"type": "integer"}
        self.assertEqual(validate(2.0, schema), [])  # 1.0-style numbers count as integers
        self.assertTrue(validate(True, schema))     # booleans are not numbers

    def test_agent_selects_tools_and_recovers(self):
        result = agent.run_agent(TASK, **self.kw)
        self.assertEqual((result["stopped"], result["steps"]), ("final_answer", 6))
        self.assertIn("12*7 = 84", result["answer"])
        self.assertIn("get_weather(city=Paris) = 18 C", result["answer"])
        self.assertIn("search_docs(query=context window) = The context window", result["answer"])

    def test_cli_runs(self):
        env = dict(os.environ, LOCAL_MODEL_URL=self.base_url, LOCAL_MODEL="fake-model", PYTHONIOENCODING="utf-8")
        out = subprocess.run([sys.executable, "multi_tool_agent.py"], cwd=HERE, env=env,
                             capture_output=True, encoding="utf-8", check=True).stdout
        self.assertIn("step 2: get_weather", out)
        self.assertIn("'stopped': 'final_answer'", out)


if __name__ == "__main__":
    unittest.main()
