"""Seam S2 cryptography inventory -> application-architecture plan: owned, joined with data lifetimes, never dropped."""
import unittest

import _lab  # noqa: F401
import inventory
import migration_plan
import seams


class TestSeamInventoryPlan(unittest.TestCase):
    def test_seam_passes(self):
        for stage in ("before", "after"):
            self.assertTrue(seams.s2_inventory_to_plan(inventory.scan(stage))["ok"], stage)

    def test_unowned_file_is_escalated(self):
        row = migration_plan.plan([{"file": "tools/x.py", "line": 3, "algorithm": "RSA-2048", "usage": "signature",
                                    "service": "unowned", "pq": False}])[0]
        self.assertEqual(row["priority"], "P1-review")

    def test_lifetime_comes_from_the_manifest(self):
        rows = migration_plan.plan(inventory.scan("before"))
        self.assertEqual({(r["service"], r["x"]) for r in rows if r["service"] == "messaging"}, {("messaging", 12)})


if __name__ == "__main__":
    unittest.main()
