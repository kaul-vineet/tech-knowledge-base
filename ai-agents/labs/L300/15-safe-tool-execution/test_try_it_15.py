"""Try it (lesson 15): two changes. Run: python -m unittest -v test_try_it_15"""
import sys
import tempfile
import unittest
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import payments_service  # noqa: E402
import safe_tools as st  # noqa: E402
from fake_server_l300 import start_in_thread  # noqa: E402


class FreshKeyGate(st.ToolGate):
    """The mistake: a NEW idempotency key on every attempt."""

    def _send(self, args, key):
        for attempt in range(3):
            try:
                return st.ToolGate._send(self, args, f"{key}-{attempt}")
            except RuntimeError:
                continue


class TryIt(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=HERE)
        self.pay, self.pay_url = payments_service.start_in_thread(slow_first=True)

    def tearDown(self):
        self.pay.shutdown()
        self.pay.server_close()
        self.tmp.cleanup()

    def test_1_new_key_per_attempt(self):
        gate = FreshKeyGate(Path(self.tmp.name) / "a.db", self.pay_url, retries=0)
        gate.request("send_refund", {"order_id": "A-1001", "amount": 25.0}, "run-1", "call_1")
        gate.decide(1, "alice", approve=True)
        gate.execute_approved()
        gate.db.close()
        refunds = requests.get(f"{self.pay_url}/refunds", timeout=5).json()
        print("\nobserved:", refunds)
        self.assertEqual(len(refunds), 2)

    def test_2_dry_run(self):
        model, url = start_in_thread()
        gate = st.ToolGate(Path(self.tmp.name) / "b.db", self.pay_url, dry_run=True)
        answer = st.run_agent("Refund order A-1001 for 25.00, it arrived broken.", gate, "run-2", base_url=url, model="fake-model")
        rows = gate.db.execute("SELECT COUNT(*) FROM approvals").fetchone()[0]
        gate.db.close()
        model.shutdown()
        model.server_close()
        refunds = requests.get(f"{self.pay_url}/refunds", timeout=5).json()
        print("\nobserved:", answer, "| approvals:", rows, "| refunds:", refunds)
        self.assertEqual((rows, refunds), (0, []))


if __name__ == "__main__":
    unittest.main(verbosity=2)
