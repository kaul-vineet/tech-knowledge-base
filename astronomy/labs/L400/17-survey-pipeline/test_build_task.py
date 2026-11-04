"""buildTask check (lesson 17): background() must follow the sky across the frame (mesh, not one level).

By default this checks solution/survey.py. To check your edited survey.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v      (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file both build-task tests fail; after your fix they pass.
"""
import importlib.util
import os
import unittest
from pathlib import Path

import numpy as np

import survey_sim as sim

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("survey.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/survey.py")
spec = importlib.util.spec_from_file_location("survey_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestMeshBackground(unittest.TestCase):
    def test_background_error_below_two_percent_of_sky(self):
        rng = np.random.default_rng(3)
        sky = np.stack([sim.SKY + rng.normal(0, 20, sim.SKY.shape) for _ in range(2)])
        err = np.abs(target.background(sky) - sim.SKY) / sim.SKY
        self.assertLess(float(np.percentile(err, 99)), 0.02)

    def test_completeness_on_the_night(self):
        raws, bias, flat, truth = sim.night()
        rows, _, _ = target.run("A", raws, bias, flat)
        self.assertGreaterEqual(target.score(rows, truth)[0], 0.95)


if __name__ == "__main__":
    unittest.main()
