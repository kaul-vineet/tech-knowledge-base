"""Try it (lesson 4): two small changes, run against the fake server. Run: python -m unittest -v test_try_it_04"""
import contextlib
import io
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "01-setup"))
from structured_output import extract_person  # noqa: E402
from fake_model_server import start_in_thread  # noqa: E402

TEXT = "Maria moved to Lisbon in 2019; she is 34 and works as a nurse."


class TryIt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.base_url = start_in_thread()
        cls.kw = {"base_url": cls.base_url, "model": "fake-model"}

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_1_one_attempt_only(self):
        # change max_attempts=3 to max_attempts=1 in prompt-only mode
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(ValueError) as ctx:
            extract_person(TEXT, max_attempts=1, **self.kw)
        print("\nobserved: ValueError:", ctx.exception)
        self.assertEqual(str(ctx.exception), "no valid JSON after 1 attempts")

    def test_2_text_without_age(self):
        # remove "she is 34" from the input text
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(ValueError):
            extract_person("Maria moved to Lisbon in 2019 and works as a nurse.", **self.kw)
        lines = out.getvalue().strip().splitlines()
        print("\nobserved:", " | ".join(s.strip() for s in lines))
        self.assertEqual(len(lines), 3)
        self.assertIn("age must be an integer 0-150", lines[-1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
