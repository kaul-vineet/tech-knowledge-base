"""Fitness function for lab 20: the compiled circuit stays within the depth budget (docs/adr/0001-noise-aware-compile.md).
Run: python -m unittest test_fitness -v    (same BUILD_TARGET / BUILD_TASK_MODULE switch as test_build_task)

Thresholds on both the calibrated and the drifted device: depth <= 22 · ESP >= 0.75 · CX <= 20 ·
noiseless output identical to the logical circuit.
"""
import unittest

import buildtarget
import compile_lab as lab
import device as D
import noisy_check as nc

mod = buildtarget.load("solution_layout", "my_layout")


class CompiledCircuitFitness(unittest.TestCase):
    def check(self, dev):
        ops, final, m = lab.compile_circuit(dev, mod.choose_layout(dev), weighted=True, optimise=True)
        self.assertLessEqual(m["depth"], lab.DEPTH_BUDGET)
        self.assertGreaterEqual(m["esp"], 0.75)
        self.assertLessEqual(m["cx"], 20)
        self.assertTrue(nc.equivalent(ops, final))

    def test_calibrated_device(self):
        self.check(D.make_device())

    def test_drifted_device(self):
        self.check(D.make_device(drift=D.DRIFT))


if __name__ == "__main__":
    unittest.main()
