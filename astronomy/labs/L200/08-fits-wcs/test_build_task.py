"""buildTask check (lesson 8): sky_to_pixel() must invert pixel_to_sky().

By default this checks solution/fitslite.py. To check your edited fitslite.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task -v        (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfinished) file all 3 tests fail (NotImplementedError); after your change all 3 pass.
"""
import importlib.util
import os
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("fitslite.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/fitslite.py")
spec = importlib.util.spec_from_file_location("fitslite_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestSkyToPixel(unittest.TestCase):
    def test_crval_maps_to_crpix(self):
        x, y = target.sky_to_pixel(target.WCS, 83.8221, -5.3911)
        self.assertAlmostEqual(float(x), 32.5, places=9)
        self.assertAlmostEqual(float(y), 32.5, places=9)

    def test_round_trip_whole_image(self):
        yy, xx = np.mgrid[1:65, 1:65].astype(float)
        ra, dec = target.pixel_to_sky(target.WCS, xx, yy)
        bx, by = target.sky_to_pixel(target.WCS, ra, dec)
        self.assertLess(max(np.abs(bx - xx).max(), np.abs(by - yy).max()), 1e-8)

    def test_round_trip_with_rotation(self):
        h = dict(target.WCS, CD1_1=-2.6e-4, CD1_2=1.0e-4, CD2_1=1.0e-4, CD2_2=2.6e-4, CRVAL2=60.0)
        ra, dec = target.pixel_to_sky(h, 10.0, 50.0)
        bx, by = target.sky_to_pixel(h, ra, dec)
        self.assertAlmostEqual(float(bx), 10.0, places=8)
        self.assertAlmostEqual(float(by), 50.0, places=8)


if __name__ == "__main__":
    unittest.main()
