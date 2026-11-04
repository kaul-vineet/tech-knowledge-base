"""Build task (lesson 11): a per-session rate limit on tool calls."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "solution"))
from rate_limited_session import RateLimitedSession  # noqa: E402


class BuildTask(unittest.TestCase):
    def test_third_call_is_refused(self):
        s = RateLimitedSession({"search_docs"}, max_calls_per_tool=2)
        results = [s.execute("search_docs", {"query": "deploys"}) for _ in range(3)]
        self.assertIn("handbook.md", results[0])
        self.assertIn("handbook.md", results[1])
        self.assertEqual(results[2], "error: rate limit: search_docs called more than 2 times in this session")


if __name__ == "__main__":
    unittest.main()
