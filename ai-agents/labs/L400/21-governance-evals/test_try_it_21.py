"""Try it (lesson 21): a pass-rate-only gate; edit one audit row."""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import fake_server_l400  # noqa: E402
import governance as g  # noqa: E402


class TryIt(unittest.TestCase):
    def test_1_pass_rate_only_gate(self):
        server, url = fake_server_l400.start_in_thread()
        try:
            r = g.evaluate_candidate(url, "fake-model", "fake-model:v2", [c["ticket"] for c in g.eval_gate.load_cases()] * 5)
        finally:
            server.shutdown()
            server.server_close()
        r["gate_reasons"] = [x for x in r["gate_reasons"] if not x.startswith("regressions")]  # keep only the 95 % bar
        print(f"\nobserved: pass rate {r['pass_rate']:.0%} -> {g.decide_upgrade(r)} (t14 'immediately' is now normal priority)")
        self.assertEqual(g.decide_upgrade(r), "ACCEPT")

    def test_2_edit_one_audit_row(self):
        with tempfile.TemporaryDirectory(dir=HERE) as d:
            log = g.AuditLog(Path(d) / "audit.db")
            for day, actor in enumerate(["agent", "agent", "alice", "executor"]):
                log.append(day, actor, "step", f"text {day}")
            log.db.execute("UPDATE audit SET actor = 'bob' WHERE seq = 3")
            result = log.verify()
            log.db.close()
        print(f"\nobserved: verify() -> {result}")
        self.assertEqual(result, (False, 3))


if __name__ == "__main__":
    unittest.main(verbosity=2)
