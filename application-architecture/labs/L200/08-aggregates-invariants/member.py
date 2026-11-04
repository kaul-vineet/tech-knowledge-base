"""Member aggregate: a member and their loans form ONE consistency boundary.

Every change goes through the root (Member), so the invariants below hold after every method call:
  1. at most max_loans active loans per member
  2. a member never has the same book on loan twice
"""
from dataclasses import dataclass, replace
from datetime import date


class LoanRuleViolation(Exception):
    pass


class LoanLimitReached(LoanRuleViolation):
    pass


class AlreadyBorrowed(LoanRuleViolation):
    pass


class NotBorrowed(LoanRuleViolation):
    pass


@dataclass(frozen=True)
class Loan:  # entity INSIDE the aggregate; frozen, so outside code cannot edit it behind the root's back
    book_id: str
    borrowed_on: date
    returned_on: date | None = None


class Member:  # aggregate root: the only object outside code may hold a reference to
    def __init__(self, member_id, max_loans=3, loans=(), version=0):
        self.member_id = member_id
        self.max_loans = max_loans
        self._loans = list(loans)
        self.version = version  # optimistic concurrency: the repository compares it on save

    @property
    def loans(self):
        return tuple(self._loans)  # read-only view: no member.loans.append(...) bypassing the rules

    @property
    def active_loans(self):
        return tuple(loan for loan in self._loans if loan.returned_on is None)

    def borrow(self, book_id, today: date):
        # invariants are checked here, in one place, before any state changes
        if any(loan.book_id == book_id for loan in self.active_loans):
            raise AlreadyBorrowed(f"member {self.member_id} already has {book_id}")
        if len(self.active_loans) >= self.max_loans:
            raise LoanLimitReached(f"member {self.member_id} already has {self.max_loans} loans")
        loan = Loan(book_id, today)
        self._loans.append(loan)
        return loan

    def give_back(self, book_id, today: date):
        for i, loan in enumerate(self._loans):
            if loan.book_id == book_id and loan.returned_on is None:
                self._loans[i] = replace(loan, returned_on=today)
                return self._loans[i]
        raise NotBorrowed(f"member {self.member_id} has no active loan of {book_id}")
