"""Lesson 18: failure lab (crash after the refund), long-running approval, replay (python -m unittest -v test_durable)."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent), str(HERE.parent.parent / "L300" / "15-safe-tool-execution")]
import durable  # noqa: E402
import fake_server_l400  # noqa: E402
import payments_service  # noqa: E402
from harness import drive  # noqa: E402
from naive_workflow import run_naive  # noqa: E402


class Durable(unittest.TestCase):
    def setUp(self):
        self.server, self.url = fake_server_l400.start_in_thread()
        self.pay, self.pay_url = payments_service.start_in_thread()
        self.tmp = tempfile.TemporaryDirectory(dir=HERE)
        self.db = Path(self.tmp.name) / "wf.db"

    def tearDown(self):
        for s in (self.server, self.pay):
            s.shutdown()
            s.server_close()
        self.tmp.cleanup()

    def refunds(self):
        return len(requests.get(f"{self.pay_url}/refunds", timeout=5).json())

    def engine(self, crash=(), **kw):
        return durable.Engine(self.db, self.pay_url, self.url, "fake-model", crash_at=crash, **kw)

    def finish(self, crash, **kw):
        self.engine().start("wf-1", "A-1001")
        status, crashes, eng = drive(lambda c: self.engine(c, **kw), "wf-1", crash_at=crash)
        eng.db.close()
        return status, crashes

    def test_failure_lab_naive_refunds_twice(self):
        self.assertEqual(run_naive("A-1001", self.pay_url, self.url, "fake-model", crash_at={"after_effect:refund"}), 2)
        self.assertEqual(self.refunds(), 2)

    def test_failure_lab_checkpoint_without_key_refunds_twice(self):
        self.assertEqual(self.finish({"after_effect:refund"}, use_keys=False), ("done", ["after_effect:refund"]))
        self.assertEqual(self.refunds(), 2)

    def test_failure_lab_durable_refunds_once(self):
        self.assertEqual(self.finish({"after_effect:refund"}), ("done", ["after_effect:refund"]))
        eng = self.engine()
        replayed = eng.db.execute("SELECT data FROM history WHERE step = 'refund' AND event = 'completed'").fetchone()[0]
        outbox = eng.db.execute("SELECT kind FROM outbox").fetchall()
        eng.db.close()
        self.assertEqual((self.refunds(), '"replayed": true' in replayed, outbox), (1, True, [("refund_done",)]))

    def test_long_running_approval_survives_restarts(self):
        clock = durable.Clock(0)
        eng = self.engine(clock=clock)
        eng.start("wf-1", "A-1001")
        self.assertEqual(eng.run("wf-1"), "waiting")
        eng.db.close()
        clock.hours = 30  # a day and a half later, a new process
        eng = self.engine(clock=clock)
        self.assertEqual(eng.run("wf-1"), "waiting")
        eng.signal("wf-1", "approve", "alice")
        self.assertEqual((eng.run("wf-1"), self.refunds()), ("done", 1))
        self.assertEqual(eng.db.execute("SELECT ts FROM history WHERE event = 'signal:approve'").fetchone()[0], 30)
        eng.db.close()

    def test_replay_does_not_call_the_model_again(self):
        eng = self.engine()
        eng.start("wf-1", "A-1001")
        eng.run("wf-1")
        calls = self.server.stats["requests"]
        eng.db.close()
        eng = self.engine()
        self.assertEqual((eng.run("wf-1"), self.server.stats["requests"]), ("waiting", calls))
        eng.db.close()

    def test_reject_moves_no_money(self):
        eng = self.engine()
        eng.start("wf-1", "A-1001")
        eng.run("wf-1")
        eng.signal("wf-1", "reject", "bob")
        self.assertEqual((eng.run("wf-1"), eng.run("wf-1"), self.refunds()), ("rejected", "rejected", 0))
        eng.db.close()

    def test_cli(self):
        env = {**os.environ, "LOCAL_MODEL_URL": self.url, "LOCAL_MODEL": "fake-model"}
        out = subprocess.run([sys.executable, "durable.py"], cwd=HERE, env=env, capture_output=True, text=True,
                             encoding="utf-8", timeout=120).stdout
        self.assertIn("naive, crash after the refund : 2 -> 2 refunds", out)
        self.assertIn("durable, same crash          : done ['after_effect:refund'] -> 1 refund", out)


if __name__ == "__main__":
    unittest.main()
