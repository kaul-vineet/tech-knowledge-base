"""Build task solution: member.py plus invariant 3 - no new loan while any loan is overdue.

Only the aggregate changes: the repository, the app service and the database schema stay as they are.
"""
from dataclasses import dataclass, replace
from datetime import date

LOAN_DAYS = 14


class LoanRuleViolation(Exception):
    pass


class LoanLimitReached(LoanRuleViolation):
    pass


class AlreadyBorrowed(LoanRuleViolation):
    pass


class NotBorrowed(LoanRuleViolation):
    pass


class HasOverdueLoans(LoanRuleViolation):
    pass


@dataclass(frozen=True)
class Loan:
    book_id: str
    borrowed_on: date
    returned_on: date | None = None

    def is_overdue(self, today):
        return self.returned_on is None and (today - self.borrowed_on).days > LOAN_DAYS


class Member:
    def __init__(self, member_id, max_loans=3, loans=(), version=0):
        self.member_id = member_id
        self.max_loans = max_loans
        self._loans = list(loans)
        self.version = version

    @property
    def loans(self):
        return tuple(self._loans)

    @property
    def active_loans(self):
        return tuple(loan for loan in self._loans if loan.returned_on is None)

    def borrow(self, book_id, today: date):
        overdue = [loan.book_id for loan in self._loans if loan.is_overdue(today)]
        if overdue:  # invariant 3, checked in the same place as the others
            raise HasOverdueLoans(f"member {self.member_id} has overdue loans: {', '.join(overdue)}")
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
