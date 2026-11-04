"""M3: policy as code (tools.rego via rego_lite) + human approval in the secure host."""
import unittest

import _lab
import scenarios as sc
from policy_engine import RegoPolicy

CASES = [  # (side_effect, risk, scope_ok, args_valid, provenance_ok) -> (allowed, needs_approval)
    ((False, "low", True, True, False), (True, False)),
    ((False, "low", False, True, True), (False, False)),
    ((True, "low", True, True, True), (True, False)),
    ((True, "low", True, True, False), (False, False)),
    ((True, "high", True, True, True), (True, True)),
    ((True, "high", True, False, True), (False, True)),
    ((True, "high", False, True, True), (False, True)),
]


class TestPolicyHost(unittest.TestCase):
    def test_policy_table(self):
        pdp = RegoPolicy()
        for (se, risk, scope, valid, prov), expect in CASES:
            d = pdp.decide({"tool": {"name": "t", "side_effect": se, "risk": risk}, "scope_ok": scope,
                            "args_valid": valid, "provenance_ok": prov})
            self.assertEqual((d["allowed"], d["needs_approval"]), expect, (se, risk, scope, valid, prov))

    def test_deny_by_default_on_empty_input(self):
        self.assertFalse(RegoPolicy().decide({})["allowed"])

    def test_s1_read_only_call_runs(self):
        env, answer = sc.s1_benign(_lab.url(), _lab.registry())
        self.assertEqual([(c["tool"], c["executed"]) for c in env.host.calls], [("search_docs", True)])
        self.assertIn('<untrusted_data source="tool:search_docs">', answer)

    def test_s3_in_scope_side_effect_with_user_provenance(self):
        env, _ = sc.s3_in_scope_effect(_lab.url(), _lab.registry())
        self.assertEqual(env.world.effects, [("save_memory", {"note": "the rollout is on Friday"})])

    def test_s4_high_risk_waits_for_a_human(self):
        ok, _ = sc.s4_approval(_lab.registry(), approve=True)
        no, _ = sc.s4_approval(_lab.registry(), approve=False)
        self.assertEqual(len(ok.world.effects), 1)
        self.assertEqual(no.world.effects, [])
        self.assertEqual(ok.approver.seen[0]["args"]["to"], "alice@corp.example")  # the human sees the exact call


if __name__ == "__main__":
    unittest.main()
