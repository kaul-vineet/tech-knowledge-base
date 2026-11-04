"""buildTask check (lesson 10): sequential replications. Point the import at your own file to test your version."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "solution"))
import sequential_reps as SOLUTION  # noqa: E402
import warmup as wu  # noqa: E402


class TestSequentialReplications(unittest.TestCase):
    def test_stops_when_precise_enough_and_not_before(self):
        n, mean, half = SOLUTION.reps_for_precision(rel=0.05)
        self.assertLessEqual(half / mean, 0.05 / 1.05)
        prev = wu.ci([wu.waits(5_000, 201 + i)[169:].mean() for i in range(n - 1)])
        self.assertGreater(prev[1] / prev[0], 0.05 / 1.05)  # one replication fewer was not enough
        self.assertLess(abs(mean - wu.TRUE_WQ), half)

    def test_looser_target_needs_fewer_replications(self):
        self.assertLess(SOLUTION.reps_for_precision(rel=0.10)[0], SOLUTION.reps_for_precision(rel=0.05)[0])

    def test_cap_is_respected(self):
        self.assertEqual(SOLUTION.reps_for_precision(rel=0.001, max_reps=12)[0], 12)


if __name__ == "__main__":
    unittest.main()
