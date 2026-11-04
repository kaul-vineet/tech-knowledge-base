import unittest

import _lab  # noqa: F401
import inventory
import migration_plan as mp


class TestM4Plan(unittest.TestCase):
    def test_p1_items(self):
        rows = mp.plan(inventory.scan("before"))
        p1 = [(r["service"], r["algorithm"]) for r in rows if r["priority"] == "P1"]
        self.assertEqual(p1, [("messaging", "X25519"), ("payments", "ECDHE X25519/P-256"), ("payments", "RSA-3072")])

    def test_mosca_is_strict(self):
        rows = mp.plan(inventory.scan("before"))
        records = next(r for r in rows if r["service"] == "records")
        self.assertEqual((records["x"] + records["y"], records["z"], records["priority"]), (10, 10, "P2-kex"))

    def test_after_messaging_done(self):
        rows = mp.plan(inventory.scan("after"))
        self.assertEqual(mp.summary(rows), {"P1": 2, "P2-kex": 2, "P2-sig": 2, "done": 2, "none": 2})

    def test_horizon_needs_a_label(self):
        with self.assertRaises(ValueError):
            mp.Horizon(10, "simulator", "derived from N = 21")


if __name__ == "__main__":
    unittest.main()
