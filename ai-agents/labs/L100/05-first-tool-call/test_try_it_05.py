"""Try it (lesson 5): two small changes, run against the fake server. Run: python -m unittest -v test_try_it_05"""
import contextlib
import io
import os
import sys
import unittest

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "01-setup"))
from first_tool_call import ask, chat  # noqa: E402
from fake_model_server import start_in_thread  # noqa: E402


class TryIt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.base_url = start_in_thread()
        cls.kw = {"base_url": cls.base_url, "model": "fake-model"}

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_1_question_needs_no_tool(self):
        # ask a question that needs no clock
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            answer = ask("What is the capital of France?", **self.kw)
        print("\nobserved:", answer, "| tool lines printed:", len(out.getvalue().splitlines()))
        self.assertEqual(out.getvalue(), "")
        self.assertTrue(answer.startswith("Hello from fake-model!"))

    def test_2_skip_assistant_turn(self):
        # delete messages.append(reply): send the tool result without the assistant tool_calls turn
        messages = [{"role": "user", "content": "What time is it?"}]
        call = chat(messages, **self.kw)["tool_calls"][0]
        messages.append({"role": "tool", "tool_call_id": call["id"], "content": "2026-10-28T06:00:00+00:00"})
        with self.assertRaises(requests.HTTPError) as ctx:
            chat(messages, **self.kw)
        body = ctx.exception.response.json()["error"]["message"]
        print(f"\nobserved: HTTP {ctx.exception.response.status_code} - {body}")
        self.assertEqual(ctx.exception.response.status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
