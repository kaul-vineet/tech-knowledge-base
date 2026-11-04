import importlib.util
import unittest

import numpy as np

import photometry as ph


class TestApertureGeometry(unittest.TestCase):
    def test_area_close_to_pi_r_squared(self):
        w = ph.aperture_weights((41, 41), 20.3, 19.7, 6.0)
        self.assertAlmostEqual(w.sum() / (np.pi * 36), 1.0, delta=0.01)

    def test_weights_between_zero_and_one(self):
        w = ph.aperture_weights((21, 21), 10.0, 10.0, 3.0)
        self.assertTrue(((w >= 0) & (w <= 1)).all())


class TestPhotometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.img = ph.make_image()
        cls.res = [ph.measure(cls.img, x, y) for x, y, _ in ph.STARS]

    def test_background_recovered(self):
        for r in self.res:
            self.assertAlmostEqual(r["bkg"], ph.SKY, delta=2.0)

    def test_flux_within_three_sigma(self):
        for (_, _, flux), r in zip(ph.STARS, self.res):
            self.assertLess(abs(r["net"] - flux), 3 * r["net"] / r["snr"] + 3 * np.sqrt(flux))

    def test_snr_falls_with_flux(self):
        snr = [r["snr"] for r in self.res]
        self.assertEqual(snr, sorted(snr, reverse=True))

    def test_bright_star_printed_values(self):
        self.assertEqual((f"{self.res[0]['net']:.1f}", f"{self.res[0]['snr']:.1f}"), ("20006.2", "102.6"))

    def test_noise_free_image_is_exact(self):
        yy, xx = np.mgrid[0:101, 0:101]
        model = ph.SKY + 5000 / (2 * np.pi * ph.SIGMA**2) * np.exp(-((xx - 50) ** 2 + (yy - 50) ** 2) / (2 * ph.SIGMA**2))
        self.assertAlmostEqual(ph.measure(model, 50, 50)["net"] / 5000, 1 - np.exp(-36 / (2 * ph.SIGMA**2)), delta=0.002)


@unittest.skipUnless(importlib.util.find_spec("photutils"), "photutils not installed (runs in CI)")
class TestPhotutilsEquivalent(unittest.TestCase):
    def test_photutils_agrees(self):
        import photometry_photutils
        for ours, theirs in photometry_photutils.compare():
            self.assertAlmostEqual(theirs / ours, 1.0, delta=0.01)


if __name__ == "__main__":
    unittest.main()
