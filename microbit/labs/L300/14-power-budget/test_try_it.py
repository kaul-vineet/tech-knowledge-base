import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    """The observed tryIt results quoted in content/L300.json."""

    def test_try_1(self):
        self.assertEqual(try_it.try_1(), "solution.py: avg 6.4 mA, life 195.3 h, meets brief False")

    def test_try_2(self):
        self.assertEqual(try_it.try_2(), "main.py: avg 7.9 mA, life 158.2 h, meets brief False")


if __name__ == "__main__":
    unittest.main(verbosity=2)
