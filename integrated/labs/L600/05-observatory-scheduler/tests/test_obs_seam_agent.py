"""SEAM ai-agents <-> scheduler: the agent proposes text; parser + validator decide; explanations are gated."""
import unittest

from tests import _lab

import agent_plan  # noqa: E402
import validator  # noqa: E402
from timeutil import UtcInstant  # noqa: E402


class AgentPlanGate(unittest.TestCase):
    def setUp(self):
        self.r = _lab.night()

    def decide(self, text):
        return agent_plan.decide(text, self.r["local"], self.r["reqs"], self.r["slots"])

    def test_naive_time_is_rejected_not_guessed(self):
        v = self.decide("PLAN Vega 2026-11-19T18:50")
        self.assertFalse(v["agent_ok"])
        self.assertIn("ISO 8601", v["reasons"][0])

    def test_below_horizon_target_is_rejected(self):
        v = self.decide("PLAN Sirius 2026-11-19T13:20:00Z")
        self.assertTrue(any("airmass inf" in x for x in v["reasons"]))

    def test_unknown_target_overlap_and_off_grid_are_rejected(self):
        v = self.decide("PLAN Rigel 2026-11-19T15:00:00Z\nPLAN Vega 2026-11-19T13:20:00Z\n"
                        "PLAN Deneb 2026-11-19T13:35:00Z")
        text = " | ".join(v["reasons"])
        for phrase in ("not a requested target", "overlap", "off the 10-min slot grid"):
            self.assertIn(phrase, text)

    def test_valid_plan_in_utc_is_adopted_when_it_promises_as_much(self):
        text = "\n".join(f"PLAN {x['target']} {x['start_utc']}" for x in self.r["local_rows"])
        self.assertEqual(self.decide(text)["adopted"], "agent")

    def test_valid_but_worse_plan_loses_to_the_optimiser(self):
        text = "\n".join(f"PLAN {x['target']} {x['start_utc']}" for x in self.r["greedy_rows"])
        v = self.decide(text)
        self.assertTrue(v["agent_ok"])
        self.assertEqual(v["adopted"], "optimiser")

    def test_validator_refuses_untyped_starts(self):
        out = validator.validate([{"target": "Vega", "start": "2026-11-19T13:20:00Z"}])
        self.assertIn("not a UtcInstant", out[0])
        self.assertTrue(isinstance(self.r["slots"][0].utc, UtcInstant))


class ExplanationGate(unittest.TestCase):
    def test_invented_number_or_target_is_blocked(self):
        r = _lab.night()
        facts = agent_plan.explain_facts(r)
        good = f"Expected value {facts['local_value']} vs {facts['greedy_value']}."
        self.assertTrue(agent_plan.checked_explanation(good, facts, r["reqs"])[0])
        self.assertFalse(agent_plan.checked_explanation("Expected value 12.0, guaranteed.", facts, r["reqs"])[0])
        self.assertFalse(agent_plan.checked_explanation("Rigel fits in the gap.", facts, r["reqs"])[0])


if __name__ == "__main__":
    unittest.main()
