import unittest
from email.utils import formatdate

import ratelimit as rl
from helpers import SimClock


class TestTokenBucket(unittest.TestCase):
    def test_burst_then_refill_and_exact_wait(self):
        clock = SimClock()
        bucket = rl.TokenBucket(2.0, 5, clock)
        self.assertEqual([bucket.allow()[0] for _ in range(6)], [True] * 5 + [False])
        self.assertEqual(bucket.allow(), (False, 0.5))  # 1 token at 2 tokens/s = 0.5 s
        clock.t = 0.5
        self.assertEqual(bucket.allow(), (True, 0.0))

    def test_long_run_rate_is_bounded(self):
        clock, bucket, ok = SimClock(), rl.TokenBucket(2.0, 5, SimClock()), 0
        bucket.clock = clock
        for i in range(1000):  # hammer every 10 ms for 10 s
            clock.t = i / 100
            ok += bucket.allow()[0]
        self.assertLessEqual(ok, 5 + 2 * 10)  # burst + rate x time


class TestRetryAfter(unittest.TestCase):
    def test_both_rfc9110_forms(self):
        self.assertEqual(rl.retry_after_seconds("120"), 120)
        self.assertAlmostEqual(rl.retry_after_seconds(formatdate(1_000_003, usegmt=True), now_epoch=1_000_000), 3.0)


class TestApi(unittest.TestCase):
    def test_429_with_retry_after_and_per_client_isolation(self):
        out = rl.run({"alice": (12, True), "bob": (12, False), "carol": (3, True)})
        self.assertEqual((out["alice"]["429"], out["alice"]["done"]), (4, 4.0))
        self.assertIn("429(wait 1)", out["alice"]["trace"])
        self.assertGreater(out["bob"]["429"], 30)  # the naive client burns requests
        self.assertEqual(out["carol"]["429"], 0)  # bob's flood does not touch carol's bucket


if __name__ == "__main__":
    unittest.main()
