"""Tests for lab 19: analytic counts vs counted circuits, Toffoli T-count, model values. Run: python -m unittest -v"""
import importlib.util
import os
import unittest

import counting as c
import estimate_lab as lab

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None
HAVE_QDK = importlib.util.find_spec("qdk") is not None
if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")
if os.environ.get("REQUIRE_QDK") == "1" and not HAVE_QDK:
    raise ImportError("REQUIRE_QDK=1 but qdk is not installed")


class Counting(unittest.TestCase):
    def test_formulas_match_counted_circuits(self):
        for n in (6, 8, 10, 12):
            for p in (1, 2, 3):
                edges = c.mc.regular_graph(n, 3, seed=1)
                colours = len(set(c.edge_colouring(edges).values()))
                counted, est = c.count(c.qaoa_ops(n, edges, p), n), lab.qaoa_logical(n, p, colours)
                self.assertEqual((counted["cx"], counted["rotations"]), (est["cx"], est["rotations"]), (n, p))
                self.assertLessEqual(counted["depth"], est["depth"], (n, p))   # formula = upper bound

    def test_depth_formula_is_tight_with_four_colours(self):
        edges = c.mc.regular_graph(12, 3, seed=1)
        self.assertEqual(c.count(c.qaoa_ops(12, edges, 3), 12)["depth"], lab.qaoa_logical(12, 3)["depth"])  # 40

    def test_toffoli_is_7_t(self):
        self.assertEqual(c.toffoli_ok(), (7, True))

    def test_rotation_synthesis_cost(self):
        self.assertEqual(c.t_per_rotation(1e-3 / 50), 47)

    def test_gidney_ekera_formulas(self):
        r = lab.rsa_logical(2048)
        self.assertEqual((r["logical_qubits"], r["toffoli"], r["depth"]), (6190, 2624225018, 2143289344))

    def test_surface_code_model(self):
        self.assertAlmostEqual(lab.logical_error(3), 3e-4)
        self.assertAlmostEqual(lab.logical_error(27), 3e-16)


@unittest.skipUnless(HAVE_QISKIT, "qiskit not installed (runs in CI)")
class QiskitAgrees(unittest.TestCase):
    def test_cx_and_depth(self):
        import count_qiskit
        out = count_qiskit.check()
        self.assertEqual(out["qiskit_cx"], out["analytic_cx"])
        self.assertEqual(out["qiskit_depth"], out["counted_depth"])


@unittest.skipUnless(HAVE_QDK, "qdk not installed (runs in CI job l400-qdk)")
class QdkEstimator(unittest.TestCase):
    def test_qdk_is_at_or_above_our_lower_bound_same_order(self):
        import estimate_qdk
        ours, qdk = estimate_qdk.ours(), estimate_qdk.run_qdk()
        ratio = qdk["qdk_min_physical_qubits"] / ours["ours_physical_qubits_data_only"]
        self.assertTrue(0.3 <= ratio <= 30, ratio)


if __name__ == "__main__":
    unittest.main()
