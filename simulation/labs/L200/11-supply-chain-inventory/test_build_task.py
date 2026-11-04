"""buildTask check (lesson 11): fill rate. Point the import at your own file to test your version."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "solution"))
import fill_rate as SOLUTION  # noqa: E402
import inventory as inv  # noqa: E402


class TestFillRate(unittest.TestCase):
    def test_hand_case(self):
        r = SOLUTION.simulate(0, 5, np.array([8, 0]), np.array([1, 1]))  # 8 wanted, 5 sold
        self.assertAlmostEqual(r["fill_rate"], 5 / 8)

    def test_between_zero_and_one_and_consistent(self):
        d, lead = inv.streams(0)
        r = SOLUTION.simulate(30, 80, d, lead)
        self.assertTrue(0 <= r["fill_rate"] <= 1)
        self.assertAlmostEqual(r["fill_rate"], (d.sum() - r["lost"]) / d.sum())

    def test_bigger_S_serves_more_with_crn(self):
        m, h = SOLUTION.compare_fill((30, 80), (30, 90))
        self.assertGreater(m - h, 0)


if __name__ == "__main__":
    unittest.main()
