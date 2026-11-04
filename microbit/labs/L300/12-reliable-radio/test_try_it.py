import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    """The observed tryIt results quoted in content/L300.json."""

    def test_try_1(self):
        self.assertEqual(try_it.try_1(),
                         'delivered 20/20, missing none, duplicates 19, in order False | sender retx 22 gave_up 0 | receiver gap -19')

    def test_try_2(self):
        self.assertEqual(try_it.try_2(),
                         'delivered 20/20, missing none, duplicates 0, in order True | sender retx 13 gave_up 4 | receiver gap 0')


if __name__ == "__main__":
    unittest.main(verbosity=2)
