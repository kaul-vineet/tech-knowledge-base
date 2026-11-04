import unittest

import numpy as np

import _lab  # noqa: F401
import shor_sim
from qsim import statevector as sv


class TestM1Shor(unittest.TestCase):
    def test_factors_15_and_21(self):
        self.assertEqual(shor_sim.shor(15, 7)["factors"], [3, 5])
        self.assertEqual(shor_sim.shor(21, 2)["factors"], [3, 7])

    def test_success_probability_and_counts(self):
        r15, r21 = shor_sim.shor(15, 7), shor_sim.shor(21, 2)
        self.assertEqual((r15["qubits"], r15["p_success_per_run"], r15["successes"]), (12, 0.5, 101))
        self.assertEqual((r21["qubits"], r21["p_success_per_run"], r21["successes"]), (15, 0.3222, 66))
        self.assertEqual(r21["gates"]["iqft_cp"], 45)                       # t (t - 1) / 2 for t = 10
        self.assertEqual(r21["statevector_bytes"], 16 * 2 ** 15)

    def test_gate_level_oracle_equals_permutation(self):
        t, n = 8, 4
        zero = np.zeros(2 ** (t + n), dtype=complex)
        zero[0] = 1
        start = sv.run(t + n, [sv.x(t)] + [sv.h(j) for j in range(t)], zero)
        perm = start
        for j in range(t):
            perm = shor_sim.controlled_mult(perm, j, t, n, pow(7, 2 ** j, 15), 15)
        gates = sv.run(t + n, shor_sim.gate_level_ops_15_7(t), start)
        self.assertTrue(np.allclose(perm, gates))
        self.assertEqual(shor_sim.counts(shor_sim.gate_level_ops_15_7(t)), {"cx": 14, "ccx": 5})

    def test_matches_quantum_L500_closed_form(self):
        for args in ((15, 7), (21, 2)):
            self.assertTrue(shor_sim.matches_fft_shortcut(shor_sim.shor(*args)))


if __name__ == "__main__":
    unittest.main()
