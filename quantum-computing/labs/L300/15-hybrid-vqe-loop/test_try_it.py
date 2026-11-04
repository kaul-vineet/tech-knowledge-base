"""Tests for lab 15 try-it items. Run: python -m unittest -v"""
import unittest

import try_it


class TryItNumpy(unittest.TestCase):
    def test_more_shots_only_helps_at_huge_cost(self):
        out = try_it.more_shots_same_optimizer()
        self.assertEqual({k: v["error"] for k, v in out.items()}, {1000: 1.5645, 100000: 0.9195, 1000000: 0.0076})
        self.assertGreater(out[1000000]["total_shots"], 1000 * try_it.spsa_cost()["total_shots"])

    def test_noisy_minimum_is_below_the_true_ground_energy(self):
        self.assertEqual(try_it.below_the_ground_energy(),
                         {"E0": -1.8405, "best_energy_est": -1.84964, "rows_below_E0": 8, "rows": 150})


if __name__ == "__main__":
    unittest.main()
