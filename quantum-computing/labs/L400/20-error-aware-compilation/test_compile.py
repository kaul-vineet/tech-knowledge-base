"""Tests for lab 20: routing correctness, metrics, noise model, and the Qiskit path (CI). Run: python -m unittest -v"""
import importlib.util
import os
import sys
import unittest
from pathlib import Path

import numpy as np

import compile_lab as lab
import device as D
import noisy_check as nc

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from qsim import density as dm  # noqa: E402
from qsim import statevector as sv  # noqa: E402

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None
if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class Compilation(unittest.TestCase):
    def test_every_option_is_equivalent_to_the_logical_circuit(self):
        dev = D.make_device(drift=D.DRIFT)
        for layout, weighted, opt in ((lab.choose_layout(dev), False, False), (lab.dense_layout(dev), False, True),
                                      ([5, 1, 6, 2, 3], True, True)):
            ops, final, _ = lab.compile_circuit(dev, layout, weighted, opt)
            self.assertTrue(nc.equivalent(ops, final), layout)
            self.assertTrue(all(D.cx_error(dev, *o[1]) is not None for o in ops if o[0] == "cx"))   # only device edges

    def test_observed_metrics(self):
        dev = D.make_device(drift=D.DRIFT)
        self.assertEqual(lab.compile_circuit(dev, lab.choose_layout(dev))[2], {"esp": 0.2084, "cx": 27, "depth": 32})
        self.assertEqual(lab.compile_circuit(dev, lab.dense_layout(dev), False, True)[2], {"esp": 0.3059, "cx": 19, "depth": 24})

    def test_cancel_removes_only_adjacent_identical_cx(self):
        ops = [("cx", (0, 1), None), ("cx", (0, 1), None), ("cx", (1, 2), None), ("rz", (2,), 0.1), ("cx", (1, 2), None)]
        self.assertEqual(lab.cancel(ops), [("cx", (1, 2), None), ("rz", (2,), 0.1), ("cx", (1, 2), None)])

    def test_tensor_depolarizing_matches_qsim_density(self):
        rho = dm.pure(sv.run(3, [sv.h(0), sv.cx(0, 1), sv.cx(1, 2)]))
        ref = dm.apply_kraus(rho, dm.depolarizing_kraus(0.2, 2), [0, 2], 3)
        self.assertTrue(np.allclose(nc.depolarize(rho, 0.2, [0, 2], 3), ref))

    def test_esp_ranks_like_simulated_fidelity(self):
        dev = D.make_device(drift=D.DRIFT)
        rows = []
        for layout, weighted, opt in ((lab.choose_layout(dev), False, False), ([5, 1, 6, 2, 3], True, True)):
            ops, final, m = lab.compile_circuit(dev, layout, weighted, opt)
            rows.append((m["esp"], nc.noisy_fidelity(ops, final, dev)))
        self.assertEqual(rows, [(0.2084, 0.8959), (0.7835, 0.9878)])


@unittest.skipUnless(HAVE_QISKIT, "qiskit not installed (runs in CI)")
class QiskitLevels(unittest.TestCase):
    def test_level3_is_at_least_as_reliable_as_level0_and_fits_the_budget(self):
        import compile_qiskit
        out = compile_qiskit.run()
        self.assertGreaterEqual(out[3]["esp"], out[0]["esp"])
        self.assertLessEqual(out[3]["depth"], 3 * lab.DEPTH_BUDGET)    # 1q basis translation adds layers


if __name__ == "__main__":
    unittest.main()
