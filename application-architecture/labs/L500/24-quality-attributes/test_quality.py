import unittest

import availability as av
import tradeoff as tr


class AvailabilityTest(unittest.TestCase):
    def test_series_and_parallel(self):
        self.assertAlmostEqual(0.999 * 0.9995, av.series([0.999, 0.9995]))
        self.assertAlmostEqual(1 - 0.005 ** 2, av.parallel([0.995, 0.995]))

    def test_series_never_beats_weakest_part(self):
        parts = [0.9999, 0.995, 0.999]
        self.assertLessEqual(av.series(parts), min(parts))
        self.assertLessEqual(av.union_bound(parts), av.series(parts))

    def test_k_of_n(self):
        self.assertAlmostEqual(av.parallel([0.9] * 3), av.k_of_n(1, 3, 0.9))
        self.assertAlmostEqual(0.9 ** 3, av.k_of_n(3, 3, 0.9))

    def test_downtime(self):
        self.assertAlmostEqual(43.2, av.downtime_minutes(0.999, av.MINUTES_PER_30_DAYS))
        self.assertAlmostEqual(52.56, av.downtime_minutes(0.9999))
        self.assertAlmostEqual(3.0, av.nines(0.999))

    def test_library_loans(self):
        self.assertAlmostEqual(0.998375686, av.library_loans(2), places=8)


class TradeoffTest(unittest.TestCase):
    def test_break_even(self):
        self.assertAlmostEqual(0.4 / 0.95, tr.break_even(tr.SINGLE_SQLITE, tr.REPLICATED_POSTGRES))
        self.assertIsNone(tr.break_even((0.9, 0.9), (0.1, 0.2)))  # dominated: no trade-off

    def test_highest_priority_leaf_is_high_high(self):
        top = tr.prioritise()[0]
        self.assertEqual(("H", "H"), (top[3], top[4]))


if __name__ == "__main__":
    unittest.main()
