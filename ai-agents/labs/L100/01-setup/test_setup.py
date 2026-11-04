import json
import os
import subprocess
import sys
import unittest

import requests

from check_endpoint import check
from fake_model_server import start_in_thread

HERE = os.path.dirname(os.path.abspath(__file__))


class SetupTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.base_url = start_in_thread()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_check_endpoint(self):
        ids, reply = check(self.base_url, "fake-model")
        self.assertEqual(ids, ["fake-model"])
        self.assertIn("ready", reply)

    def test_cli_runs(self):
        env = dict(os.environ, LOCAL_MODEL_URL=self.base_url, LOCAL_MODEL="fake-model", PYTHONIOENCODING="utf-8")  # same pipe encoding on Windows
        out = subprocess.run([sys.executable, "check_endpoint.py"], cwd=HERE, env=env,
                             capture_output=True, encoding="utf-8", check=True).stdout
        self.assertIn("models served: ['fake-model']", out)

    def test_cli_old_env_names_still_work(self):
        env = {k: v for k, v in os.environ.items() if k not in ("LOCAL_MODEL_URL", "LOCAL_MODEL")}
        env.update(BASE_URL=self.base_url, MODEL="fake-model", PYTHONIOENCODING="utf-8")  # fallback names only
        out = subprocess.run([sys.executable, "check_endpoint.py"], cwd=HERE, env=env,
                             capture_output=True, encoding="utf-8", check=True).stdout
        self.assertIn("models served: ['fake-model']", out)
        self.assertNotIn("WARNING", out)

    def test_rejects_bad_request(self):
        r = requests.post(f"{self.base_url}/chat/completions", json={"model": "fake-model"}, timeout=5)
        self.assertEqual(r.status_code, 400)
        self.assertIn("error", r.json())

    def test_tool_call_shape(self):
        tools = [{"type": "function", "function": {"name": "calculator", "parameters": {"type": "object"}}}]
        r = requests.post(f"{self.base_url}/chat/completions", timeout=5, json={
            "model": "fake-model", "tools": tools,
            "messages": [{"role": "user", "content": "What is 2+3?"}]}).json()
        choice = r["choices"][0]
        self.assertEqual(choice["finish_reason"], "tool_calls")
        call = choice["message"]["tool_calls"][0]
        self.assertEqual(call["function"]["name"], "calculator")
        self.assertEqual(json.loads(call["function"]["arguments"]), {"expression": "2+3"})


if __name__ == "__main__":
    unittest.main()
