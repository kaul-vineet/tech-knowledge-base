"""Tests for lab 15 agent assist. Run: python -m unittest -v
Runs only against the deterministic fake model server (127.0.0.1, random free port); no real model needed.
"""
import unittest

import agent_assist
import fake_vqe_rule
from local_agent import fake_model_server

SUMMARY = {"iters": 100, "best_energy_est": -1.77348, "final_energy_est": -0.27276, "evals": 900,
           "tail_energy_std": 0.3912, "tail_grad_norm_median": 15.5125}


class AgentAssistFake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fake_vqe_rule.register(fake_model_server)
        cls.server, cls.url = fake_model_server.start_in_thread()
        cls.results = agent_assist.run(cls.url)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_good_proposal_is_accepted_after_code_runs_it(self):
        self.assertEqual(self.results["diagnose"], ("ACCEPT", ["code ran spsa @ 1000 shots: error 0.0064"]))

    def test_hallucinated_number_and_wrong_diagnosis_are_rejected(self):
        verdict, notes = self.results["report"]
        self.assertEqual(verdict, "REJECT")
        self.assertIn("not in the log", notes[0])
        self.assertIn("!= code rule 'shot_noise'", notes[1])

    def test_over_budget_proposal_is_not_run(self):
        verdict, notes = self.results["costly"]
        self.assertEqual(verdict, "REJECT")
        self.assertIn("> budget", notes[-1])


class CheckIsDeterministicCode(unittest.TestCase):
    def test_code_diagnosis(self):
        self.assertEqual(agent_assist.code_diagnosis(SUMMARY), "shot_noise")
        self.assertEqual(agent_assist.code_diagnosis({**SUMMARY, "tail_energy_std": 0.001}), "converged")

    def test_reply_without_proposal(self):
        self.assertEqual(agent_assist.check("No idea.", SUMMARY), ("REJECT", ["no valid proposal"]))

    def test_unknown_setting_is_rejected(self):
        reply = '{"diagnosis": "shot_noise", "best_energy": -1.77348, "proposal": {"optimizer": "spsa", "shots": 1000, "exec": "rm -rf"}}'
        self.assertEqual(agent_assist.check(reply, SUMMARY)[0], "REJECT")


if __name__ == "__main__":
    unittest.main()
