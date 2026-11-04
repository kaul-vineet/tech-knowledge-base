"""Lesson 15 tests: failureLab (double refund vs key + approval), reject, dry-run, same call -> same key, 422, CLI."""
import json
import os
import subprocess
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
from naive_refund import send_refund_naive  # noqa: E402

TASK = "Refund order A-1001 for 25.00, it arrived broken."


class SafeTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model, cls.url = start_in_thread()

    @classmethod
    def tearDownClass(cls):
        cls.model.shutdown()
        cls.model.server_close()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=HERE)
        self.pay, self.pay_url = payments_service.start_in_thread(slow_first=True)
        self.gate = st.ToolGate(Path(self.tmp.name) / "approvals.db", self.pay_url)

    def tearDown(self):
        self.gate.db.close()
        self.pay.shutdown()
        self.pay.server_close()
        self.tmp.cleanup()

    def refunds(self):
        return requests.get(f"{self.pay_url}/refunds", timeout=5).json()

    def events(self):
        return [e for (e,) in self.gate.db.execute("SELECT event FROM audit ORDER BY id")]

    def test_failure_lab_naive_retry_refunds_twice(self):
        send_refund_naive(self.pay_url, "A-1001", 25.0)  # before: timeout -> retry -> second refund
        self.assertEqual(len(self.refunds()), 2)

    def test_failure_lab_key_and_approval_refund_once(self):
        answer = st.run_agent(TASK, self.gate, "run-1", base_url=self.url, model="fake-model")
        self.assertIn("queued for human approval as #1", answer)
        self.assertEqual(self.refunds(), [])  # nothing moves before a human says yes
        self.gate.decide(1, "alice", approve=True)
        result = self.gate.execute_approved()
        self.assertEqual(len(self.refunds()), 1)  # after: the retry was replayed, not repeated
        self.assertTrue(result[0]["replayed"])
        self.assertEqual(self.events(), ["queued", "approved", "timeout_retry", "executed"])

    def test_rejected_never_runs(self):
        st.run_agent(TASK, self.gate, "run-2", base_url=self.url, model="fake-model")
        self.gate.decide(1, "bob", approve=False)
        self.assertEqual((self.gate.execute_approved(), self.refunds()), ([], []))

    def test_dry_run_changes_nothing(self):
        self.gate.dry_run = True
        answer = st.run_agent(TASK, self.gate, "run-3", base_url=self.url, model="fake-model")
        self.assertIn('DRY RUN: would call send_refund with {"amount": 25.0, "order_id": "A-1001"}', answer)
        self.assertEqual(self.gate.db.execute("SELECT COUNT(*) FROM approvals").fetchone()[0], 0)
        self.assertEqual(self.refunds(), [])

    def test_same_call_same_key_one_row(self):
        a = self.gate.request("send_refund", {"order_id": "A-1", "amount": 5.0}, "run-4", "call_1")
        b = self.gate.request("send_refund", {"order_id": "A-1", "amount": 5.0}, "run-4", "call_1")  # agent replayed
        self.assertEqual(a, b)
        self.assertEqual(self.gate.db.execute("SELECT COUNT(*) FROM approvals").fetchone()[0], 1)

    def test_key_reuse_with_other_body_is_422(self):
        post = lambda amount: requests.post(f"{self.pay_url}/refunds", json={"order_id": "B-2", "amount": amount},
                                            headers={"Idempotency-Key": "k1"}, timeout=5)
        self.assertEqual(post(10.0).status_code, 201)  # slow_first: answers after 0.6 s, no client timeout here
        self.assertEqual(post(99.0).status_code, 422)
        self.assertEqual(len(self.refunds()), 1)

    def test_read_only_tool_runs_directly(self):
        self.assertIn('"status": "delivered"', self.gate.request("lookup_order", {"order_id": "A-1001"}, "run-5", "c1"))
        self.assertEqual(self.events(), ["read"])

    def test_cli_runs(self):
        env = dict(os.environ, LOCAL_MODEL_URL=self.url, LOCAL_MODEL="fake-model", PYTHONIOENCODING="utf-8")
        out = subprocess.run([sys.executable, "safe_tools.py"], cwd=HERE, env=env, capture_output=True,
                             encoding="utf-8", check=True).stdout
        (HERE / "approvals.db").unlink(missing_ok=True)
        self.assertIn("refunds after approval : [{'id': 1, 'order_id': 'A-1001', 'amount': 25.0}]", out)
        self.assertEqual(json.loads(out.strip().splitlines()[-1])["event"], "executed")


if __name__ == "__main__":
    unittest.main()
