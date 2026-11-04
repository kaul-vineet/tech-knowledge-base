"""Repository layer: the ONLY code that knows how loans are stored.

Both classes expose the same four methods, so the service layer cannot tell them apart.
"""
import sqlite3
from dataclasses import dataclass


@dataclass
class Loan:
    id: int
    book_id: str
    member_id: str
    returned: bool = False


# repository pattern: same four methods (add/get/active/mark_returned) => storage is swappable
class InMemoryLoanRepository:
    def __init__(self):
        self._loans: dict[int, Loan] = {}

    def add(self, book_id, member_id):
        loan = Loan(len(self._loans) + 1, book_id, member_id)
        self._loans[loan.id] = loan
        return loan

    def get(self, loan_id):
        return self._loans.get(loan_id)

    def active(self):
        return [loan for loan in self._loans.values() if not loan.returned]

    def mark_returned(self, loan_id):
        # returning keeps the row, so the next new loan id keeps counting up
        self._loans[loan_id].returned = True


class SqliteLoanRepository:
    def __init__(self, path=":memory:"):
        # check_same_thread=False: the HTTP server calls us from its own thread.
        self._db = sqlite3.connect(path, check_same_thread=False)
        self._db.execute("CREATE TABLE IF NOT EXISTS loans (id INTEGER PRIMARY KEY, "
                         "book_id TEXT NOT NULL, member_id TEXT NOT NULL, "
                         "returned INTEGER NOT NULL DEFAULT 0)")
        self._db.commit()

    def add(self, book_id, member_id):
        # parameter binding: ? placeholders send values apart from the SQL text (no SQL injection)
        cur = self._db.execute("INSERT INTO loans (book_id, member_id) VALUES (?, ?)",
                               (book_id, member_id))
        self._db.commit()
        return Loan(cur.lastrowid, book_id, member_id)

    def get(self, loan_id):
        row = self._db.execute("SELECT id, book_id, member_id, returned FROM loans "
                               "WHERE id = ?", (loan_id,)).fetchone()
        return Loan(row[0], row[1], row[2], bool(row[3])) if row else None

    def active(self):
        rows = self._db.execute("SELECT id, book_id, member_id FROM loans WHERE returned = 0")
        return [Loan(r[0], r[1], r[2]) for r in rows.fetchall()]

    def mark_returned(self, loan_id):
        self._db.execute("UPDATE loans SET returned = 1 WHERE id = ?", (loan_id,))
        self._db.commit()
