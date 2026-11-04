"""buildTask check (lesson 8): waiting-room limit (max_queue). Point the import at your own file to test your version."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "solution"))
import mmc_capacity as SOLUTION  # noqa: E402
import mmc_queue as mq  # noqa: E402


class TestWaitingRoomLimit(unittest.TestCase):
    def test_unlimited_line_is_unchanged(self):
        r = SOLUTION.simulate(20_000, max_queue=None)
        self.assertEqual(r["blocked"], 0.0)
        base = mq.simulate(20_000)
        self.assertEqual({k: r[k] for k in base}, base)  # same seed, same events: identical results

    def test_no_waiting_room_matches_erlang_b(self):
        r = SOLUTION.simulate(200_000, max_queue=0)
        self.assertEqual(r["Wq"], 0.0)
        self.assertAlmostEqual(r["blocked"], SOLUTION.erlang_b(), delta=0.01)
        self.assertAlmostEqual(SOLUTION.erlang_b(), 0.268, places=3)

    def test_bigger_room_blocks_fewer(self):
        b = [SOLUTION.simulate(50_000, max_queue=q)["blocked"] for q in (0, 2, 5, 20)]
        self.assertEqual(b, sorted(b, reverse=True))


if __name__ == "__main__":
    unittest.main()
