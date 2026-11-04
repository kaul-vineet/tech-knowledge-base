"""Fitness function (lab 17): keeps ADR-0017 true. Run in CI on every change.

Six sensors, five seeds, the design's per-link loss table: delivery >= 99.0 %,
p95 sensor-to-store latency <= 2,000 ms (simulated time), no reading given up.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import edge_sim  # noqa: E402

DELIVERY_MIN, P95_MAX_MS = 99.0, 2000


class Fitness(unittest.TestCase):
    def test_delivery_and_latency_across_seeds(self):
        for seed in range(1, 6):
            res, _ = edge_sim.run("solution.py", seed=seed)
            with self.subTest(seed=seed):
                self.assertGreaterEqual(res["delivery_pct"], DELIVERY_MIN)
                self.assertLessEqual(res["p95_ms"], P95_MAX_MS)
                self.assertEqual(res["gave_up"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
