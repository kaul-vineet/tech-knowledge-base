"""Tests for lab 08 agent assist. Run: python -m unittest -v
Runs only against the deterministic fake model server (127.0.0.1, random free port); no real model needed.
"""
import importlib.util
import os
import unittest

import agent_assist
import fake_grover_rule
from local_agent import fake_model_server


class AgentAssistFake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fake_grover_rule.register(fake_model_server)
        cls.server, cls.url = fake_model_server.start_in_thread()
        cls.results = agent_assist.run(cls.url)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_bit_order_mistake_is_rejected(self):
        verdict, reason, k = self.results["single"]
        self.assertEqual((verdict, k), ("REJECT", None))
        self.assertIn("needs ['011']", reason)

    def test_right_oracle_wrong_iterations_is_overridden_by_code(self):
        self.assertEqual(self.results["pair"], ("ACCEPT", "oracle ok; k=2 gives P=0.25, code uses k=1: P=1.0", 1))

    def test_no_amplification_case_is_rejected(self):
        verdict, reason, _ = self.results["even"]
        self.assertEqual(verdict, "REJECT")
        self.assertIn("P(success)=0.5", reason)


class CheckIsDeterministicCode(unittest.TestCase):
    def test_reply_without_proposal(self):
        self.assertEqual(agent_assist.check("No idea.", 3, lambda x: x == 3)[:2], ("REJECT", "no valid JSON proposal"))

    def test_wrong_length_rejected(self):
        self.assertEqual(agent_assist.check('{"marked": ["0011"], "iterations": 2}', 3, lambda x: x == 3)[0], "REJECT")

    def test_correct_unfenced_proposal_accepted(self):
        self.assertEqual(agent_assist.check('{"marked": ["011"], "iterations": 2}', 3, lambda x: x == 3),
                         ("ACCEPT", "oracle ok; k=2 gives P=0.9453", 2))


HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None
if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


@unittest.skipUnless(HAVE_QISKIT, "qiskit not installed (runs in CI)")
class SdkAgreesWithTheJudge(unittest.TestCase):
    def test_overridden_iterations_in_qiskit(self):
        import grover_lab
        self.assertAlmostEqual(grover_lab.success_probability(["101", "110"], 1), 1.0, places=3)
        self.assertAlmostEqual(grover_lab.success_probability(["101", "110"], 2), 0.25, places=3)


if __name__ == "__main__":
    unittest.main()
