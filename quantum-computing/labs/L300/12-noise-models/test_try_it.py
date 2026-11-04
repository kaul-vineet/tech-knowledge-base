"""Tests for lab 12 try-it items. Run: python -m unittest -v"""
import os
import unittest

import try_it

if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not try_it.HAVE_AER:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit-aer is not installed")


class TryItNumpy(unittest.TestCase):
    def test_symmetric_noise_removes_imbalance(self):
        self.assertEqual(try_it.symmetric_noise(), {"p_all0": 0.4454, "p_all1": 0.4454})

    def test_readout_costs_more_than_cx_noise_here(self):
        self.assertEqual(try_it.readout_vs_gate_noise(), {"readout_only": 0.8145, "cx_only": 0.9037})


@unittest.skipUnless(try_it.HAVE_AER, "qiskit-aer not installed (runs in CI)")
class TryItSdk(unittest.TestCase):
    def test_aer_agrees(self):
        out = try_it.sdk_results()
        self.assertAlmostEqual(out["readout_only"], 0.8145, delta=0.02)
        self.assertAlmostEqual(out["cx_only"], 0.9037, delta=0.02)


if __name__ == "__main__":
    unittest.main()
