"""buildTask check (lesson 11): to_com_frame() must put the system in the centre-of-mass frame.

By default this checks solution/nbody.py. To check your edited nbody.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task -v        (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfinished) file 3 of 3 tests fail; after your change all 3 pass.
"""
import importlib.util
import os
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("nbody.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/nbody.py")
spec = importlib.util.spec_from_file_location("nbody_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestCentreOfMassFrame(unittest.TestCase):
    def test_total_momentum_is_zero(self):
        pos, vel = target.to_com_frame(*target.initial_state(), target.MASSES)
        self.assertLess(np.abs(target.MASSES @ vel).max(), 1e-15)

    def test_centre_of_mass_at_origin(self):
        pos, vel = target.to_com_frame(*target.initial_state(), target.MASSES)
        self.assertLess(np.abs(target.MASSES @ pos).max(), 1e-15)

    def test_system_no_longer_drifts(self):
        _, _, _, com_shift = target.run(target.step_leapfrog, years=2.0, dt=0.002)
        self.assertLess(com_shift, 1e-9)


if __name__ == "__main__":
    unittest.main()
