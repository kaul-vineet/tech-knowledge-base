import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    """The observed tryIt results quoted in content/L400.json."""

    def test_try_1(self):
        self.assertEqual(try_it.try_1(), "genuine accepted 159 of 160 intact, forged accepted 0, replays accepted 0")

    def test_try_2(self):
        self.assertEqual(try_it.try_2(), "genuine accepted 143 of 160 intact, forged accepted 0, replays accepted 0")


if __name__ == "__main__":
    unittest.main(verbosity=2)
