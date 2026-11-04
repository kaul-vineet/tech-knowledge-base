import unittest

import numpy as np

import monte_carlo as mc


class TestMonteCarlo(unittest.TestCase):
    def test_same_seed_same_answer(self):
        self.assertTrue(np.array_equal(mc.sample_totals(1000, 42), mc.sample_totals(1000, 42)))

    def test_different_seed_different_samples(self):
        self.assertFalse(np.array_equal(mc.sample_totals(1000, 42), mc.sample_totals(1000, 7)))

    def test_totals_stay_within_task_bounds(self):
        t = mc.sample_totals(10_000, 1)
        self.assertGreaterEqual(t.min(), 2 + 5 + 2)
        self.assertLessEqual(t.max(), 8 + 14 + 6)

    def test_ci_contains_exact_mean(self):
        mean, hw, _ = mc.summarise(mc.sample_totals(100_000, 42))
        self.assertLessEqual(abs(mean - mc.exact_mean()), hw)

    def test_ci_shrinks_about_10x_for_100x_samples(self):
        _, hw_small, _ = mc.summarise(mc.sample_totals(1_000, 42))
        _, hw_big, _ = mc.summarise(mc.sample_totals(100_000, 42))
        self.assertAlmostEqual(hw_small / hw_big, 10, delta=1.5)


if __name__ == "__main__":
    unittest.main()
