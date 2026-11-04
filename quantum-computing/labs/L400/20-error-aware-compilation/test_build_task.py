"""Build-task check for lab 20 (noise-aware layout). Run: python -m unittest test_build_task -v

Checks solution_layout.py by default. Your file: my_layout.py with choose_layout(dev, budget=22) -> list of 5 physical qubits
  macOS:   BUILD_TARGET=mine python -m unittest test_build_task -v
  Windows: $env:BUILD_TARGET = "mine"; python -m unittest test_build_task -v
failureLab proof: BUILD_TASK_MODULE=compile_lab (trivial layout) FAILS test_beats_the_trivial_layout_by_far (ESP 0.2084).
"""
import unittest

import buildtarget
import compile_lab as lab
import device as D

mod = buildtarget.load("solution_layout", "my_layout")


class NoiseAwareLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = D.make_device(drift=D.DRIFT)
        cls.layout = mod.choose_layout(cls.dev)
        cls.m = lab.compile_circuit(cls.dev, cls.layout, weighted=True, optimise=True)[2]

    def test_valid_layout(self):
        self.assertEqual(len(set(self.layout)), lab.NQ)
        self.assertTrue(all(0 <= q < self.dev["n"] for q in self.layout))

    def test_beats_the_trivial_layout_by_far(self):
        self.assertGreaterEqual(self.m["esp"], 0.75)            # trivial: 0.2084

    def test_avoids_the_drifted_edge(self):
        ops = lab.compile_circuit(self.dev, self.layout, weighted=True, optimise=True)[0]
        self.assertNotIn((1, 2), {tuple(sorted(o[1])) for o in ops if o[0] == "cx"})


if __name__ == "__main__":
    unittest.main()
