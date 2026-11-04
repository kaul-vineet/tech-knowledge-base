"""Stretch check (lesson 13): gain and read noise measured from bias/flat pairs match the camera within 6%.

Checks solution/gain.py; BUILD_TARGET=mine checks gain.py in this folder (your copy).
"""
import importlib.util
import os
import unittest
from pathlib import Path

import camera

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("gain.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/gain.py")
spec = importlib.util.spec_from_file_location("gain_under_test", TARGET)
gain = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gain)


class TestPhotonTransfer(unittest.TestCase):
    def test_gain_and_read_noise_for_five_nights(self):
        for seed in range(20, 25):
            g, rn = gain.gain_and_read_noise(camera.frames(seed))
            with self.subTest(seed=seed):
                self.assertAlmostEqual(g / camera.GAIN, 1.0, delta=0.06)
                self.assertAlmostEqual(rn / camera.READ_E, 1.0, delta=0.06)


if __name__ == "__main__":
    unittest.main()
