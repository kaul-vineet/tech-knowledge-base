"""buildTask check (lesson 19): the zone index must return exactly the brute-force answer on every cone.

By default this checks solution/catalog.py. To check your edited catalog.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v      (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file both build-task tests fail; after your fix they pass.
"""
import importlib.util
import os
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("catalog.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/catalog.py")
spec = importlib.util.spec_from_file_location("catalog_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestExactConeSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = target.make_catalogue(200_000)
        cls.brute, cls.zones = target.Brute(cls.cat), target.Zones(cls.cat)

    def check(self, cones):
        for c in cones:
            with self.subTest(cone=tuple(round(float(v), 3) for v in c)):
                np.testing.assert_array_equal(self.zones.query(*c), self.brute.query(*c))

    def test_high_declination_and_poles(self):
        self.check([(10.0, 75.0, 1.0), (200.0, -88.0, 0.8), (33.0, 89.6, 0.5), (300.0, -60.0, 2.0)])

    def test_ra_wrap(self):
        self.check([(0.1, 5.0, 0.6), (359.9, -20.0, 0.6), (0.0, 45.0, 1.0)])


if __name__ == "__main__":
    unittest.main()
