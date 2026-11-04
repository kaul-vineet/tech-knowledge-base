import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "01-setup"))
from fake_model_server import start_in_thread  # noqa: E402
from prompt_structure import PROMPTS, run_all  # noqa: E402


class PromptStructureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.base_url = start_in_thread()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_prompt_shapes(self):
        roles = [m["role"] for m in PROMPTS["C few-shot+delimiters"]]
        self.assertEqual(roles, ["system", "user", "assistant", "user", "assistant", "user"])
        self.assertTrue(PROMPTS["C few-shot+delimiters"][-1]["content"].startswith("<review>"))

    def test_outputs_differ_by_structure(self):
        out = run_all(self.base_url, "fake-model")
        self.assertGreater(len(out["A user-only"].split()), 5)    # chatty
        self.assertEqual(out["B system+user"], "negative")          # one label
        self.assertEqual(out["C few-shot+delimiters"], "NEGATIVE")  # follows example format

    def test_cli_runs(self):
        env = dict(os.environ, LOCAL_MODEL_URL=self.base_url, LOCAL_MODEL="fake-model", PYTHONIOENCODING="utf-8")  # same pipe encoding on Windows
        out = subprocess.run([sys.executable, "prompt_structure.py"], cwd=HERE, env=env,
                             capture_output=True, encoding="utf-8", check=True).stdout
        self.assertEqual(len(out.strip().splitlines()), 3)


if __name__ == "__main__":
    unittest.main()
