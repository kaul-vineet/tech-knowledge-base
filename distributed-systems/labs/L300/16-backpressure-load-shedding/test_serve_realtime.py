"""python -m unittest test_serve_realtime -v: the real-clock tool target sheds with Retry-After and bounds latency."""
import unittest

import serve_realtime as sr


class RealtimeTarget(unittest.TestCase):
    def test_overload_is_shed_and_p99_bounded(self):
        srv = sr.start(0)
        try:
            out = sr.check(f"http://127.0.0.1:{srv.server_port}/work", rate=120, seconds=2)
        finally:
            srv.shutdown()
            srv.server_close()
        self.assertEqual(out["200"] + out["503"], 240)
        self.assertGreater(out["503"], 0)
        self.assertEqual(out["503_without_retry_after"], 0)
        self.assertLess(out["p99_ms"], 1000)  # bound 8 + 4 workers x 50 ms ~ 150 ms; loose for slow CI machines


if __name__ == "__main__":
    unittest.main()
