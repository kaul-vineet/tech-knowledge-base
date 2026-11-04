"""Tests for lab 19 try-it items. Run: python -m unittest -v"""
import unittest

import try_it


class TryIt(unittest.TestCase):
    def test_better_hardware(self):
        self.assertEqual(try_it.better_hardware(), {"distance": 13, "physical_qubits": 2092220, "runtime_s": 27860.0})

    def test_near_threshold(self):
        self.assertEqual(try_it.near_threshold(), {0.001: (11, 24200), 0.005: (37, 273800),
                                                   0.009: "no distance <= 101 meets budget 0.01",
                                                   0.011: "physical error 0.011 is not below the threshold 0.01"})


if __name__ == "__main__":
    unittest.main()
