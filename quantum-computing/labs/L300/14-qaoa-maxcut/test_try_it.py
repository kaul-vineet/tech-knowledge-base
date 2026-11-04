"""Tests for lab 14 try-it items. Run: python -m unittest -v"""
import unittest

import try_it


class TryItNumpy(unittest.TestCase):
    def test_only_two_of_eight_random_starts_succeed(self):
        out = try_it.random_starts()
        self.assertEqual(out["ratios"], [0.7002, 0.8352, 0.9247, 0.9247, 0.7009, 0.8329, 0.7002, 0.8329])
        self.assertEqual(out["hits"], 2)

    def test_sampling_finds_an_optimal_cut(self):
        self.assertEqual(try_it.sample_the_answer(), {"P_optimal": 0.707, "best_sampled_cut": 5, "optimal_samples": 13})


if __name__ == "__main__":
    unittest.main()
