"""Build task check: invariant 3 (no new loan while a loan is more than 14 days old).

By default this checks solution/member.py. To check your edited member.py instead:
    CHECK_MINE=1 python -m unittest test_build_task -v        (PowerShell: $env:CHECK_MINE = "1")
"""
import importlib.util
import os
import pathlib
import unittest
from datetime import date, timedelta

HERE = pathlib.Path(__file__).resolve().parent
TARGET = HERE / ("member.py" if os.environ.get("CHECK_MINE") else "solution/member.py")
spec = importlib.util.spec_from_file_location("member_under_test", TARGET)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
START = date(2026, 10, 1)


class OverdueInvariantTest(unittest.TestCase):
    def setUp(self):
        self.member = m.Member("m1", max_loans=3)
        self.member.borrow("b1", START)

    def test_day_14_is_still_fine(self):
        self.member.borrow("b2", START + timedelta(days=14))

    def test_day_15_blocks_new_loans(self):
        with self.assertRaises(m.HasOverdueLoans) as ctx:
            self.member.borrow("b2", START + timedelta(days=15))
        self.assertIn("b1", str(ctx.exception))
        self.assertEqual(len(self.member.active_loans), 1)  # nothing changed

    def test_returning_the_overdue_book_unblocks(self):
        self.member.give_back("b1", START + timedelta(days=20))
        self.member.borrow("b2", START + timedelta(days=20))

    def test_old_invariants_still_hold(self):
        self.assertRaises(m.AlreadyBorrowed, self.member.borrow, "b1", START)
        self.member.borrow("b2", START)
        self.member.borrow("b3", START)
        self.assertRaises(m.LoanLimitReached, self.member.borrow, "b4", START)


if __name__ == "__main__":
    unittest.main()
