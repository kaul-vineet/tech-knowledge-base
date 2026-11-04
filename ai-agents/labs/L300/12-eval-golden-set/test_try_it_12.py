"""Try it (lesson 12): two changes, run against the fake server. Run: python -m unittest -v test_try_it_12"""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import eval_gate as eg  # noqa: E402
from fake_server_l300 import start_in_thread  # noqa: E402


class TryIt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.url = start_in_thread()
        cls.baseline = json.loads((HERE / "baseline.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_1_lower_the_bar_to_85_percent(self):
        report = eg.evaluate(HERE / "prompts" / "v2.txt", base_url=self.url, model="fake-model")
        reasons = eg.gate(report, self.baseline, min_pass_rate=0.85)
        print("\nobserved:", reasons)
        self.assertEqual(reasons, ["regressions vs baseline: ['t07', 't15']"])

    def test_2_delete_the_account_cases(self):
        cases = [c for c in eg.load_cases() if c["expect"]["category"] != "account"]  # "fix the test", not the prompt
        report = eg.evaluate(HERE / "prompts" / "v2.txt", cases, base_url=self.url, model="fake-model")
        reasons = eg.gate(report, self.baseline)
        print("\nobserved:", f"{report['passed']}/{report['total']}", reasons)
        self.assertEqual((report["passed"], report["total"], reasons), (18, 18, []))


if __name__ == "__main__":
    unittest.main(verbosity=2)
