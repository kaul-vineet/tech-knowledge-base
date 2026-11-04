"""Lesson 20: three designs on 12 cases, the failure lab and the refusal paths (python -m unittest -v test_edge)."""
import os
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import edge  # noqa: E402
import fake_server_l400  # noqa: E402

CASE = {c["id"]: c for c in edge.CASES}


class Edge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.url = fake_server_l400.start_in_thread()
        cls.ask = staticmethod(lambda p: edge.ask(p, cls.url, "fake-model"))

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_options_measured(self):
        wrong = {o: [r["id"] for r in edge.evaluate(o, self.url, "fake-model") if not r["ok"]] for o in edge.OPTIONS}
        self.assertEqual(wrong, {"llm_decides": ["c02", "c04", "c05", "c06", "c08", "c09"],
                                 "llm_validated": ["c02", "c04", "c05", "c06", "c09"], "code_decides": []})

    def test_failure_lab_injection_changes_an_llm_decision(self):
        self.assertEqual(edge.llm_decides(CASE["c04"], self.ask)["action"], "approve_auto")  # 45 days: policy says deny
        self.assertEqual(edge.llm_decides(CASE["c08"], self.ask)["amount"], 120.0)  # more than the 80 paid
        self.assertEqual(edge.code_decides(CASE["c04"], self.ask)["action"], "deny")

    def test_validation_catches_only_invalid_answers(self):
        self.assertEqual(edge.llm_validated(CASE["c08"], self.ask)["action"], "escalate")  # 120 > paid: refused
        self.assertEqual(edge.llm_validated(CASE["c04"], self.ask)["action"], "approve_auto")  # valid but wrong

    def test_refusal_paths(self):
        down = edge.code_decides(CASE["c01"], ask=lambda p: None)  # model unavailable
        self.assertEqual((down["action"], down["explanation"]), ("approve_auto", "Decision: approve_auto for 30.0. Reason: R5 up to 50.00 within policy."))
        junk = edge.code_decides(CASE["c09"], ask=lambda p: "not json {")
        self.assertEqual((junk["action"], junk["proposal_problems"]), ("approve_auto", ["not JSON"]))  # no claim: no escalation
        out = edge.code_decides(CASE["c04"], self.ask)
        self.assertIn("$.override: additional property not allowed", out["proposal_problems"])

    def test_claims_only_escalate(self):
        self.assertEqual(edge.code_decides(CASE["c09"], self.ask)["action"], "escalate")
        threat = '{"claims": {"damaged": true, "threat": true}, "summary": "x"}'
        self.assertEqual(edge.code_decides(CASE["c03"], ask=lambda p: threat)["action"], "deny")  # deny stays deny

    def test_cli(self):
        env = {**os.environ, "LOCAL_MODEL_URL": self.url, "LOCAL_MODEL": "fake-model"}
        out = subprocess.run([sys.executable, "edge.py"], cwd=HERE, env=env, capture_output=True, text=True,
                             encoding="utf-8", timeout=60).stdout
        self.assertIn("code_decides   wrong 0/12: []", out)


if __name__ == "__main__":
    unittest.main()
