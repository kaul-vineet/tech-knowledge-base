"""Fitness function (lesson 21, ADR-0021): governance stays enforceable.

Thresholds: the lock matches the serving digest; a candidate with any golden regression is REJECTED while an
equivalent candidate is ACCEPTED (the gate is neither always-yes nor always-no); the audit chain verifies and a
single edited row is detected; a 2x shipping surge raises the drift alarm at alpha 0.01.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import fake_server_l400  # noqa: E402
import governance as g  # noqa: E402


class FitnessGovernance(unittest.TestCase):
    def test_controls_hold(self):
        server, url = fake_server_l400.start_in_thread()
        tickets = [c["ticket"] for c in g.eval_gate.load_cases()]
        shipping = [c["ticket"] for c in g.eval_gate.load_cases() if c["expect"]["category"] == "shipping"]
        try:
            self.assertEqual(g.pin_check(url, json.loads((HERE / "models.lock.json").read_text(encoding="utf-8"))), [])
            self.assertEqual(g.decide_upgrade(g.evaluate_candidate(url, "fake-model", "fake-model:v2", tickets * 5)), "REJECT")
            self.assertEqual(g.decide_upgrade(g.evaluate_candidate(url, "fake-model", "fake-large", tickets * 5)), "ACCEPT")
            self.assertTrue(g.category_drift(url, "fake-model", tickets * 10, tickets * 5 + shipping * 10)[2])
        finally:
            server.shutdown()
            server.server_close()
        with tempfile.TemporaryDirectory(dir=HERE) as d:
            log = g.AuditLog(Path(d) / "audit.db")
            for day in range(5):
                log.append(day, "agent", "triage", f"p{day}")
            ok = log.verify()
            log.db.execute("UPDATE audit SET event = 'deleted' WHERE seq = 4")
            self.assertEqual((ok, log.verify()), ((True, None), (False, 4)))
            log.db.close()


if __name__ == "__main__":
    unittest.main()
