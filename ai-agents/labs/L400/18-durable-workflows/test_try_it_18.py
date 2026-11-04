"""Try it (lesson 18): crash between the model's answer and the checkpoint; a double-clicked approval."""
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


class TryIt(unittest.TestCase):
    def setUp(self):
        self.server, self.url = fake_server_l400.start_in_thread()
        self.pay, self.pay_url = payments_service.start_in_thread()

    def tearDown(self):
        for s in (self.server, self.pay):
            s.shutdown()
            s.server_close()

    def test_1_crash_after_model_answer(self):
        with tempfile.TemporaryDirectory(dir=HERE) as d:
            make = lambda c: durable.Engine(Path(d) / "wf.db", self.pay_url, self.url, "fake-model", crash_at=c)
            make(()).start("wf-1", "A-1001")
            status, crashes, eng = drive(make, "wf-1", crash_at={"after_model:propose"})
            eng.db.close()
        refunds = len(requests.get(f"{self.pay_url}/refunds", timeout=5).json())
        print(f"\nobserved: {status}, crashes {crashes}, model calls {self.server.stats['requests']}, refunds {refunds}")
        self.assertEqual((self.server.stats["requests"], refunds), (2, 1))

    def test_2_double_click_approve(self):
        with tempfile.TemporaryDirectory(dir=HERE) as d:
            eng = durable.Engine(Path(d) / "wf.db", self.pay_url, self.url, "fake-model")
            eng.start("wf-1", "A-1001")
            eng.run("wf-1")
            eng.signal("wf-1", "approve", "alice")
            eng.signal("wf-1", "approve", "alice")
            status = eng.run("wf-1")
            signals = eng.db.execute("SELECT COUNT(*) FROM history WHERE event = 'signal:approve'").fetchone()[0]
            eng.db.close()
        refunds = len(requests.get(f"{self.pay_url}/refunds", timeout=5).json())
        print(f"\nobserved: {status}, approve signals stored {signals}, refunds {refunds}")
        self.assertEqual((signals, refunds), (1, 1))


if __name__ == "__main__":
    unittest.main(verbosity=2)
