"""Try it (lesson 3): two small changes, run against the fake server. Run: python -m unittest -v test_try_it_03"""
import copy
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "01-setup"))
from prompt_structure import PROMPTS, chat  # noqa: E402
from fake_model_server import start_in_thread  # noqa: E402


class TryIt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.base_url = start_in_thread()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_1_lowercase_examples(self):
        # in layout C, change the example answers "POSITIVE"/"NEGATIVE" to lowercase
        msgs = copy.deepcopy(PROMPTS["C few-shot+delimiters"])
        for m in msgs:
            if m["role"] == "assistant":
                m["content"] = m["content"].lower()
        out = chat(msgs, self.base_url, "fake-model")
        print("\nobserved:", out)
        self.assertEqual(out, "negative")

    def test_2_drop_system_message(self):
        # in layout C, delete the system message (the only place the task is stated)
        msgs = [m for m in PROMPTS["C few-shot+delimiters"] if m["role"] != "system"]
        out = chat(msgs, self.base_url, "fake-model")
        print("\nobserved:", out)
        self.assertTrue(out.startswith("Hello from fake-model! You said:"))  # no rules left -> no task


if __name__ == "__main__":
    unittest.main(verbosity=2)
