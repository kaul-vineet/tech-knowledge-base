"""Library Loans domain (same rules as lesson 7). Depends on a store with add/get/active/mark_returned."""
from dataclasses import dataclass


@dataclass
class Loan:
    id: int
    book_id: str
    member_id: str
    returned: bool = False


class LoanError(Exception):
    pass


class BookAlreadyOnLoan(LoanError):
    pass


class LoanLimitReached(LoanError):
    pass


class LoanNotFound(LoanError):
    pass


class LoanService:
    def __init__(self, store, max_active_per_member=3):
        self._store, self._max = store, max_active_per_member

    def borrow(self, book_id, member_id):
        if not book_id or not member_id:
            raise ValueError("bookId and memberId are required")
        active = self._store.active()
        if any(loan.book_id == book_id for loan in active):
            raise BookAlreadyOnLoan(f"book {book_id} is already on loan")
        if sum(loan.member_id == member_id for loan in active) >= self._max:
            raise LoanLimitReached(f"member {member_id} already has {self._max} loans")
        return self._store.add(book_id, member_id)

    def get(self, loan_id):
        loan = self._store.get(loan_id)
        if loan is None:
            raise LoanNotFound(f"loan {loan_id} not found")
        return loan

    def give_back(self, loan_id):
        self._store.mark_returned(self.get(loan_id).id)
        return self.get(loan_id)
