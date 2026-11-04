"""Milestone 6: chaos campaign + scorecard (code decides) + agent explanation (checked, never decides)."""
import unittest

import agent_assist
import chaos_campaign
import run_capstone


class Campaign(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runs = chaos_campaign.campaign()
        cls.rows = run_capstone.scorecard(cls.runs)

    def test_scorecard_all_pass(self):
        self.assertEqual([r["criterion"] for r in self.rows if not r["pass"]], [])
        self.assertEqual(len(self.rows), 10)
        self.assertEqual(len(self.runs), 27)

    def test_deterministic(self):
        self.assertEqual(chaos_campaign.experiment("everything", 22)[0], chaos_campaign.experiment("everything", 22)[0])

    def test_agent_claims_are_checked_and_its_verdict_ignored(self):
        results = agent_assist.explain([row for row, _ in self.runs], fake=True)
        wrong = sorted(name for name, _, _, ok in results if not ok)
        self.assertEqual(wrong, ["burst", "relay-crash"])  # the fake model's two planted mistakes
        self.assertTrue(all(r["pass"] for r in self.rows))  # unchanged by anything the model said


if __name__ == "__main__":
    unittest.main()
