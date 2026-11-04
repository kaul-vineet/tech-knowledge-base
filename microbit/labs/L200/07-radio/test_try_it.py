import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    """The observed tryIt results quoted in content/L200.json."""

    def test_try_1(self):
        self.assertEqual(try_it.try_1(), 'tx btn 1 A')

    def test_try_2(self):
        self.assertEqual(try_it.try_2(), 'tx btn 1 A*40 | rx btn 1 A*23 | bytes on air: 32')


if __name__ == "__main__":
    unittest.main(verbosity=2)
