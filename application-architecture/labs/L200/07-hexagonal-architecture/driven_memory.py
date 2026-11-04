"""Driven adapter: keeps loans in a dict (fast, for tests and demos)."""
from domain import Loan


class InMemoryLoanStore:  # implements ports.ForStoringLoans
    def __init__(self):
        self._loans: dict[int, Loan] = {}

    def add(self, book_id, member_id):
        loan = Loan(len(self._loans) + 1, book_id, member_id)
        self._loans[loan.id] = loan
        return loan

    def get(self, loan_id):
        loan = self._loans.get(loan_id)
        return Loan(**vars(loan)) if loan else None  # a copy: callers cannot mutate the store

    def active(self):
        return [Loan(**vars(l)) for l in self._loans.values() if not l.returned]

    def mark_returned(self, loan_id):
        self._loans[loan_id].returned = True
