"""python -m unittest test_serve_realtime -v: the real-clock tool target behaves like the lesson's limiter."""
import unittest

import ratelimit as rl
import serve_realtime as sr


class RealtimeTarget(unittest.TestCase):
    def test_burst_then_refill_rate_and_retry_after(self):
        srv = sr.start(0)
        try:
            counts, missing = sr.check(f"http://127.0.0.1:{srv.server_port}/data", rate=10, seconds=2)
        finally:
            srv.shutdown()
            srv.server_close()
            rl.Api.limiters = {}
        self.assertEqual(sum(counts.values()), 20)
        # burst 5 at t=0 plus ~2/s refill over ~1.9 s -> about 8-9 allowed; loose bounds for slow machines
        self.assertGreaterEqual(counts.get(200, 0), 6)
        self.assertLessEqual(counts.get(200, 0), 12)
        self.assertEqual(counts.get(200, 0) + counts.get(429, 0), 20)
        self.assertEqual(missing, 0)


if __name__ == "__main__":
    unittest.main()
