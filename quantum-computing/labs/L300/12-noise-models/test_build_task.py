"""Build-task check for lab 12 (the hardening change). Run: python -m unittest test_build_task -v

Checks solution_tolerant_check.py by default; to check your own file set BUILD_TASK_MODULE, e.g.
  macOS:   BUILD_TASK_MODULE=my_check python -m unittest test_build_task -v
  Windows: $env:BUILD_TASK_MODULE = "my_check"; python -m unittest test_build_task -v
failureLab proof: BUILD_TASK_MODULE=noise_lab (the naive check) FAILS test_correct_circuit_passes_on_noisy_device.
"""
import importlib
import os
import unittest

import numpy as np

import noise_lab as lab
from qsim import density as dm
from qsim import statevector as sv

mod = importlib.import_module(os.environ.get("BUILD_TASK_MODULE", "solution_tolerant_check"))


def counts_for(ops, n, seed, shots=2000):
    rho = dm.run(n, lab.noisy_steps(ops, lab.NOISE))
    probs = dm.readout_matrix(lab.NOISE["p01"], lab.NOISE["p10"], n) @ dm.probabilities(rho)
    return dm.sample(probs, shots, np.random.default_rng(seed))


class HardenedCheck(unittest.TestCase):
    def test_correct_circuit_passes_on_noisy_device(self):
        for n in (2, 3):
            for seed in range(20):
                self.assertTrue(mod.bell_check(lab.counts(n, lab.NOISE, seed=seed), n=n), f"n={n} seed={seed}")

    def test_ideal_simulator_still_passes(self):
        self.assertTrue(mod.bell_check(lab.counts(2, lab.IDEAL), n=2, noise=lab.IDEAL))

    def test_missing_cx_is_caught(self):
        self.assertFalse(mod.bell_check(counts_for([sv.h(0)], 2, seed=1), n=2))

    def test_missing_h_is_caught(self):
        self.assertFalse(mod.bell_check(counts_for([sv.cx(0, 1)], 2, seed=1), n=2))

    def test_broken_ghz_link_is_caught(self):
        self.assertFalse(mod.bell_check(counts_for([sv.h(0), sv.cx(0, 1)], 3, seed=1), n=3))


if __name__ == "__main__":
    unittest.main()
