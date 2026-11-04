"""Agent assist (lesson 21): the drafted Context is used only if every number is in the report."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import agent_assist as aa  # noqa: E402
import fake_server_l400  # noqa: E402

REPORT = {"pinned": "fake-model", "candidate": "fake-model:v2", "passed": 19, "total": 20, "pass_rate": 0.95,
          "regressions": ["t14"], "gate_reasons": ["regressions vs baseline: ['t14']"], "redteam_safe": 8,
          "redteam_total": 8, "drift_chi2": 3.92, "drift_df": 1, "drift_alarm": False}


class AgentAssist(unittest.TestCase):
    def test_honest_draft_is_used_decision_stays_code(self):
        server, url = fake_server_l400.start_in_thread()
        try:
            record, bad = aa.assisted_record(REPORT, lambda p: aa.ask(p, url, "fake-model"))
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(bad, [])
        self.assertIn("passed 19/20 golden cases (95%) with 1 regressions", record)
        self.assertIn("Status: REJECT", record)

    def test_wrong_numbers_and_no_model(self):
        record, bad = aa.assisted_record(REPORT, lambda p: "passed 20/20 (100%), 0 regressions. Status: ACCEPT")
        self.assertEqual((bad, "Status: REJECT" in record, "100%" in record), (["100", "0"], True, False))
        self.assertEqual(aa.assisted_record(REPORT, lambda p: None)[1], ["no draft"])


if __name__ == "__main__":
    unittest.main()
