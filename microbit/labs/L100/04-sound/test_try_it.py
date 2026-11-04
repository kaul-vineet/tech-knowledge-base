import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    """The observed tryIt results quoted in content/L100.json."""

    def test_try_1(self):
        self.assertEqual(try_it.try_1(), 'variant 16 ticks = 2000 ms (original 20 ticks = 2500 ms)')

    def test_try_2(self):
        self.assertEqual(try_it.try_2(), "serial='speaker off\\ntune played\\n', music.play calls=1, speaker_on during play=False")


if __name__ == "__main__":
    unittest.main(verbosity=2)
