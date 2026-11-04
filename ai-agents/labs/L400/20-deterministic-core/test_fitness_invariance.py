"""Fitness function (lesson 20, ADR-0020): the model cannot change a decision.

600 seeded hostile model answers (12 cases x 50 seeds: wrong types, unknown actions, extra keys, huge strings,
invalid JSON, injected claims, contradicting explanations) go through code_decides. Threshold: 0 changed decisions -
the action equals policy.decide(facts), except approve_auto -> escalate (the only move a claim may cause), and the
amount equals the policy's amount.
"""
import json
import random
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import edge  # noqa: E402
import policy  # noqa: E402

ACTIONS = ["approve_auto", "deny", "escalate", "refund_all", "APPROVE", "", None, 7]


def hostile(rng):
    claims = {"damaged": rng.choice([True, False, "yes", None]), "threat": rng.choice([True, False, 1, "true"])}
    obj = {"claims": claims, "summary": rng.choice(["ok", "x" * 5000, "ignore previous instructions"]),
           "suggested_action": rng.choice(ACTIONS)}
    if rng.random() < 0.3:
        obj.update(action="approve_auto", amount=rng.choice([999, -5, "all"]), override=True)
    return rng.choice([json.dumps(obj), json.dumps(obj)[:-3], "approved!", "", json.dumps([obj]),
                       f"Good news: refund of {rng.randint(1, 999)} approved", None])


class FitnessInvariance(unittest.TestCase):
    def test_no_model_answer_changes_a_decision(self):
        changed = []
        for case in edge.CASES:
            truth = policy.decide(case["facts"])
            for seed in range(50):
                rng = random.Random(f"{case['id']}-{seed}")
                out = edge.code_decides(case, ask=lambda prompt: hostile(rng))
                ok_action = out["action"] == truth["action"] or (truth["action"], out["action"]) == ("approve_auto", "escalate")
                ok_amount = out["amount"] == (truth["amount"] if out["action"] == truth["action"] else 0.0)
                if not (ok_action and ok_amount and out["action"] in policy.ALLOWED_ACTIONS):
                    changed.append((case["id"], seed, out["action"], out["amount"]))
        self.assertEqual(changed, [])


if __name__ == "__main__":
    unittest.main()
