"""M6: the agent explains anomalies (fake model server only); code decides which explanations count."""
import unittest

import agent_explain

ANOMALIES = [{"id": "A1", "rule": "unwrap_burst", "seq": 30, "summary": "mallory: 6 unwraps in 60 s"},
             {"id": "A2", "rule": "bad_signature", "seq": 10, "summary": "entry content does not match its signature"}]


class TestM6(unittest.TestCase):
    def test_only_reported_anomalies_accepted(self):
        rows = {r["id"]: r["verdict"] for r in agent_explain.explain(ANOMALIES)}
        self.assertEqual(rows["A1"], "ACCEPTED")
        self.assertEqual(rows["A2"], "ACCEPTED")
        self.assertTrue(rows["A99"].startswith("REJECTED"))

    def test_prompt_gate_refuses_secret(self):
        leaky = [{"id": "A1", "rule": "x", "seq": 1, "summary": "-----BEGIN PRIVATE KEY----- in a field"}]
        with self.assertRaises(ValueError):
            agent_explain.prompt_for(leaky)


if __name__ == "__main__":
    unittest.main()
