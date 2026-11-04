"""tryIt predictions, checked."""
import sys
import unittest

import shared

sys.path.insert(0, str(shared.LAB / "try_it"))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    def test_longer_lease_removes_expiries_keeps_exact_shots(self):
        short, long_ = try_it.lease(10.0), try_it.lease(20.0)
        self.assertGreater(short["lease_expiries"], 0)
        self.assertEqual(long_["lease_expiries"], 0)
        self.assertEqual(short["shots_exact"], long_["shots_exact"])

    def test_policies(self):
        chosen, best, fast = (try_it.policy(p) for p in ("floor+budget", "best-fidelity", "fastest"))
        self.assertGreater(best["p95_queue_s"], 30.0)            # everything queues on slow-clean
        self.assertGreater(fast["below_floor"], 0)               # fastest ignores the client's fidelity floor
        self.assertLessEqual(chosen["p95_queue_s"], 30.0)
        self.assertEqual(chosen["below_floor"], 0)


if __name__ == "__main__":
    unittest.main()
