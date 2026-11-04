import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    """The observed tryIt results quoted in content/L100.json."""

    def test_try_1(self):
        self.assertEqual(try_it.try_1(), "'hello from micro:bit\\ntick 1\\ntick 2\\ntick 3\\ntick 4\\n', running_time()=1000 ms")

    def test_try_2(self):
        self.assertEqual(try_it.try_2(), "import returned=False, serial='hello from micro:bit\\ntick 1\\ntick 2\\ntick 3\\n'")


if __name__ == "__main__":
    unittest.main(verbosity=2)
