"""Milestone 3 (fitness: policy decides): severity/actions come from code; proposals are validated, never obeyed."""
import inspect
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import policy  # noqa: E402
import triage  # noqa: E402
from capstone_fixture import Env, INCIDENTS  # noqa: E402

GOLDEN = {g["id"]: g["expect"] for g in map(json.loads, (HERE / "golden_incidents.jsonl").read_text(encoding="utf-8").splitlines())}


class M3Policy(unittest.TestCase):
    def test_policy_table_matches_golden(self):
        for iid, inc in INCIDENTS.items():
            d = policy.decide(inc["metrics"], inc["deploy_age_min"])
            self.assertEqual((d["severity"], d["actions"]), (GOLDEN[iid]["severity"], GOLDEN[iid]["actions"]), iid)
        self.assertEqual(list(inspect.signature(policy.decide).parameters), ["metrics", "deploy_age_min"])  # no model input

    def test_injection_in_logs_changes_nothing(self):
        env = Env()
        try:
            status, done = env.agent().handle(INCIDENTS["INC-6"])
            effects = env.effects_list()
        finally:
            env.close()
        self.assertEqual(done["propose"]["proposal"]["proposed_severity"], "SEV1")  # the model obeyed the log line...
        self.assertEqual(done["propose"]["problems"], ["unknown action delete_cluster"])
        self.assertEqual((done["decide"]["severity"], [e["action"] for e in effects]), ("SEV3", ["open_ticket"]))  # ...code did not
        self.assertTrue(done["decide"]["explanation"].startswith("Severity SEV3 by policy"))

    def test_explanation_check(self):
        d = {"severity": "SEV3", "actions": ["open_ticket"]}
        self.assertTrue(triage.explanation_ok("Likely slow queries. Proposed SEV3: open_ticket.", d))
        self.assertFalse(triage.explanation_ok("Proposed SEV1: page_oncall, delete_cluster.", d))


if __name__ == "__main__":
    unittest.main()
