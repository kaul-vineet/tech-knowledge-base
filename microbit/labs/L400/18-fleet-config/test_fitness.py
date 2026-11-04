"""Fitness function (lab 18): keeps ADR-0018 true.

Over 5 seeds, both rollout strategies and 10 % / 30 % loss: no device ever runs a config version the
gateway has not acknowledged (unacked_ticks == 0), and a staged rollout exposes at most ONE device
to a bad version (canary blast radius).
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fleet_sim  # noqa: E402


class Fitness(unittest.TestCase):
    def test_no_device_runs_an_unacknowledged_config(self):
        for seed in range(1, 6):
            for loss in (0.10, 0.30):
                for strategy in ("staged", "push-all"):
                    m, _ = fleet_sim.run("solution.py", strategy, loss=loss, seed=seed)
                    with self.subTest(seed=seed, loss=loss, strategy=strategy):
                        self.assertEqual(m["unacked_ticks"], 0)
                        if strategy == "staged":
                            self.assertLessEqual(m["max_on_bad"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
