import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    """The observed tryIt results quoted in content/L100.json."""

    def test_try_1(self):
        self.assertEqual(try_it.try_1(), 'x=200,y=0,z=-1024,tilt=right,gesture=')

    def test_try_2(self):
        self.assertEqual(try_it.try_2(), "'shake!' printed 3 time(s) in 3 polls")


if __name__ == "__main__":
    unittest.main(verbosity=2)
