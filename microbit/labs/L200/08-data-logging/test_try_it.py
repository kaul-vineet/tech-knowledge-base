import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    """The observed tryIt results quoted in content/L200.json."""

    def test_try_1(self):
        self.assertEqual(try_it.try_1(), "time_ms,temp,light | Time (seconds),temp,light | 0.00,21,120 | "
                         "0,21,120 | 1.00,22,110 | 1000,22,110")

    def test_try_2(self):
        self.assertEqual(try_it.try_2(), "kept 2 rows [['0', '21', '120'], ['1000', '22', '110']]; skipped 3 "
                         "(Time (seconds),temp,light: time_ms not an integer, 0.00,21,120: time_ms not an "
                         "integer, 1.00,22,110: time_ms not an integer)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
