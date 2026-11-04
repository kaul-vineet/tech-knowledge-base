import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    """The observed tryIt results quoted in content/L100.json."""

    def test_try_1(self):
        self.assertEqual(try_it.try_1(), "count=1, serial='count 1\\n'")

    def test_try_2(self):
        self.assertEqual(try_it.try_2(), "after 3 clicks: count=0 serial=''; held for 3 polls: count=3 serial='count 1\\ncount 2\\ncount 3\\n'")


if __name__ == "__main__":
    unittest.main(verbosity=2)
