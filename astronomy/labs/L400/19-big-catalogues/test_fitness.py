"""Fitness function (lesson 19, ADR 0001): keeps "declination zones of 1 degree + exact test" true.

The chosen index (CoarseZones, h = 1.0) must agree with brute force on all 600 test cones (incl. 50 near the
poles and 50 across RA = 0), build in < 10 s, and answer >= 10x faster than brute force on the same cones
(best of 3; the sandbox measured ~45-200x). Wall-clock bounds are generous; run 3x.
Default target: solution/catalog.py; BUILD_TARGET=mine checks your catalog.py (the shipped file fails).
"""
import importlib.util
import os
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("catalog.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/catalog.py")
spec = importlib.util.spec_from_file_location("catalog_fitness", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestCatalogueFitness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat, cls.cones = target.make_catalogue(), target.test_cones()
        cls.brute = target.Brute(cls.cat)
        t0 = time.perf_counter()
        cls.index = target.CoarseZones(cls.cat)
        cls.build_s = time.perf_counter() - t0
        cls.ref, cls.ms_brute, _ = target.measure(cls.brute, cls.cones)

    def test_exact_on_every_cone(self):
        self.assertEqual(target.measure(self.index, self.cones, self.ref)[2], 0)

    def test_build_time(self):
        self.assertLess(self.build_s, 10.0)

    def test_speedup(self):
        best = min(target.measure(self.index, self.cones)[1] for _ in range(3))
        self.assertGreaterEqual(self.ms_brute / best, 10.0)


if __name__ == "__main__":
    unittest.main()
