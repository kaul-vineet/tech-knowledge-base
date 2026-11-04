import os
import re
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "01-setup"))
from fake_model_server import start_in_thread  # noqa: E402
from first_tool_call import TOOLS, ask, get_time, run_tool  # noqa: E402

ISO = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+00:00"


class FirstToolCallTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.base_url = start_in_thread()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_tool_definition(self):
        fn = TOOLS[0]["function"]
        self.assertEqual((TOOLS[0]["type"], fn["name"]), ("function", "get_time"))
        self.assertEqual(fn["parameters"]["type"], "object")

    def test_get_time_format(self):
        self.assertRegex(get_time(), ISO)

    def test_run_tool_accepts_string_or_dict_args(self):
        self.assertRegex(run_tool({"function": {"name": "get_time", "arguments": "{}"}}), ISO)
        self.assertRegex(run_tool({"function": {"name": "get_time", "arguments": {}}}), ISO)

    def test_unknown_tool_is_not_executed(self):
        out = run_tool({"function": {"name": "delete_files", "arguments": "{}"}})
        self.assertTrue(out.startswith("error: unknown tool"))

    def test_round_trip(self):
        answer = ask("What time is it?", base_url=self.base_url, model="fake-model")
        self.assertRegex(answer, r"^Final answer: get_time\(\) = " + ISO)

    def test_no_tool_needed(self):
        answer = ask("Say hi", base_url=self.base_url, model="fake-model")
        self.assertIn("Say hi", answer)

    def test_cli_runs(self):
        env = dict(os.environ, LOCAL_MODEL_URL=self.base_url, LOCAL_MODEL="fake-model", PYTHONIOENCODING="utf-8")  # same pipe encoding on Windows
        out = subprocess.run([sys.executable, "first_tool_call.py"], cwd=HERE, env=env,
                             capture_output=True, encoding="utf-8", check=True).stdout
        self.assertTrue(re.search("model requested: get_time", out))


if __name__ == "__main__":
    unittest.main()
