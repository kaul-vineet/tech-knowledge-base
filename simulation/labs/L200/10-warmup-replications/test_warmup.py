import math
import unittest

import numpy as np

import warmup as wu


class TestWarmup(unittest.TestCase):
    def test_backlog_sets_first_wait(self):
        self.assertEqual(wu.waits(10, 1, backlog=0)[0], 0.0)
        self.assertGreater(wu.waits(10, 1)[0], 10.0)  # 30 tickets of ~1 min each

    def test_welch_moving_average_by_hand(self):
        runs = np.array([[0.0, 2, 4, 6, 8], [2.0, 4, 6, 8, 10]])  # across-rep mean: 1, 3, 5, 7, 9
        np.testing.assert_allclose(wu.welch(runs, window=1), [1.0, 3.0, 5.0, 7.0])  # t=0: own value; then 3-point mean
        np.testing.assert_allclose(wu.welch(runs, window=2)[:3], [1.0, 3.0, 5.0])  # t=1: mean of first 3

    def test_warmup_point_on_a_clean_curve(self):
        curve = np.concatenate([np.linspace(30, 4, 100), np.full(900, 4.0)])
        self.assertEqual(wu.warmup_point(curve)[0], 100 - 1)  # first point within 5% of 4.0

    def test_t_quantile_close_to_tables(self):
        for df, table in ((9, 2.262), (19, 2.093), (39, 2.023), (79, 1.990)):
            self.assertAlmostEqual(wu.t975(df), table, delta=0.005)

    def test_deleting_warmup_removes_bias(self):
        short = [wu.waits(1_000, seed) for seed in range(101, 141)]
        m0, h0 = wu.ci([r.mean() for r in short])
        m1, h1 = wu.ci([r[169:].mean() for r in short])
        self.assertGreater(m0 - h0, wu.TRUE_WQ)  # biased: CI misses 4.0 from above
        self.assertLess(abs(m1 - wu.TRUE_WQ), h1)  # after deletion the CI covers 4.0

    def test_half_width_shrinks_like_one_over_sqrt_n(self):
        means = [wu.waits(5_000, seed)[169:].mean() for seed in range(201, 281)]
        h10, h80 = wu.ci(means[:10])[1], wu.ci(means)[1]
        self.assertAlmostEqual(h10 / h80, math.sqrt(8), delta=0.35 * math.sqrt(8))


try:
    from scipy import stats
except ImportError:  # SciPy runs in CI only
    stats = None


@unittest.skipIf(stats is None, "scipy not installed (pending-ci)")
class TestSciPyEquivalent(unittest.TestCase):
    def test_t975_matches_scipy(self):
        for df in (9, 19, 39, 79):
            self.assertAlmostEqual(wu.t975(df), stats.t.ppf(0.975, df), delta=0.005)


if __name__ == "__main__":
    unittest.main()
