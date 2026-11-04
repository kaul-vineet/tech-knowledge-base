import unittest
from datetime import date

import _lab
import crypto_registry as registry
import fitness
import inventory
from flags import Flags


class TestFitness(unittest.TestCase):
    def test_f1_after_migration_passes_before_fails(self):
        self.assertTrue(fitness.f1_no_classical_kex_for_exposed_data(inventory.scan("after"))["ok"])
        before = fitness.f1_no_classical_kex_for_exposed_data(inventory.scan("before"))
        self.assertEqual(before["violations"], ["messaging sample_repo/services/messaging/channel.py:10 X25519"])

    def test_f1_baseline_expires(self):
        late = fitness.f1_no_classical_kex_for_exposed_data(inventory.scan("after"), today=date(2027, 7, 1))
        self.assertEqual(len(late["violations"]), 2)          # both payments entries are overdue on the fake clock

    def test_f2_budget(self):
        stats = _lab.phase_stats("migrated", [2, 2, 1], required=False)
        r = fitness.f2_handshake_budget(stats["tap"])
        self.assertEqual((r["ok"], r["client_flight_bytes"], r["handshake_bytes"]), (True, 1352, 5871))

    def test_f3_lint_flags_the_unmigrated_service(self):
        stats = _lab.phase_stats("migrated", [2], required=False)
        v1 = fitness.f3_registry_only(_lab.LAB / "sample_repo/services/messaging/channel.py", stats["tap"])
        self.assertGreater(v1["static_violations"], 0)
        self.assertTrue(stats["f3"]["ok"], stats["f3"])

    def test_f4_flags_expire_on_the_fake_clock(self):
        self.assertTrue(fitness.f4_flags_owned_and_live()["ok"])
        later = Flags(registry.HERE / "flags.json", today=date(2027, 2, 1))
        self.assertEqual(fitness.f4_flags_owned_and_live(later)["expired"], ["pq_required.messaging"])


if __name__ == "__main__":
    unittest.main()
