import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    """The observed tryIt results quoted in content/L100.json."""

    def test_try_1(self):
        self.assertEqual(try_it.try_1(), 'lit=13, sum=101, centre=9')

    def test_try_2(self):
        self.assertEqual(try_it.try_2(), '0 1 2 3 4 0 1')


if __name__ == "__main__":
    unittest.main(verbosity=2)
