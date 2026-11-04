"""Lesson 12 tests: three kinds of check, the gate, the failureLab (spot check misses v2, gate blocks it), CLI."""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import eval_gate as eg  # noqa: E402
from fake_server_l300 import start_in_thread  # noqa: E402

V1, V2 = HERE / "prompts" / "v1.txt", HERE / "prompts" / "v2.txt"
CASE = {"id": "x", "ticket": "I was charged twice", "expect": {"category": "billing", "priority": "normal"},
        "rubric": {"mentions": "charged"}}


class EvalGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.url = start_in_thread()
        cls.kw = {"base_url": cls.url, "model": "fake-model"}
        cls.baseline = json.loads((HERE / "baseline.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_three_kinds_of_check(self):
        good = '{"category": "billing", "priority": "normal", "summary": "I was charged twice"}'
        self.assertEqual(eg.check(CASE, good), [])
        self.assertEqual(eg.check(CASE, "Sure! billing"), ["structural: not JSON"])
        self.assertIn("structural: keys ['category', 'priority']", eg.check(CASE, '{"category": "billing", "priority": "normal"}'))
        self.assertEqual(eg.check(CASE, good.replace("billing", "other")), ["exact: category='other', expected 'billing'"])
        long_sorry = '{"category": "billing", "priority": "normal", "summary": "' + "sorry " * 13 + '"}'
        self.assertEqual(eg.check(CASE, long_sorry), ["rubric: 0/3 points"])

    def test_v1_matches_baseline_and_passes(self):
        report = eg.evaluate(V1, **self.kw)
        self.assertEqual((report["passed"], report["total"]), (20, 20))
        self.assertEqual(eg.gate(report, self.baseline), [])

    def test_failure_lab_spot_check_misses_the_regression(self):
        # before: "CI" ran three hand-picked examples - all still pass with v2, so the break is silent
        spot = eg.evaluate(V2, eg.load_cases()[:3], **self.kw)
        self.assertEqual(spot["passed"], 3)

    def test_failure_lab_gate_blocks_v2(self):
        # after: the full golden set + regression gate names the two broken cases
        report = eg.evaluate(V2, **self.kw)
        self.assertEqual(report["pass_rate"], 0.9)
        self.assertEqual(eg.gate(report, self.baseline),
                         ["pass rate 90% < 95%", "regressions vs baseline: ['t07', 't15']"])

    def test_cli_exit_codes(self):
        env = dict(os.environ, LOCAL_MODEL_URL=self.url, LOCAL_MODEL="fake-model", PYTHONIOENCODING="utf-8")
        run = lambda *a: subprocess.run([sys.executable, "eval_gate.py", *a], cwd=HERE, env=env,
                                        capture_output=True, encoding="utf-8")
        ok, bad = run(), run("--prompt", str(V2))
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
        self.assertIn("GATE: PASS", ok.stdout)
        self.assertEqual(bad.returncode, 1)
        self.assertIn("FAIL t07 (account): exact: category='other', expected 'account'", bad.stdout)


if __name__ == "__main__":
    unittest.main()
