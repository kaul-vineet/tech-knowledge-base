import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "01-setup"))
from fake_model_server import start_in_thread  # noqa: E402
from structured_output import extract_person, validate  # noqa: E402

TEXT = "Maria moved to Lisbon in 2019; she is 34 and works as a nurse."
EXPECTED = {"name": "Maria", "age": 34, "city": "Lisbon"}


class StructuredOutputTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.base_url = start_in_thread()
        cls.kw = {"base_url": cls.base_url, "model": "fake-model"}

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_validator(self):
        self.assertEqual(validate(EXPECTED), [])
        self.assertIn("age must be an integer 0-150", validate({**EXPECTED, "age": "34"}))
        self.assertIn("age must be an integer 0-150", validate({**EXPECTED, "age": True}))
        self.assertIn("missing key 'city'", validate({"name": "Maria", "age": 34}))
        self.assertIn("unexpected key 'x'", validate({**EXPECTED, "x": 1}))
        self.assertEqual(validate([1]), ["top level must be an object"])

    def test_retry_recovers_from_fenced_json(self):
        obj, attempts = extract_person(TEXT, **self.kw)
        self.assertEqual(obj, EXPECTED)
        self.assertEqual(attempts, 2)  # first reply had prose + code fences

    def test_response_format_first_try(self):
        obj, attempts = extract_person(TEXT, use_response_format=True, **self.kw)
        self.assertEqual((obj, attempts), (EXPECTED, 1))

    def test_gives_up_after_budget(self):
        with self.assertRaises(ValueError):
            extract_person(TEXT, max_attempts=1, **self.kw)

    def test_cli_runs(self):
        env = dict(os.environ, LOCAL_MODEL_URL=self.base_url, LOCAL_MODEL="fake-model", PYTHONIOENCODING="utf-8")  # same pipe encoding on Windows
        out = subprocess.run([sys.executable, "structured_output.py"], cwd=HERE, env=env,
                             capture_output=True, encoding="utf-8", check=True).stdout
        self.assertEqual(out.count("'name': 'Maria'"), 2)


if __name__ == "__main__":
    unittest.main()
