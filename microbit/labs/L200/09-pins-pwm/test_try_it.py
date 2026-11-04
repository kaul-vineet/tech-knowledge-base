import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    """The observed tryIt results quoted in content/L200.json."""

    def test_try_1(self):
        self.assertEqual(try_it.try_1(), 'on=1,level=2,duty=511 | on=0,level=2,duty=0 | on=1,level=2,duty=511')

    def test_try_2(self):
        self.assertEqual(try_it.try_2(), 'on=1,level=2,duty=682 | duty_for(0..3) = [0, 341, 682, 1023]')


if __name__ == "__main__":
    unittest.main(verbosity=2)
