import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    """The observed tryIt results quoted in content/L400.json."""

    def test_try_1(self):
        self.assertEqual(try_it.try_1(), '{"n3 DRIFT_TEMP": 10, "n5 DRIFT_LAT": 9} | false alarms: fixture 3, synthetic 12 per 1000')

    def test_try_2(self):
        self.assertEqual(try_it.try_2(), '{"n3 DRIFT_TEMP": 5} | false alarms: fixture 6, synthetic 74 per 1000')


if __name__ == "__main__":
    unittest.main(verbosity=2)
