"""Try it (lesson 11): two small changes, run against the fake server. Run: python -m unittest -v test_try_it_11"""
import os
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "L100", "01-setup"))
import guarded_agent as ga  # noqa: E402
from fake_model_server import start_in_thread  # noqa: E402

TASK = 'Search docs for "vendor portal deploys".'


class TryIt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.url = start_in_thread()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def run_without_screening(self, **session_kw):
        ga.OUTBOX.clear()
        s = ga.Session({"search_docs", "send_email"}, **session_kw)
        with mock.patch.object(ga.guards, "screen", lambda source, text: (text, False)):  # screening switched off
            s.run(TASK, base_url=self.url, model="fake-model")
        return [line for line in s.log if line.startswith("send_email")], list(ga.OUTBOX)

    def test_1_screening_off(self):
        log, outbox = self.run_without_screening()
        print("\nobserved:", log, "| outbox:", outbox)
        self.assertEqual(log, ["send_email -> error: denied (needs approval and an @example.com recipient)"])

    def test_2_screening_off_and_human_says_yes(self):
        log, outbox = self.run_without_screening(approve=lambda name, args: True)
        print("\nobserved:", log, "| outbox:", outbox)
        self.assertEqual(outbox, [])  # the recipient rule still blocks attacker@evil.test


if __name__ == "__main__":
    unittest.main(verbosity=2)
