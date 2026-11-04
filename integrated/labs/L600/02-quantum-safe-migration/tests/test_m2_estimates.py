import unittest

import _lab  # noqa: F401
import estimates


class TestM2Estimates(unittest.TestCase):
    def test_cited_values_are_the_papers_words(self):
        self.assertEqual(estimates.CITED["GE2019"]["physical_qubits"], "20 million noisy qubits")
        self.assertEqual(estimates.CITED["GE2019"]["runtime"], "8 hours")
        self.assertEqual(estimates.CITED["G2025"]["physical_qubits"], "less than a million noisy qubits")
        self.assertEqual(estimates.CITED["G2025"]["runtime"], "less than a week")

    def test_formula_evaluation(self):
        f = estimates.ge_formula(2048)
        self.assertEqual((f["logical_qubits"], f["toffoli"]), (6190, 2624225018))

    def test_nist_timeline(self):
        self.assertEqual(estimates.NIST_IR_8547["timeline"], "deprecated after 2030, disallowed after 2035")


if __name__ == "__main__":
    unittest.main()
