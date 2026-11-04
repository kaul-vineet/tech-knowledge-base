import os
import subprocess
import sys
import unittest

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "01-setup"))
from fake_model_server import start_in_thread  # noqa: E402
from call_model import chat  # noqa: E402


class CallModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.base_url = start_in_thread()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_reply_shape(self):
        data = chat([{"role": "user", "content": "Say hello"}], base_url=self.base_url, model="fake-model")
        choice = data["choices"][0]
        self.assertEqual(choice["message"]["role"], "assistant")
        self.assertEqual(choice["finish_reason"], "stop")
        self.assertIn("Say hello", choice["message"]["content"])
        self.assertIn("total_tokens", data["usage"])

    def test_http_error_raises(self):
        with self.assertRaises(requests.HTTPError):
            chat([], base_url=self.base_url, model="fake-model")  # empty messages -> 400

    def test_urllib_variant_matches(self):
        import call_model_urllib
        msgs = [{"role": "user", "content": "Say hello"}]
        a = chat(msgs, base_url=self.base_url, model="fake-model")
        b = call_model_urllib.chat(msgs, base_url=self.base_url, model="fake-model")
        self.assertEqual(a["choices"], b["choices"])

    def test_cli_runs(self):
        env = dict(os.environ, LOCAL_MODEL_URL=self.base_url, LOCAL_MODEL="fake-model", PYTHONIOENCODING="utf-8")  # same pipe encoding on Windows
        out = subprocess.run([sys.executable, "call_model.py"], cwd=HERE, env=env,
                             capture_output=True, encoding="utf-8", check=True).stdout
        self.assertIn("finish_reason: stop", out)


if __name__ == "__main__":
    unittest.main()
