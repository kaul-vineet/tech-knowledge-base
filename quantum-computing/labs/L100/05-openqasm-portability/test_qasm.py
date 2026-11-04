"""Tests for lab 05. Run: python -m unittest -v   (from this folder)"""
import importlib.util
import os
import unittest
from pathlib import Path

import crosscheck_qasm_numpy

HERE = Path(__file__).resolve().parent
BELL = {"00": 0.5, "11": 0.5}
HAVE_QISKIT = all(importlib.util.find_spec(m) for m in ("qiskit", "qiskit_qasm3_import"))
if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit/qiskit-qasm3-import are not installed")


def _read(name):
    return (HERE / name).read_text(encoding="utf-8")


class CrossCheck(unittest.TestCase):
    def test_reference_files(self):
        self.assertEqual(crosscheck_qasm_numpy.probabilities(_read("reference_bell_qasm3.qasm")), BELL)
        self.assertEqual(crosscheck_qasm_numpy.probabilities(_read("reference_bell_qasm2.qasm")), BELL)

    def test_physical_qubits_and_x(self):
        text = 'OPENQASM 3.0; include "stdgates.inc"; x $0;'
        self.assertEqual(crosscheck_qasm_numpy.probabilities(text), {"1": 1.0})

    def test_unknown_statement_rejected(self):
        with self.assertRaises(ValueError):
            crosscheck_qasm_numpy.probabilities("OPENQASM 3.0; qubit[1] q; rz(0.1) q[0];")


@unittest.skipUnless(HAVE_QISKIT, "qiskit/qiskit-qasm3-import not installed (runs in CI)")
class SdkLab(unittest.TestCase):
    def test_qasm3_text_is_openqasm3(self):
        import qasm_lab
        text, _ = qasm_lab.roundtrip_qasm3(qasm_lab.bell_circuit())
        self.assertTrue(text.lstrip().startswith("OPENQASM 3"))
        self.assertIn('include "stdgates.inc"', text)

    def test_exported_text_readable_by_independent_parser(self):
        import qasm_lab
        for roundtrip in (qasm_lab.roundtrip_qasm3, qasm_lab.roundtrip_qasm2):
            text, _ = roundtrip(qasm_lab.bell_circuit())
            self.assertEqual(crosscheck_qasm_numpy.probabilities(text), BELL, text)

    def test_roundtrip_preserves_unitary(self):
        import qasm_lab
        original = qasm_lab.bell_circuit(measure=False)
        self.assertTrue(qasm_lab.same_unitary(original, qasm_lab.roundtrip_qasm3(original)[1]))
        self.assertTrue(qasm_lab.same_unitary(original, qasm_lab.roundtrip_qasm2(original)[1]))

    def test_reimported_circuit_gives_only_00_11(self):
        import qasm_lab
        _, back = qasm_lab.roundtrip_qasm3(qasm_lab.bell_circuit())
        counts = qasm_lab.counts(back, shots=1000, seed=9)
        self.assertLessEqual(set(counts), set(BELL))
        self.assertEqual(sum(counts.values()), 1000)

    def test_reference_file_loads_in_qiskit(self):
        import qasm_lab
        loaded = qasm_lab.qasm3.loads(_read("reference_bell_qasm3.qasm"))
        self.assertLessEqual(set(qasm_lab.counts(loaded, seed=1)), set(BELL))


if __name__ == "__main__":
    unittest.main()
