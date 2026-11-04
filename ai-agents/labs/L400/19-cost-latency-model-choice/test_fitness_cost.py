"""Fitness function (lesson 19, ADR-0019): the cheap route must not cost quality.

Thresholds on the 20-case golden set: rules+cascade passes 20/20 (= large-only), costs <= 60 % of large-only,
and the production prompt keeps >= 60 % of prompt tokens cacheable (stable instructions first).
"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import fake_server_l400  # noqa: E402
import route_cost as rc  # noqa: E402


class FitnessCost(unittest.TestCase):
    def test_route_keeps_quality_and_saves(self):
        server, url = fake_server_l400.start_in_thread()
        try:
            large = rc.summary(rc.run("large-only", base_url=url))
            chosen = rc.summary(rc.run("rules+cascade", base_url=url))
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(chosen["passed"], large["passed"])
        self.assertLessEqual(chosen["cost"], 0.6 * large["cost"])
        self.assertGreaterEqual(large["cache_ratio"], 0.6)


if __name__ == "__main__":
    unittest.main()
