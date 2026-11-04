"""Try it (lesson 8): two small changes, run against the fake server. Run: python -m unittest -v test_try_it_08"""
import contextlib
import io
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "L100", "01-setup"))
import multi_tool_agent as agent  # noqa: E402
from fake_model_server import start_in_thread  # noqa: E402

TASK = 'Compute 12*7, tell me the weather in Paris in kelvin, and search docs for "context window" top 50.'


class TryIt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.base_url = start_in_thread()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_1_fahrenheit_needs_no_retry(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = agent.run_agent(TASK.replace("kelvin", "fahrenheit"), base_url=self.base_url, model="fake-model")
        line = [ln for ln in out.getvalue().splitlines() if "get_weather" in ln][0]
        print("\nobserved:", line, "| steps:", result["steps"])
        self.assertEqual(line, 'step 2: get_weather({"city": "Paris", "unit": "fahrenheit"}) -> 64 F')
        self.assertEqual(result["steps"], 5)

    def test_2_raise_top_k_maximum(self):
        schema = agent.REGISTRY["search_docs"]["schema"]["properties"]["top_k"]
        old = schema["maximum"]
        schema["maximum"] = 50
        try:
            result = agent.execute("search_docs", '{"query": "context window", "top_k": 50}')
        finally:
            schema["maximum"] = old
        print("\nobserved:", result)
        self.assertEqual(result.count(" | "), 2)  # all 3 notes come back: the limit was the only guard


if __name__ == "__main__":
    unittest.main(verbosity=2)
