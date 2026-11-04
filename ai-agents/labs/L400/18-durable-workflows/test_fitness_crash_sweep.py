"""Fitness function (lesson 18, ADR-0018): a crash at ANY step resumes without a duplicate side effect.

For each of the 12 crash points the workflow is killed once, restarted from the SQLite file and driven to the end.
Thresholds: status done, exactly 1 refund, exactly 1 refund_done outbox row, at most 2 model calls (one repeat is
allowed only when the crash hit between the model's answer and the checkpoint - a cost, not a side effect).
"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent), str(HERE.parent.parent / "L300" / "15-safe-tool-execution")]
import fake_server_l400  # noqa: E402
import harness  # noqa: E402


class FitnessCrashSweep(unittest.TestCase):
    def test_every_crash_point(self):
        server, url = fake_server_l400.start_in_thread()
        try:
            rows = harness.sweep("durable", url, server=server)
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(len(rows), 12)
        for r in rows:
            self.assertEqual((r["status"], r["refunds"], r["notifications"]), ("done", 1, 1), r["crash_at"])
            self.assertLessEqual(r["model_calls"], 2 if r["crash_at"] == "after_model:propose" else 1, r["crash_at"])


if __name__ == "__main__":
    unittest.main()
