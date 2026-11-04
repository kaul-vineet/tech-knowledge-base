import unittest

import eval_stats as s


class EvalStatsTest(unittest.TestCase):
    def test_wilson_matches_score_test_roots(self):
        for x, n in ((0, 10), (7, 10), (18, 20), (20, 20)):
            w, b = s.wilson(x, n), s.score_roots_by_bisection(x, n)
            self.assertAlmostEqual(w[0], b[0], places=9)
            self.assertAlmostEqual(w[1], b[1], places=9)

    def test_wilson_stays_in_unit_interval_wald_does_not(self):
        self.assertGreater(s.wald(18, 20)[1], 1.0)
        lo, hi = s.wilson(18, 20)
        self.assertTrue(0 <= lo < hi <= 1)

    def test_wilson_coverage_beats_wald_near_one(self):
        self.assertGreater(s.coverage(s.wilson, 20, 0.95), s.coverage(s.wald, 20, 0.95) + 0.2)

    def test_sample_size_and_exact_power(self):
        self.assertEqual(s.sample_size(0.90, 0.85), 253)
        c, size, power = s.exact_power(253, 0.90, 0.85)
        self.assertLessEqual(size, 0.05)
        self.assertGreater(power, 0.75)

    def test_mcnemar(self):
        self.assertAlmostEqual(s.mcnemar_exact(2, 0), 0.5)
        self.assertAlmostEqual(s.mcnemar_exact(15, 5), 0.04138946533203125)
        self.assertLess(s.mcnemar_exact(15, 5), s.two_proportion_p(170, 160, 200))

    def test_fwer(self):
        self.assertAlmostEqual(s.fwer_independent(0.05, 20), 0.6415140775914581)
        self.assertLessEqual(s.fwer_independent(0.05 / 20, 20), 0.05)


if __name__ == "__main__":
    unittest.main()
