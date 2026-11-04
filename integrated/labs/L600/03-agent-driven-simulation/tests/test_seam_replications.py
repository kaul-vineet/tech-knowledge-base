"""Seam sim stochasticity <-> conclusions: no conclusion from noise; replications come from a target half-width."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _fixture  # noqa: E402
import unittest  # noqa: E402

import _kb  # noqa: E402
import pipeline  # noqa: E402
import stats  # noqa: E402

A, B = _fixture.A, _fixture.B


class TestReplicationSeam(unittest.TestCase):
    def test_exact_t_quantiles_and_the_approximation_gap_at_df_2(self):
        self.assertAlmostEqual(stats.t_quantile(0.975, 2), 4.302653, places=5)
        self.assertAlmostEqual(stats.t_quantile(0.975, 9), 2.262157, places=5)
        self.assertLess(_kb.load("warmup").t975(2), 3.9)  # Cornish-Fisher is too narrow at df 2

    def test_required_replications_rule(self):
        rule = pipeline.load_policy("solution/replications.py")
        self.assertEqual(rule(3, [1.0, 2.0, 3.0], [1.0, 2.0, 3.0], 0.3), 10)
        a = [4.0 + (i % 5) * 0.5 for i in range(10)]
        b = [3.0 + (i % 5) * 0.4 for i in range(10)]
        _, hw, _ = stats.welch_ci(a, b)
        self.assertEqual(rule(3, a, b, 0.3), math.ceil(10 * (hw / 0.3) ** 2))

    def test_extension_reuses_the_first_runs_unchanged(self):
        reg3, pl3 = _fixture.session("few-reps")[:2]
        reg55 = _fixture.session()[0]
        job3 = [r["run_id"] for r in reg3.runs() if r["job"] == "job-3"]
        job55 = [r["run_id"] for r in reg55.runs() if r["job"] == "job-3"]
        self.assertEqual(job3, job55[:6])  # reps 0-2 of both arms: same seeds, same ids

    def test_three_replications_cannot_support_a_conclusion(self):
        _, f = _fixture.ab_facts(_fixture.session("few-reps")[0])
        self.assertEqual(f["replications"], 3)
        self.assertLessEqual(f["baseline_mean"] - f["baseline_half_width"], f["candidate_mean"] + f["candidate_half_width"])
        self.assertLess(f["difference_low"], 0)
        self.assertGreater(f["difference_high"], 0)
        self.assertEqual(f["verdict"], "inconclusive")


if __name__ == "__main__":
    unittest.main()
