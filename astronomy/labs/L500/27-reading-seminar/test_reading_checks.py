import unittest

import reading_checks as rc


class TestReadingChecks(unittest.TestCase):
    def test_hubble_time_for_k_500(self):
        self.assertAlmostEqual(rc.hubble_time_gyr(500), 1.956, places=3)

    def test_ngc7619_absolute_magnitude_matches_paper(self):
        self.assertAlmostEqual(rc.abs_mag(11.8, 7.8), -17.65, delta=0.02)


if __name__ == "__main__":
    unittest.main()
