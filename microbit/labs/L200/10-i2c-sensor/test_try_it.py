import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    """The observed tryIt results quoted in content/L200.json."""

    def test_try_1(self):
        self.assertEqual(try_it.try_1(), 'i2c: no device at 0x49 (errno 19)')

    def test_try_2(self):
        self.assertEqual(try_it.try_2(), 'temp_c=231.00')


if __name__ == "__main__":
    unittest.main(verbosity=2)
