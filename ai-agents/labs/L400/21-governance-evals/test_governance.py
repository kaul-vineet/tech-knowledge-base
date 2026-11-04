"""Lesson 21: pinning, the upgrade gate, drift, audit trail, decision record (python -m unittest -v test_governance)."""
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import fake_server_l400  # noqa: E402
import governance as g  # noqa: E402

LOCK = json.loads((HERE / "models.lock.json").read_text(encoding="utf-8"))
TICKETS = [c["ticket"] for c in g.eval_gate.load_cases()]
T14 = "Delivery is late and I need it immediately for an event"


class Governance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.url = fake_server_l400.start_in_thread()
        cls.report = g.evaluate_candidate(cls.url, "fake-model", "fake-model:v2", TICKETS * 10)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_failure_lab_unpinned_alias_changes_answers(self):
        server, url = fake_server_l400.start_in_thread()
        try:
            before = g.classify([T14], url, "fake-model:latest")[0]["priority"]
            server.retag("fake-model:latest", "fake-model:v2")  # a pull: same name, new weights, no code change
            after = g.classify([T14], url, "fake-model:latest")[0]["priority"]
            problems = g.pin_check(url, LOCK)
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual((before, after), ("high", "normal"))
        self.assertEqual(problems, ["fake-model:latest: pinned 1f49242847a4, server has 52d1337ffaca"])

    def test_gate_blocks_a_regression_that_the_pass_rate_hides(self):
        r = self.report
        self.assertEqual((r["passed"], r["pass_rate"], r["regressions"]), (19, 0.95, ["t14"]))
        self.assertEqual((r["redteam_safe"], r["redteam_total"], g.decide_upgrade(r)), (8, 8, "REJECT"))

    def test_drift(self):
        self.assertEqual((self.report["drift_chi2"], self.report["drift_alarm"]), (3.92, False))  # too coarse to see t14
        shipping = [c["ticket"] for c in g.eval_gate.load_cases() if c["expect"]["category"] == "shipping"]
        self.assertEqual(g.category_drift(self.url, "fake-model", TICKETS * 10, TICKETS * 5), (0.0, 4, False))
        self.assertEqual(g.category_drift(self.url, "fake-model", TICKETS * 10, TICKETS * 5 + shipping * 10), (45.71, 4, True))

    def test_audit_chain_detects_tampering(self):
        with tempfile.TemporaryDirectory(dir=HERE) as d:
            log = g.AuditLog(Path(d) / "audit.db")
            for day in range(3):
                log.append(day, "agent", "triage", f"prompt {day}")
            self.assertEqual(log.verify(), (True, None))
            log.db.execute("UPDATE audit SET actor = 'alice' WHERE seq = 2")
            self.assertEqual(log.verify(), (False, 2))
            log.db.close()

    def test_record_is_filled_from_numbers(self):
        text = g.fill_record(self.report)
        self.assertIn("Status: REJECT", text)
        self.assertIn("| 19/20 (95%), regressions 1: ['t14'] |", text)
        self.assertNotIn("{{", text)

    def test_cli(self):
        out = subprocess.run([sys.executable, "governance.py"], cwd=HERE, capture_output=True, text=True,
                             encoding="utf-8", timeout=180).stdout
        self.assertIn("pin check after pull : ['fake-model:latest: pinned 1f49242847a4, server has 52d1337ffaca']", out)
        self.assertIn("decision: REJECT", out)


if __name__ == "__main__":
    unittest.main()
