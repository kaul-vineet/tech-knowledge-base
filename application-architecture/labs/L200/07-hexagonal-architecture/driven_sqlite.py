"""Driven adapter: keeps loans in SQLite. The only file that imports sqlite3."""
import sqlite3

from domain import Loan


class SqliteLoanStore:  # implements ports.ForStoringLoans
    def __init__(self, path=":memory:"):
        # check_same_thread=False: the HTTP adapter calls us from the server thread
        self._db = sqlite3.connect(path, check_same_thread=False)
        with self._db:
            self._db.execute("CREATE TABLE IF NOT EXISTS loans (id INTEGER PRIMARY KEY, book_id TEXT NOT NULL, "
                             "member_id TEXT NOT NULL, returned INTEGER NOT NULL DEFAULT 0)")

    def add(self, book_id, member_id):
        with self._db:  # commit on success, roll back on error
            cur = self._db.execute("INSERT INTO loans (book_id, member_id) VALUES (?, ?)", (book_id, member_id))
        return Loan(cur.lastrowid, book_id, member_id)

    def get(self, loan_id):
        row = self._db.execute("SELECT id, book_id, member_id, returned FROM loans WHERE id = ?",
                               (loan_id,)).fetchone()
        return Loan(row[0], row[1], row[2], bool(row[3])) if row else None

    def active(self):
        rows = self._db.execute("SELECT id, book_id, member_id FROM loans WHERE returned = 0").fetchall()
        return [Loan(*row) for row in rows]

    def mark_returned(self, loan_id):
        with self._db:
            self._db.execute("UPDATE loans SET returned = 1 WHERE id = ?", (loan_id,))

    def close(self):
        self._db.close()
