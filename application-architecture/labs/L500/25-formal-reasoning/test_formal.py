import random
import unittest

import contracts as c
import model_check as mc


class ContractTest(unittest.TestCase):
    def test_invariant_holds_on_random_traces(self):
        stats = c.random_traces(random.Random(7), traces=500)
        self.assertEqual((0, 0, 0), (stats["inv_broken"], stats["post_broken"], stats["not_atomic"]))

    def test_rejected_borrow_leaves_state_unchanged(self):
        member, day = c.Member("m1", max_loans=1), c.date(2026, 10, 1)
        member.borrow("b1", day)
        before = c.snapshot(member)
        with self.assertRaises(c.LoanRuleViolation):
            member.borrow("b2", day)
        self.assertEqual(before, c.snapshot(member))


class LiskovTest(unittest.TestCase):
    def test_valid_and_invalid_subtypes(self):
        self.assertEqual((0, 0), c.substitution_violations(c.StrictLimit()))
        self.assertEqual((0, 8), c.substitution_violations(c.GenerousLimit()))
        self.assertEqual((33, 0), c.substitution_violations(c.NoOverdueAccepted()))


class ModelCheckTest(unittest.TestCase):
    def test_buggy_workflow_has_four_step_counterexample(self):
        _, cex, _, _ = mc.bfs(fixed=False)
        self.assertEqual(["A reads: book free", "B reads: book free", "A borrows", "B borrows"], cex)

    def test_fixed_workflow_is_safe_and_live(self):
        n, cex, dead, _ = mc.bfs(fixed=True)
        self.assertIsNone(cex)
        self.assertEqual([], dead)
        self.assertEqual((True, n), mc.can_always_free_book(fixed=True))


if __name__ == "__main__":
    unittest.main()
