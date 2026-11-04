import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    """The observed tryIt results quoted in content/L300.json."""

    def test_try_1(self):
        self.assertEqual(try_it.try_1(),
                         "racy, short window: irqs 1039, isr runs 1039, consumed 1000, pending 0, lost 39")

    def test_try_2(self):
        self.assertEqual(try_it.try_2(),
                         "fixed, long section: irqs 1632, isr runs 1316, consumed 1316, pending 0, lost 0")


if __name__ == "__main__":
    unittest.main(verbosity=2)
