"""buildTask check (lesson 9): calibrate() returns (magnitude, error) per star from one reference star.

By default this checks solution/photometry.py. To check your edited photometry.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task -v        (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfinished) file all 3 tests fail (NotImplementedError); after your change all 3 pass.
"""
import importlib.util
import math
import os
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("photometry.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/photometry.py")
spec = importlib.util.spec_from_file_location("photometry_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)

RESULTS = [{"net": 20000.0, "snr": 100.0}, {"net": 2000.0, "snr": 20.0}, {"net": -50.0, "snr": -0.5}]


class TestCalibrate(unittest.TestCase):
    def test_reference_star_gets_its_catalogue_magnitude(self):
        self.assertAlmostEqual(target.calibrate(RESULTS, 0, 10.0)[0][0], 10.0, places=12)

    def test_ten_times_fainter_is_2_5_mag_and_error_from_snr(self):
        mag, err = target.calibrate(RESULTS, 0, 10.0)[1]
        self.assertAlmostEqual(mag, 12.5, places=12)
        self.assertAlmostEqual(err, 1.0857 / 20, places=4)

    def test_non_detection_is_nan_not_a_crash(self):
        mag, _ = target.calibrate(RESULTS, 0, 10.0)[2]
        self.assertTrue(math.isnan(mag))


if __name__ == "__main__":
    unittest.main()
