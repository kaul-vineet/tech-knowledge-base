"""Tests for lab 13 try-it items. Run: python -m unittest -v"""
import unittest

import try_it


class TryItNumpy(unittest.TestCase):
    def test_zne_trades_bias_for_variance(self):
        out = try_it.zne_shot_noise()
        self.assertEqual(out, {"raw_mean": 0.9041, "raw_std": 0.0069, "richardson_mean": 0.9942, "richardson_std": 0.017})
        self.assertGreater(out["richardson_std"], 2 * out["raw_std"])

    def test_clip_is_close_but_constrained_is_better(self):
        out = try_it.clip_vs_constrained()
        self.assertEqual(out, {"clip": 0.0436, "constrained": 0.0426})


if __name__ == "__main__":
    unittest.main()
