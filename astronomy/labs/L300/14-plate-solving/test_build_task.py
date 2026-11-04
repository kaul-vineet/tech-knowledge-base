"""buildTask check (lesson 14): the solver must work away from the equator, with the TAN projection.

By default this checks solution/platesolve.py. To check your edited platesolve.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task -v        (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file 2 of 2 tests fail; after your fix both pass.
"""
import importlib.util
import os
import unittest
from pathlib import Path

import fields

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("platesolve.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/platesolve.py")
spec = importlib.util.spec_from_file_location("platesolve_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestTanProjection(unittest.TestCase):
    def test_both_fields_solve_to_sub_arcsecond_accuracy(self):
        for name in fields.FIELDS:
            r = target.run(name)
            with self.subTest(field=name):
                self.assertTrue(r["solved"])
                self.assertLess(r["rms_arcsec"], 0.6)
                self.assertLess(r["pointing_error_arcsec"], 1.0)
                self.assertAlmostEqual(r["rotation_deg"], fields.FIELDS[name]["rot_deg"], delta=0.05)

    def test_pixel_scale_is_the_camera_scale(self):
        for name in fields.FIELDS:
            r = target.run(name)
            with self.subTest(field=name):
                self.assertAlmostEqual(r.get("scale_arcsec_px", 0.0), fields.SCALE_ARCSEC, delta=0.001)


if __name__ == "__main__":
    unittest.main()
