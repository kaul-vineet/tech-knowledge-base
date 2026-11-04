"""Unit layer: the domain with an in-memory fake store. No files, no sockets, no threads."""
import unittest

from loans import BookAlreadyOnLoan, Loan, LoanLimitReached, LoanNotFound, LoanService


class FakeStore:
    """Test double that honours the same 4-method contract as the real stores."""

    def __init__(self):
        self.loans = {}

    def add(self, book_id, member_id):
        self.loans[len(self.loans) + 1] = Loan(len(self.loans) + 1, book_id, member_id)
        return self.loans[len(self.loans)]

    def get(self, loan_id):
        return self.loans.get(loan_id)

    def active(self):
        return [loan for loan in self.loans.values() if not loan.returned]

    def mark_returned(self, loan_id):
        self.loans[loan_id].returned = True


class LoanServiceUnitTest(unittest.TestCase):
    def setUp(self):
        self.service = LoanService(FakeStore(), max_active_per_member=2)

    def test_borrow_returns_an_active_loan(self):
        self.assertEqual(self.service.borrow("b1", "m1"), Loan(1, "b1", "m1", False))

    def test_book_cannot_be_on_loan_twice(self):
        self.service.borrow("b1", "m1")
        self.assertRaises(BookAlreadyOnLoan, self.service.borrow, "b1", "m2")

    def test_member_limit(self):
        self.service.borrow("b1", "m1")
        self.service.borrow("b2", "m1")
        self.assertRaises(LoanLimitReached, self.service.borrow, "b3", "m1")

    def test_limit_is_per_member(self):
        self.service.borrow("b1", "m1")
        self.service.borrow("b2", "m1")
        self.assertEqual(self.service.borrow("b3", "m2").member_id, "m2")

    def test_return_frees_the_book(self):
        self.service.borrow("b1", "m1")
        self.assertTrue(self.service.give_back(1).returned)
        self.assertEqual(self.service.borrow("b1", "m2").id, 2)

    def test_return_frees_a_slot(self):
        self.service.borrow("b1", "m1")
        self.service.borrow("b2", "m1")
        self.service.give_back(1)
        self.assertEqual(self.service.borrow("b3", "m1").id, 3)

    def test_unknown_loan(self):
        self.assertRaises(LoanNotFound, self.service.get, 42)
        self.assertRaises(LoanNotFound, self.service.give_back, 42)

    def test_missing_fields(self):
        self.assertRaises(ValueError, self.service.borrow, "", "m1")
        self.assertRaises(ValueError, self.service.borrow, "b1", None)


if __name__ == "__main__":
    unittest.main()
