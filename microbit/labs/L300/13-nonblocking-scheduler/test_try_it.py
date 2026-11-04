import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    """The observed tryIt results quoted in content/L300.json."""

    def test_try_1(self):
        self.assertEqual(try_it.try_1(),
                         "counted 6 of 8 | stats {'runs': 160, 'overruns': 0, 'missed': 0, 'errors': 0} | events none")

    def test_try_2(self):
        self.assertEqual(try_it.try_2(),
                         "counted 8 of 8 | stats {'runs': 440, 'overruns': 10, 'missed': 170, 'errors': 0} | events ['late', 'overrun']")


if __name__ == "__main__":
    unittest.main(verbosity=2)
