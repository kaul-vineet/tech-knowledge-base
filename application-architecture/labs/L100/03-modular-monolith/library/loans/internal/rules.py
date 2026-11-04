# Talks to the catalog ONLY through its public interface (library.catalog).
from library import catalog

_LOANS = {}


class LoanError(Exception):
    pass


def borrow(book_id, member_id):
    if not catalog.is_available(book_id):
        raise LoanError(f"book {book_id} is not available")
    catalog.set_on_loan(book_id, True)
    loan_id = len(_LOANS) + 1
    _LOANS[loan_id] = (book_id, member_id)
    return loan_id


def give_back(loan_id):
    book_id, _ = _LOANS.pop(loan_id)
    catalog.set_on_loan(book_id, False)
