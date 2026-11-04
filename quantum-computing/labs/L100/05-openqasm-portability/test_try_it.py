"""Tests for lab 05 try-it items. Run: python -m unittest -v"""
import os
import unittest

import try_it

if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not try_it.HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit/qiskit-qasm3-import are not installed")


class TryItParser(unittest.TestCase):
    def test_swapped_control_breaks_the_bell_pair(self):
        self.assertEqual(try_it.parser_result("swap_control"), {"00": 0.5, "01": 0.5})

    def test_tiny_parser_rejects_gate_outside_its_subset(self):
        self.assertEqual(try_it.parser_result("add_s_gate"), "ValueError: unsupported statement: 's q[0]'")


@unittest.skipUnless(try_it.HAVE_QISKIT, "qiskit/qiskit-qasm3-import not installed (runs in CI)")
class TryItSdk(unittest.TestCase):
    def test_qiskit_reads_both_edits(self):
        self.assertEqual(try_it.qiskit_probabilities("swap_control"), {"00": 0.5, "01": 0.5})
        self.assertEqual(try_it.qiskit_probabilities("add_s_gate"), {"00": 0.5, "11": 0.5})  # S only adds a phase


if __name__ == "__main__":
    unittest.main()
