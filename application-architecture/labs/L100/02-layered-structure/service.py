"""Service layer: business rules only. No HTTP, no SQL - it receives a repository."""


class LoanError(Exception):
    """Base class for rule violations; the presentation layer maps these to HTTP codes."""


class BookAlreadyOnLoan(LoanError):
    pass


class LoanLimitReached(LoanError):
    pass


class LoanNotFound(LoanError):
    pass


# dependency direction: the service is handed a repository; it never imports http.server or sqlite3
class LoanService:
    def __init__(self, repository, max_active_per_member=3):
        self._repo = repository
        self._max = max_active_per_member

    def borrow(self, book_id, member_id):
        if not book_id or not member_id:
            raise ValueError("bookId and memberId are required")
        active = self._repo.active()
        if any(loan.book_id == book_id for loan in active):
            raise BookAlreadyOnLoan(f"book {book_id} is already on loan")
        if sum(loan.member_id == member_id for loan in active) >= self._max:
            # domain error, not an HTTP code: the presentation layer maps it to 409
            raise LoanLimitReached(f"member {member_id} already has {self._max} loans")
        return self._repo.add(book_id, member_id)

    def get(self, loan_id):
        loan = self._repo.get(loan_id)
        if loan is None:
            raise LoanNotFound(f"loan {loan_id} not found")
        return loan

    def give_back(self, loan_id):
        loan = self.get(loan_id)
        self._repo.mark_returned(loan.id)
        return self.get(loan_id)
