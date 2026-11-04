"""Tests for lab 20 try-it items. Run: python -m unittest -v"""
import unittest

import try_it


class TryIt(unittest.TestCase):
    def test_other_drift(self):
        self.assertEqual(try_it.other_drift(), {"layout": [1, 2, 5, 0, 4], "esp": 0.7503, "cx": 13, "depth": 18,
                                                "uses_drifted_edge": False, "noisy_fidelity": 0.9855})

    def test_tight_budget_is_reported_not_hidden(self):
        self.assertEqual(try_it.tight_budget(), {"esp": 0.7835, "cx": 19, "depth": 21, "within_budget": False})


if __name__ == "__main__":
    unittest.main()
