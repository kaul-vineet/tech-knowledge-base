"""Tests for lab 11. Run: python -m unittest -v   (from this folder)"""
import importlib.util
import os
import unittest

import crosscheck_numpy as cc

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None
if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class CrossCheck(unittest.TestCase):
    def test_basis_rewrites_keep_the_unitary(self):
        self.assertTrue(all(cc.basis_rewrites().values()))

    def test_star_needs_routing_on_a_line(self):
        self.assertEqual(cc.non_adjacent(cc.STAR, cc.COUPLING["line"]), [(0, 2), (0, 3), (0, 4)])

    def test_heavy_hex_size(self):
        self.assertEqual(cc.heavy_hex_qubits(3), 19)


@unittest.skipUnless(HAVE_QISKIT, "qiskit not installed (runs in CI)")
class SdkLab(unittest.TestCase):
    def test_original_counts(self):
        import transpile_lab
        self.assertEqual(transpile_lab.two_qubit_count(transpile_lab.ghz_star()), 4)

    def test_only_basis_gates_and_map_edges_after_transpile(self):
        import transpile_lab
        for name, backend in transpile_lab.backends().items():
            edges = {tuple(e) for e in backend.coupling_map.get_edges()}
            allowed = set(backend.operation_names) | {"barrier", "measure"}
            for level in range(4):
                tqc = transpile_lab.transpile_for(transpile_lab.ghz_star(), backend, level)
                self.assertLessEqual({i.operation.name for i in tqc.data}, allowed, (name, level))
                for inst in tqc.data:
                    if inst.operation.num_qubits == 2:
                        pair = tuple(tqc.find_bit(q).index for q in inst.qubits)
                        self.assertIn(pair, edges, (name, level, pair))

    def test_routing_costs_two_qubit_gates_on_line(self):
        import transpile_lab
        b = transpile_lab.backends()
        star = transpile_lab.ghz_star()
        self.assertEqual(transpile_lab.two_qubit_count(transpile_lab.transpile_for(star, b["all-to-all"], 0)), 4)
        self.assertGreater(transpile_lab.two_qubit_count(transpile_lab.transpile_for(star, b["line"], 0)), 4)

    def test_behaviour_survives_transpiling(self):
        import transpile_lab
        for backend in transpile_lab.backends().values():
            self.assertTrue(transpile_lab.same_outcomes(transpile_lab.transpile_for(transpile_lab.ghz_star(), backend, 3)))


if __name__ == "__main__":
    unittest.main()
