"""Runs only where Qiskit is installed (CI job); skipped in the authoring sandbox."""
import importlib.util
import unittest

import _lab  # noqa: F401

HAS_QISKIT = importlib.util.find_spec("qiskit") is not None


@unittest.skipUnless(HAS_QISKIT, "qiskit not installed (pending CI)")
class TestQiskitCrossCheck(unittest.TestCase):
    def test_same_distribution_as_numpy(self):
        import numpy as np
        import shor_qiskit
        import shor_sim
        for modulus, a in ((15, 7), (21, 2)):
            self.assertTrue(np.allclose(shor_qiskit.counting_probs(modulus, a),
                                        shor_sim.run_order_finding(modulus, a)["probs"], atol=1e-9))


if __name__ == "__main__":
    unittest.main()
