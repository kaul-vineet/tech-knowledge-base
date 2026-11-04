"""Tests for lab 01. Run: python -m unittest -v   (from this folder)

SDK tests are skipped when qiskit is not installed, unless REQUIRE_QUANTUM_SDKS=1 (set in CI).
"""
import importlib.util
import os
import sys
import unittest

import crosscheck_numpy

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None
if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class CrossCheck(unittest.TestCase):
    def test_x_flips_zero_to_one(self):
        self.assertEqual(crosscheck_numpy.x_then_measure_probabilities(), {"0": 0.0, "1": 1.0})


@unittest.skipUnless(HAVE_QISKIT, "qiskit not installed (runs in CI)")
class SdkLab(unittest.TestCase):
    def test_python_version(self):
        self.assertGreaterEqual(sys.version_info[:2], (3, 11))

    def test_pinned_versions_installed(self):
        import check_env
        found = check_env.installed_versions()
        for name in ("qiskit", "qiskit-qasm3-import"):
            self.assertEqual(found[name], check_env.PINNED[name], name)

    def test_one_qubit_circuit_matches_numpy(self):
        import check_env
        counts = check_env.run_one_qubit(shots=100)
        expected = {k: round(p * 100) for k, p in crosscheck_numpy.x_then_measure_probabilities().items() if p > 0}
        self.assertEqual(counts, expected)  # X is deterministic: {'1': 100}


if __name__ == "__main__":
    unittest.main()
