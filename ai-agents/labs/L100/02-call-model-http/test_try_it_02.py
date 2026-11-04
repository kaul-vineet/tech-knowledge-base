"""Try it (lesson 2): two small changes, run against the fake server. Run: python -m unittest -v test_try_it_02"""
import os
import sys
import unittest

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "01-setup"))
from call_model import chat  # noqa: E402
from fake_model_server import start_in_thread  # noqa: E402


class TryIt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.base_url = start_in_thread()
        cls.kw = {"base_url": cls.base_url, "model": "fake-model"}

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_1_resend_history(self):
        # send the follow-up alone, then with the earlier turns, and compare prompt_tokens
        first = chat([{"role": "user", "content": "Hi"}], **self.kw)
        alone = chat([{"role": "user", "content": "What did I just say?"}], **self.kw)
        history = [{"role": "user", "content": "Hi"}, first["choices"][0]["message"],
                   {"role": "user", "content": "What did I just say?"}]
        full = chat(history, **self.kw)
        a, f = alone["usage"]["prompt_tokens"], full["usage"]["prompt_tokens"]
        print(f"\nobserved: alone prompt_tokens={a}, with history prompt_tokens={f} ({len(history)} messages)")
        self.assertEqual((a, f), (5, 12))

    def test_2_no_user_message(self):
        # change the only message's role from "user" to "system"
        with self.assertRaises(requests.HTTPError) as ctx:
            chat([{"role": "system", "content": "Say hello"}], **self.kw)
        body = ctx.exception.response.json()["error"]["message"]
        print(f"\nobserved: HTTP {ctx.exception.response.status_code} - {body}")
        self.assertEqual(ctx.exception.response.status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
