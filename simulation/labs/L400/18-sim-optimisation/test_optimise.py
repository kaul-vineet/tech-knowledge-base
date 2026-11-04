import unittest

import numpy as np

import make_truth
import optimise as op


class TestBudgetAndStreams(unittest.TestCase):
    def test_budget_refuses_extra_runs(self):
        b = op.Budget(3, crn_offset=0)
        for r in range(3):
            b.run((30, 50), r)
        with self.assertRaises(RuntimeError):
            b.run((30, 50), 3)

    def test_common_random_numbers_same_stream_same_cost(self):
        a, b = op.Budget(10, 0), op.Budget(10, 0)
        self.assertEqual(a.run((30, 50), 2), b.run((30, 50), 2))
        self.assertNotEqual(a.run((30, 50), 2), op.Budget(10, 1000).run((30, 50), 2))

    def test_every_method_spends_at_most_the_budget(self):
        for method in (op.grid_search, op.surrogate_search, op.evolution):
            with self.subTest(method=method.__name__):
                self.assertLessEqual(op.optimise(method, 0)["runs"], op.BUDGET)


class TestBuildingBlocks(unittest.TestCase):
    def test_ocba_by_hand(self):
        # means 1, 2, 3 and sd 1: N2 ~ (1/1)^2 = 1, N3 ~ (1/2)^2 = 0.25, Nb = 1 * sqrt(1 + 0.0625) = 1.0308
        n = op.ocba([1.0, 2.0, 3.0], [1.0, 1.0, 1.0], 2.2808)
        np.testing.assert_allclose(n, [1.0308, 1.0, 0.25], atol=1e-4)

    def test_gp_lite_interpolates_with_small_noise(self):
        X = np.array([[0.0], [1.0], [2.0], [3.0]])
        y = np.array([1.0, 3.0, 2.0, 5.0])
        mean, sd = op.gp_posterior(X, y, X, length=1.0, noise=1e-6)
        np.testing.assert_allclose(mean, y, atol=1e-3)
        self.assertTrue(np.all(sd < 1e-2))

    def test_truth_table_reproduces(self):
        for s, q in ((25, 70), (10, 20), (50, 100)):
            self.assertEqual(make_truth.true_cost(s, q), op.TRUTH[(s, q)])


class TestFailureLab(unittest.TestCase):
    """Fault: the shipped pick() reports the winner's search-phase mean. Your fix is checked by test_build_task.py."""

    def test_fault_winners_curse_makes_reported_cost_optimistic(self):
        rows = [op.optimise(op.grid_search, m) for m in range(5)]
        self.assertLess(np.mean([r["reported"] - r["true"] for r in rows]), -0.3)


if __name__ == "__main__":
    unittest.main()
