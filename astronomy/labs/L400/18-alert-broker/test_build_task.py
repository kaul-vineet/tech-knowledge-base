"""buildTask check (lesson 18): difference() must match the PSF and the transparency before subtracting.

By default this checks solution/alerts.py. To check your edited alerts.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v      (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file test_constant_stars_vanish and the fitness test test_alert_volume_and_purity fail
(the supernova is bright enough to survive either way); after your fix all 6 pass.
"""
import importlib.util
import os
import unittest
from pathlib import Path

import numpy as np

import alert_sim as sim

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("alerts.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/alerts.py")
spec = importlib.util.spec_from_file_location("alerts_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestMatchedDifference(unittest.TestCase):
    def test_constant_stars_vanish(self):
        """Same stars, worse seeing and 20% less transparency, no noise: the difference must be ~0."""
        x, y, f = sim.stars()
        ref = sim.render(zip(x, y, f), sim.REF_SIGMA)
        new = sim.render(zip(x, y, 0.8 * f), 1.9)
        resid = target.difference(new, ref, 1.9)
        self.assertLess(float(np.abs(resid).max()), 0.02 * float(np.abs(new - sim.SKY).max()))

    def test_supernova_survives(self):
        e = sim.nights()[10]  # night 5, exposure a
        d = target.difference(e["image"], sim.reference(), e["sigma"])
        self.assertGreater(float(d[90, 40]), 8 * 1.4826 * float(np.median(np.abs(d - np.median(d)))))


if __name__ == "__main__":
    unittest.main()
