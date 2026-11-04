import unittest

import sky_numbers as sn


class TestSkyNumbers(unittest.TestCase):
    def test_two_magnitudes_is_6_31(self):
        self.assertAlmostEqual(sn.flux_ratio(5, 7), 6.3096, places=4)

    def test_lower_orbits_enter_shadow_earlier(self):
        self.assertLess(sn.max_sunlit_depression(350), sn.max_sunlit_depression(550))
        self.assertAlmostEqual(sn.max_sunlit_depression(550), 23.0, delta=0.05)

    def test_release_must_keep_nc(self):
        self.assertFalse(sn.release_ok(["CC-BY-NC-3.0-IGO"], "CC-BY-4.0")[0])
        self.assertTrue(sn.release_ok(["CC-BY-NC-3.0-IGO"], "CC-BY-NC-4.0")[0])
        self.assertFalse(sn.release_ok(["CC-BY-NC-3.0-IGO", "CC-BY-SA-4.0"], "CC-BY-NC-4.0")[0])


if __name__ == "__main__":
    unittest.main()
