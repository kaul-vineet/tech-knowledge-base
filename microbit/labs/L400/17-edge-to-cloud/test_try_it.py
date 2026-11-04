import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    """The observed tryIt results quoted in content/L400.json."""

    def test_try_1(self):
        self.assertEqual(try_it.try_1(), "delivered 480/480 (100.0%), p95 165 ms, gave_up 0, "
                                         "relay drops 0, sensor drops 176")

    def test_try_2(self):
        self.assertEqual(try_it.try_2(), "delivered 151/480 (31.5%), p95 19031 ms, gave_up 216, "
                                         "relay drops 570, sensor drops 15787")


if __name__ == "__main__":
    unittest.main(verbosity=2)
