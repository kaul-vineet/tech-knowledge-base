"""Seam S1 quantum-computing -> cryptography risk model: the toy result never becomes a timeline."""
import unittest

import _lab  # noqa: F401
import estimates
import migration_plan
import seams
import shor_sim


class TestSeamQuantumRisk(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sims = [shor_sim.shor(15, 7), shor_sim.shor(21, 2)]

    def test_seam_passes(self):
        self.assertTrue(seams.s1_quantum_to_risk(self.sims)["ok"])

    def test_simulator_cannot_speak_about_rsa(self):
        bad = estimates.check_claims([{"target": "RSA-2048", "source": "this-lab-simulator", "text": "extrapolated"}])
        self.assertEqual(len(bad), 2)          # wrong target for the simulator AND no published source

    def test_sim_result_is_not_a_horizon(self):
        with self.assertRaises(TypeError):
            migration_plan.exposed(12, 2, self.sims[1])


if __name__ == "__main__":
    unittest.main()
