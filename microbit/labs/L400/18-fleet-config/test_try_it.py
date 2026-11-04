import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    """The observed tryIt results quoted in content/L400.json."""

    def test_try_1(self):
        self.assertEqual(try_it.try_1(), "jobs: v2 halted @3310, v3 halted @18310 | final versions 111111 | unacked_ticks 0")

    def test_try_2(self):
        self.assertEqual(try_it.try_2(), "jobs: v2 halted @8920, v3 halted @16810 | final versions 111111 | unacked_ticks 0")


if __name__ == "__main__":
    unittest.main(verbosity=2)
