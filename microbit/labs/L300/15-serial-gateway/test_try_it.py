import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import try_it  # noqa: E402


class TryIt(unittest.TestCase):
    """The observed tryIt results quoted in content/L300.json."""

    def test_try_1(self):
        self.assertEqual(try_it.try_1(),
                         'no CRC: forwarded 181, 2 WRONG, bad_crc 0, bad_payload 9 | with CRC: forwarded 179, 0 WRONG, bad_crc 13, bad_payload 0')

    def test_try_2(self):
        self.assertEqual(try_it.try_2(),
                         "forwarded 190 readings, 0 wrong; metrics {'frames_ok': 190, 'bad_len': 6, 'bad_crc': 3, 'bad_payload': 0, 'resyncs': 9, 'skipped_bytes': 184}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
