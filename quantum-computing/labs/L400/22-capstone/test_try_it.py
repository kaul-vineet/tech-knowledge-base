"""Tests for the capstone try-it items. Run: python -m unittest -v"""
import unittest

import try_it


class TryIt(unittest.TestCase):
    def test_small_budget(self):
        self.assertEqual(try_it.small_budget(), ("annealing", {"greedy": 1.0, "annealing": 1.0, "qaoa-noisy": 1.0}))

    def test_calibrated_device(self):
        self.assertEqual(try_it.calibrated_device(), {"esp": 0.5103, "gate_fidelity": 0.6262, "cx": 47, "depth": 48})


if __name__ == "__main__":
    unittest.main()
