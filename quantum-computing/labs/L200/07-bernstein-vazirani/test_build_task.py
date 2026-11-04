"""Build-task check for lab 07. Run: python -m unittest test_build_task -v

Checks solution_bias.py by default; to check your own file set BUILD_TASK_MODULE, e.g.
  macOS:   BUILD_TASK_MODULE=my_bias python -m unittest test_build_task -v
  Windows: $env:BUILD_TASK_MODULE = "my_bias"; python -m unittest test_build_task -v
"""
import importlib
import importlib.util
import itertools
import os
import unittest

mod = importlib.import_module(os.environ.get("BUILD_TASK_MODULE", "solution_bias"))
HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None


class BiasNumpy(unittest.TestCase):
    def test_bias_never_changes_the_answer(self):
        for bits in itertools.product("01", repeat=3):
            secret = "".join(bits)
            for bias in (0, 1):
                self.assertEqual(mod.recovered_numpy(secret, bias), {secret: 1.0}, (secret, bias))


@unittest.skipUnless(HAVE_QISKIT, "qiskit not installed (runs in CI)")
class BiasSdk(unittest.TestCase):
    def test_qiskit_oracle_with_bias(self):
        import bv_lab
        qc = bv_lab.bv_circuit(mod.bv_oracle_with_bias("1011", 1))
        self.assertEqual(bv_lab.run(qc), {"1011": 100})


if __name__ == "__main__":
    unittest.main()
