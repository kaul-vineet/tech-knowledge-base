"""Tests for lab 08 try-it items. Run: python -m unittest -v"""
import os
import unittest

import try_it

if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not try_it.HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class TryItNumpy(unittest.TestCase):
    def test_one_more_iteration_overshoots(self):
        self.assertEqual(try_it.numpy_success("overshoot"), {"k": 3, "P": 0.3301, "optimal_k": 2, "P_at_optimal": 0.9453})

    def test_more_marked_states_need_fewer_iterations(self):
        self.assertEqual(try_it.numpy_success("two_marked_k2"), {"k": 2, "P": 0.25, "optimal_k": 1, "P_at_optimal": 1.0})


@unittest.skipUnless(try_it.HAVE_QISKIT, "qiskit not installed (runs in CI)")
class TryItSdk(unittest.TestCase):
    def test_qiskit_matches_numpy(self):
        self.assertAlmostEqual(try_it.sdk_success("overshoot"), 0.3301, places=3)
        self.assertAlmostEqual(try_it.sdk_success("two_marked_k2"), 0.25, places=3)


if __name__ == "__main__":
    unittest.main()
