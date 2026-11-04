import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    """The observed tryIt results quoted in content/L400.json."""

    def test_try_1(self):
        self.assertEqual(try_it.try_1(), "alarm sets changed 0/200, replies published 35, "
                                         "published notes claiming a state change 18")

    def test_try_2(self):
        self.assertEqual(try_it.try_2(), "alarm sets changed 0/200, replies published 79, "
                                         "published notes claiming a state change 0")


if __name__ == "__main__":
    unittest.main(verbosity=2)
