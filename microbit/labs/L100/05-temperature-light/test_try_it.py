import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    """The observed tryIt results quoted in content/L100.json."""

    def test_try_1(self):
        self.assertEqual(try_it.try_1(), 'temp=27,light=128,state=ok')

    def test_try_2(self):
        self.assertEqual(try_it.try_2(), 'temp=30,light=10,state=hot')


if __name__ == "__main__":
    unittest.main(verbosity=2)
