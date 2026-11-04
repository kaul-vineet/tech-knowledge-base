"""failureLab symptom (observed, seeded): node.py with six sensors in one classroom.

PASSES because it pins the failure: every board samples at t = 0 and retries on the same
deadlines, the relay's 3-frame queue overflows, and 11% of readings never reach the store.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import edge_sim  # noqa: E402


class Symptom(unittest.TestCase):
    def test_six_boards_overflow_the_relay(self):
        res, _ = edge_sim.run("node.py")
        self.assertEqual((res["stored"], res["sampled"]), (160, 180))
        self.assertEqual((res["gave_up"], res["relay_queue_drops"]), (56, 149))
        self.assertGreater(res["p95_ms"], 9000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
