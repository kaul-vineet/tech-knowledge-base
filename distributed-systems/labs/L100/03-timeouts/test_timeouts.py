import io
import unittest
from contextlib import redirect_stdout

import timeouts as t


class TestTimeouts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = t.start_b()
        cls.base = f"http://127.0.0.1:{cls.b.server_port}/work?delay="

    @classmethod
    def tearDownClass(cls):
        cls.b.shutdown()
        cls.b.server_close()

    def test_no_timeout_waits_for_slow_b(self):
        result, took = t.call(self.base + "0.6")
        self.assertEqual(result, "200 ok")
        self.assertGreaterEqual(took, 0.6)

    def test_timeout_fails_fast(self):
        result, took = t.call(self.base + "3", timeout=0.3)
        self.assertTrue(result.startswith("FAILED"))
        self.assertLess(took, 1.5)  # far less than B's 3 s

    def test_choose_timeout_is_reproducible(self):
        with redirect_stdout(io.StringIO()):
            a, b = t.choose_timeout(), t.choose_timeout()
        self.assertEqual(a, b)
        self.assertTrue(0.04 < a < 0.2)
        with redirect_stdout(io.StringIO()):
            stricter = t.choose_timeout(false_timeout_rate=0.01)  # p99 instead of p99.9
        self.assertLess(stricter, a)


if __name__ == "__main__":
    unittest.main()
