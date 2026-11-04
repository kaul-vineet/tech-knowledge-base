"""Try it (lesson 1): two small changes, run against the fake server. Run: python -m unittest -v test_try_it_01"""
import contextlib
import io
import os
import sys
import unittest

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_endpoint  # noqa: E402
from fake_model_server import start_in_thread  # noqa: E402


class TryIt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.base_url = start_in_thread()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_1_model_not_pulled(self):
        # change LOCAL_MODEL to a name the server does not list
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            check_endpoint.check(self.base_url, "not-pulled")
        print("\nobserved:", out.getvalue().splitlines()[1])
        self.assertIn("WARNING: 'not-pulled' not listed", out.getvalue())
        self.assertIn("chat reply: Hello from fake-model!", out.getvalue())

    def test_2_base_url_without_v1(self):
        # drop "/v1" from LOCAL_MODEL_URL
        with self.assertRaises(requests.HTTPError) as ctx:
            check_endpoint.check(self.base_url[:-3], "fake-model")
        print("\nobserved:", str(ctx.exception).split(" for url")[0])
        self.assertEqual(ctx.exception.response.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
