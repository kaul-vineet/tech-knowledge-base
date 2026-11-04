"""Failure lab: a hard-coded fast path that bypasses the registry. Static checks miss it; the wire seam catches it."""
import unittest

import _lab
import fitness
import inventory


class TestFailureLab(unittest.TestCase):
    def test_static_checks_miss_the_bypass(self):
        found = inventory.scan("after", messaging="faults/messaging_bypass")
        kex = [f for f in found if f["service"] == "messaging" and f["usage"] == "key-establishment"]
        self.assertEqual(kex, [])                                                     # inventory: nothing to migrate
        self.assertTrue(fitness.f1_no_classical_kex_for_exposed_data(found)["ok"])     # F1 passes
        self.assertEqual(_lab.phase_stats("bypass", [2], False)["f3"]["static_violations"], 0)   # lint passes

    def test_wire_seam_catches_the_bypass(self):
        stats = _lab.phase_stats("bypass", [2, 2, 1], required=False)
        self.assertFalse(stats["s3"]["ok"])
        self.assertEqual(stats["sessions"], {"X25519": 6})                            # silently classical
        self.assertEqual(stats["f3"]["client_kex_resolutions"], 0)

    def test_fix_routes_through_the_port(self):
        stats = _lab.phase_stats("migrated", [2, 2, 1], required=False)
        self.assertTrue(stats["s3"]["ok"])
        self.assertEqual(stats["sessions"], {"X25519MLKEM768": 4, "X25519": 2})

    def test_bypass_breaks_loudly_once_pq_is_required(self):
        stats = _lab.phase_stats("bypass", [2, 2, 2], required=True)
        self.assertEqual((stats["delivered"], stats["refused"]), (0, 6))


if __name__ == "__main__":
    unittest.main()
