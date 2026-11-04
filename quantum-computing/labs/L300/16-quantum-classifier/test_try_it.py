"""Tests for lab 16 try-it items. Run: python -m unittest -v"""
import unittest

import try_it


class TryItNumpy(unittest.TestCase):
    def test_global_readout_is_flat_even_with_good_init(self):
        out = try_it.global_readout_with_good_init()
        self.assertEqual(out, {"local": 0.8742, "global": 0.0303})

    def test_shot_noise_costs_accuracy(self):
        self.assertEqual(try_it.shot_noise_at_prediction(), {"exact": 0.9, "100_shots": 0.85})


if __name__ == "__main__":
    unittest.main()
