import pathlib
import tempfile
import unittest
from datetime import date

from app import borrow, give_back
from member import AlreadyBorrowed, LoanLimitReached, Member, NotBorrowed
from member_repository import BookAlreadyOnLoan, ConcurrencyConflict, MemberNotFound, SqliteMemberRepository

HERE = pathlib.Path(__file__).resolve().parent
DAY = date(2026, 10, 1)


class MemberAggregateTest(unittest.TestCase):
    """Unit tests: the invariants hold without any database."""

    def setUp(self):
        self.member = Member("m1", max_loans=2)

    def test_limit(self):
        self.member.borrow("b1", DAY)
        self.member.borrow("b2", DAY)
        self.assertRaises(LoanLimitReached, self.member.borrow, "b3", DAY)
        self.assertEqual(len(self.member.active_loans), 2)  # failed call changed nothing

    def test_no_double_loan_of_the_same_book(self):
        self.member.borrow("b1", DAY)
        self.assertRaises(AlreadyBorrowed, self.member.borrow, "b1", DAY)

    def test_return_frees_a_slot_and_keeps_history(self):
        self.member.borrow("b1", DAY)
        self.member.borrow("b2", DAY)
        self.member.give_back("b1", date(2026, 10, 5))
        self.member.borrow("b3", DAY)
        self.assertEqual([l.book_id for l in self.member.loans], ["b1", "b2", "b3"])
        self.assertRaises(NotBorrowed, self.member.give_back, "b1", DAY)

    def test_outside_code_cannot_bypass_the_root(self):
        self.member.borrow("b1", DAY)
        self.assertIsInstance(self.member.loans, tuple)  # no .append
        with self.assertRaises(AttributeError):  # frozen dataclass (FrozenInstanceError)
            self.member.loans[0].returned_on = DAY


class MemberRepositoryTest(unittest.TestCase):
    """Integration tests: the repository loads and saves the WHOLE aggregate."""

    def setUp(self):
        self.repo = SqliteMemberRepository()
        self.addCleanup(self.repo.close)
        self.repo.add(Member("m1", max_loans=3))
        self.repo.add(Member("m2", max_loans=3))

    def test_round_trip(self):
        borrow(self.repo, "m1", "b1", DAY)
        give_back(self.repo, "m1", "b1", date(2026, 10, 3))
        loaded = self.repo.get("m1")
        self.assertEqual((loaded.loans[0].returned_on, loaded.version), (date(2026, 10, 3), 2))

    def test_unknown_member(self):
        self.assertRaises(MemberNotFound, self.repo.get, "nobody")

    def test_stale_copy_is_rejected(self):
        first, second = self.repo.get("m1"), self.repo.get("m1")
        first.borrow("b1", DAY)
        self.repo.save(first)
        second.borrow("b2", DAY)
        self.assertRaises(ConcurrencyConflict, self.repo.save, second)
        self.assertEqual([l.book_id for l in self.repo.get("m1").loans], ["b1"])

    def test_cross_member_rule_is_enforced_by_the_database(self):
        borrow(self.repo, "m1", "b1", DAY)
        self.assertRaises(BookAlreadyOnLoan, borrow, self.repo, "m2", "b1", DAY)
        self.assertEqual((self.repo.get("m2").version, self.repo.get("m2").loans), (0, ()))  # rolled back

    def test_persists_in_a_file(self):
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            path = str(pathlib.Path(tmp) / "members.db")
            repo = SqliteMemberRepository(path)
            repo.add(Member("m9"))
            borrow(repo, "m9", "b9", DAY)
            repo.close()
            again = SqliteMemberRepository(path)
            self.assertEqual(again.get("m9").active_loans[0].book_id, "b9")
            again.close()


if __name__ == "__main__":
    unittest.main()
