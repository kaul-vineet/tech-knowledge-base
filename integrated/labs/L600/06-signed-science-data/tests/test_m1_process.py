"""M1: the astronomy processing step (reuses astronomy L100 #4 units and L400 #21 rows)."""
import unittest

from _world import world

import canonical
import checks
import science


class M1Process(unittest.TestCase):
    def test_milestone(self):
        ok, d = checks.m1_process(world())
        self.assertTrue(ok, d)
        self.assertEqual(d["rows"], 28)  # release v4 = 12 + 4 * 4 rows

    def test_inverse_parallax_only_when_fractional_error_small(self):
        for r in science.catalogue(4)["rows"]:
            if r["parallax_snr"] >= science.MIN_PARALLAX_SNR:
                self.assertEqual(r["method"], "inverse-parallax")
                self.assertAlmostEqual(r["distance_pc"], 1000.0 / r["parallax_mas"], places=9)
            else:
                self.assertIsNone(r["distance_pc"])
                self.assertEqual(r["method"], "needs-prior")

    def test_deterministic_bytes(self):
        a = world().mirrors[0].objects["releases/v2/catalogue.json"]
        self.assertEqual(a, canonical.dumps(science.catalogue(2)))  # re-running the step gives identical bytes


if __name__ == "__main__":
    unittest.main()
