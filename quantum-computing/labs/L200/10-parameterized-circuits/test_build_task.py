"""Build-task check for lab 10. Run: python -m unittest test_build_task -v

Checks solution_offset.py by default; to check your own file set BUILD_TASK_MODULE, e.g.
  macOS:   BUILD_TASK_MODULE=my_offset python -m unittest test_build_task -v
  Windows: $env:BUILD_TASK_MODULE = "my_offset"; python -m unittest test_build_task -v
"""
import importlib
import importlib.util
import os
import unittest

mod = importlib.import_module(os.environ.get("BUILD_TASK_MODULE", "solution_offset"))
HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None


class OffsetNumpy(unittest.TestCase):
    def test_exact_recovery(self):
        for phi in (-1.0, 0.0, 0.3, 2.0):
            self.assertAlmostEqual(mod.offset_numpy(phi), phi, places=2)

    def test_recovery_from_shots(self):
        self.assertLess(abs(mod.offset_numpy(0.3, shots=400) - 0.3), 0.05)


@unittest.skipUnless(HAVE_QISKIT, "qiskit not installed (runs in CI)")
class OffsetSdk(unittest.TestCase):
    def test_partial_binding_and_recovery(self):
        free, phi = mod.offset_qiskit(0.3)
        self.assertEqual(free, 1)
        self.assertAlmostEqual(phi, 0.3, places=2)


if __name__ == "__main__":
    unittest.main()
