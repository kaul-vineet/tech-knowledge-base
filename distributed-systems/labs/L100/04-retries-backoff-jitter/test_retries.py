import random
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError, URLError

import retries as r


class TestRetries(unittest.TestCase):
    def test_full_jitter_stays_within_capped_ceiling(self):
        rng = random.Random(1)
        for attempt in range(10):
            ceiling = min(0.5, 0.02 * 2 ** attempt)
            for _ in range(200):
                self.assertTrue(0 <= r.backoff_full_jitter(attempt, rng) <= ceiling)

    def test_which_errors_are_retried(self):
        self.assertTrue(r.is_retryable(HTTPError("u", 503, "x", {}, None)))
        self.assertTrue(r.is_retryable(HTTPError("u", 429, "x", {}, None)))
        self.assertFalse(r.is_retryable(HTTPError("u", 400, "x", {}, None)))
        self.assertFalse(r.is_retryable(HTTPError("u", 404, "x", {}, None)))
        self.assertTrue(r.is_retryable(URLError("connection refused")))
        self.assertTrue(r.is_retryable(TimeoutError()))

    def test_budget_pauses_retries(self):
        b = r.RetryBudget(max_tokens=10, ratio=0.1)
        for _ in range(5):
            b.record(False)
        self.assertTrue(b.can_retry())   # 5.0 tokens = exactly half
        b.record(False)
        self.assertFalse(b.can_retry())  # below half -> retries paused

    def test_retries_against_flaky_b_are_reproducible(self):
        def run():
            r.FlakyB.rng, r.FlakyB.fail_rate = random.Random(42), 0.3
            srv = ThreadingHTTPServer(("127.0.0.1", 0), r.FlakyB)
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            url, rng, budget = f"http://127.0.0.1:{srv.server_port}/data", random.Random(7), r.RetryBudget()
            out = [r.get_with_retry(url, rng, budget, sleep=lambda s: None) for _ in range(20)]
            srv.shutdown(); srv.server_close()
            return out
        first, second = run(), run()
        self.assertEqual(first, second)
        self.assertEqual(len(first), 20)
        self.assertTrue(all(n <= 4 for _, n, _ in first))
        self.assertTrue(any(n > 1 and o == 200 for o, n, _ in first))  # a retry rescued a request


if __name__ == "__main__":
    unittest.main()
