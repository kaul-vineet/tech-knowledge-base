import importlib.util
import tempfile
import unittest
from pathlib import Path

import numpy as np

import fitslite as fl
from field import synthetic_field


class TestFitsFile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "t.fits"

    def tearDown(self):
        self.tmp.cleanup()

    def test_round_trip_and_block_size(self):
        img = synthetic_field()
        fl.write_fits(self.path, img, fl.WCS)
        self.assertEqual(self.path.stat().st_size % fl.BLOCK, 0)
        h, data = fl.read_fits(self.path)
        self.assertTrue(np.array_equal(data, img))
        self.assertEqual((h["NAXIS1"], h["CTYPE1"], h["CD2_2"]), (64, "RA---TAN", 2.7778e-4))

    def test_integer_image_and_big_endian_bytes(self):
        img = np.arange(6, dtype=np.int16).reshape(2, 3)
        fl.write_fits(self.path, img, {})
        raw = self.path.read_bytes()
        self.assertEqual(raw[fl.BLOCK:fl.BLOCK + 4], b"\x00\x00\x00\x01")  # 0 then 1, most significant byte first
        h, data = fl.read_fits(self.path)
        self.assertEqual((h["NAXIS1"], h["NAXIS2"]), (3, 2))  # NAXIS1 = number of columns
        self.assertTrue(np.array_equal(data, img))

    def test_cards_are_80_chars(self):
        self.assertEqual(len(fl.card("CTYPE1", "RA---TAN")), 80)
        self.assertEqual(fl.card("CTYPE1", "RA---TAN")[10], "'")  # string starts in column 11


class TestWcs(unittest.TestCase):
    def test_reference_pixel_maps_to_crval(self):
        ra, dec = fl.pixel_to_sky(fl.WCS, 32.5, 32.5)
        self.assertAlmostEqual(float(ra), 83.8221, places=10)
        self.assertAlmostEqual(float(dec), -5.3911, places=10)

    def test_pixel_scale_is_one_arcsec(self):
        ra1, dec1 = fl.pixel_to_sky(fl.WCS, 32.5, 32.5)
        ra2, dec2 = fl.pixel_to_sky(fl.WCS, 32.5, 33.5)
        self.assertAlmostEqual(float(dec2 - dec1) * 3600, 1.0, places=3)

    def test_east_is_left(self):
        ra_left, _ = fl.pixel_to_sky(fl.WCS, 1, 32.5)
        self.assertGreater(float(ra_left), 83.8221)  # CD1_1 < 0: RA increases to the left


@unittest.skipUnless(importlib.util.find_spec("astropy"), "astropy not installed (runs in CI)")
class TestAstropyEquivalent(unittest.TestCase):
    def test_astropy_reads_our_file_and_agrees(self):
        import fits_astropy
        same, max_err_arcsec = fits_astropy.compare()
        self.assertTrue(same)
        self.assertLess(max_err_arcsec, 1e-6)


if __name__ == "__main__":
    unittest.main()
