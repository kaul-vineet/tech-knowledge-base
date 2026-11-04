"""Lesson tests for lab 18: python -m unittest -v"""
import unittest

import crdts as c
from helpers import check_laws, converge, replay, shrink, law_failures


class CRDTs(unittest.TestCase):
    def test_two_phones_converge_and_add_wins(self):
        a, b = c.two_phones()
        self.assertEqual(a.state(), b.state())
        self.assertEqual(a.value(), {"milk", "eggs"})  # the concurrent re-add survives the remove

    def test_counters_and_or_set_obey_the_laws(self):
        for cls in (c.GCounter, c.PNCounter, c.ORSet):
            with self.subTest(cls=cls.__name__):
                self.assertEqual(set(check_laws(cls)["counts"].values()), {"500/500"})
                self.assertEqual(converge(cls)["converged"], "500/500")

    def test_failure_lab_lww_tie_is_not_commutative(self):
        laws, conv = check_laws(c.LWWRegister), converge(c.LWWRegister)
        self.assertEqual(laws["counts"]["commutative"], "407/500")
        self.assertEqual(conv["converged"], "386/500")
        self.assertIn("commutative fails after: r0.assign('r0', 'r0.9', 0); r1.assign('r1', 'r1.10', 0)", laws["counterexample"])

    def test_shrinker_returns_a_minimal_history(self):
        hist = [("op", 0, "assign", ("r0", "x", 0)), ("sync", 1, 2), ("op", 1, "assign", ("r1", "y", 0)), ("sync", 2, 0)]
        small = shrink(hist, lambda h: "commutative" in law_failures(c.LWWRegister, h))
        self.assertEqual(len(small), 2)
        x, y, _ = replay(c.LWWRegister, small)
        self.assertNotEqual(x.merge(y).state(), y.merge(x).state())

    def test_option_evidence_lww_number_loses_updates(self):
        r = c.like_counter()
        self.assertEqual(r["truth"], 140)
        self.assertEqual(r["pn"], [140, 140, 140])
        self.assertLess(max(r["lww"]), 140)


if __name__ == "__main__":
    unittest.main()
