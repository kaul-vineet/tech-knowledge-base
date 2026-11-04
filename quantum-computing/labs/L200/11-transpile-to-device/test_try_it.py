"""Tests for lab 11 try-it items. Run: python -m unittest -v"""
import os
import unittest

import try_it

if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not try_it.HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class TryItLocal(unittest.TestCase):
    def test_ring_needs_less_routing_than_line(self):
        self.assertEqual(try_it.ring_vs_line_local(), {"all-to-all": 0, "ring": 2, "line": 3})

    def test_h_in_rz_sx_basis(self):
        self.assertEqual(try_it.h_in_basis_local(),
                         {"gates": ["rz", "sx", "rz"], "equals_H_up_to_phase": True, "global_phase_turns": -0.125})


@unittest.skipUnless(try_it.HAVE_QISKIT, "qiskit not installed (runs in CI)")
class TryItSdk(unittest.TestCase):
    def test_qiskit(self):
        out = try_it.sdk_results()
        self.assertLessEqual(out["level0_2q"]["ring"], out["level0_2q"]["line"])
        self.assertLessEqual(set(out["h_ops"]), {"rz", "sx", "x"})
        self.assertTrue(out["h_equiv"])


if __name__ == "__main__":
    unittest.main()
