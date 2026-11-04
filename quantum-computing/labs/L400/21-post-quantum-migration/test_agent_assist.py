"""Tests for lab 21 agent assist. Runs only against the deterministic fake model server (127.0.0.1). Run: python -m unittest -v"""
import unittest

import agent_assist
import fake_pqc_rule
import pqc_lab as lab
import solution_scanner as scanner
from local_agent import fake_model_server


class AgentAssistFake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fake_pqc_rule.register(fake_model_server)
        cls.server, cls.url = fake_model_server.start_in_thread()
        cls.results = agent_assist.run(cls.url)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_correct_notes_are_accepted(self):
        self.assertEqual(self.results["draft"], ("ACCEPT", []))

    def test_missing_p1_and_replaced_aes_are_rejected(self):
        self.assertEqual(self.results["summarise"], ("REJECT", ["toy_app/storage.py:10 is symmetric (AES-GCM): keep it, do not replace",
                                                                "P1 item missing: toy_app/sync.py:7"]))

    def test_invented_file_wrong_replacement_and_date_are_rejected(self):
        verdict, notes = self.results["creative"]
        self.assertEqual(verdict, "REJECT")
        self.assertEqual(notes, ["toy_app/payments.py:12 is not in the inventory",
                                 "toy_app/auth.py:11 replacement 'ML-KEM-768' != 'ML-DSA-65'",
                                 "year 2029 is not a NIST IR 8547 date"])


class CheckIsCode(unittest.TestCase):
    def test_empty_reply_misses_every_p1(self):
        verdict, notes = agent_assist.check("No idea.", lab.plan(scanner.scan()))
        self.assertEqual((verdict, len(notes)), ("REJECT", 2))


if __name__ == "__main__":
    unittest.main()
