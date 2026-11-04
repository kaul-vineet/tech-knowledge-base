"""Build-task check for lab 13 (the hardening change). Run: python -m unittest test_build_task -v

Checks solution_constrained.py by default; to check your own file set BUILD_TASK_MODULE, e.g.
  macOS:   BUILD_TASK_MODULE=my_mitigation python -m unittest test_build_task -v
  Windows: $env:BUILD_TASK_MODULE = "my_mitigation"; python -m unittest test_build_task -v
failureLab proof: BUILD_TASK_MODULE=mitigation_lab (plain inverse) FAILS test_always_a_probability_distribution.
"""
import importlib
import os
import unittest

import numpy as np

import mitigation_lab as lab

mod = importlib.import_module(os.environ.get("BUILD_TASK_MODULE", "solution_constrained"))


def runs(cal_shots, shots, seeds=100):
    for seed in range(seeds):
        rng = np.random.default_rng(seed)
        m_est = lab.calibrate(cal_shots, rng)
        p_noisy = lab.measure(lab.true_bell(), shots, rng)
        yield p_noisy, m_est


class ConstrainedMitigation(unittest.TestCase):
    def test_always_a_probability_distribution(self):
        for budget in ((100, 200), (4000, 4000)):
            for p_noisy, m_est in runs(*budget):
                p = mod.mitigate(p_noisy, m_est)
                self.assertGreaterEqual(p.min(), 0.0, budget)
                self.assertAlmostEqual(float(p.sum()), 1.0, places=9)

    def test_not_worse_than_plain_inverse(self):
        ideal = lab.true_bell()
        for budget in ((100, 200), (4000, 4000)):
            ours = np.mean([lab.tvd(mod.mitigate(p, m), ideal) for p, m in runs(*budget)])
            plain = np.mean([lab.tvd(lab.mitigate(p, m), ideal) for p, m in runs(*budget)])
            self.assertLessEqual(ours, plain + 1e-9, budget)

    def test_more_shots_beat_raw_readout(self):
        ideal = lab.true_bell()
        for p_noisy, m_est in runs(4000, 4000, seeds=20):
            self.assertLess(lab.tvd(mod.mitigate(p_noisy, m_est), ideal), lab.tvd(p_noisy, ideal))


if __name__ == "__main__":
    unittest.main()
