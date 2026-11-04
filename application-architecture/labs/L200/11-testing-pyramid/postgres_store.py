"""PostgreSQL adapter (psycopg 3). Same four methods as SqliteLoanStore.

Used only by test_integration_postgres.py, which Testcontainers runs in CI (pending-ci): it needs
`pip install -r requirements-ci.txt` and a container engine (Docker or Podman).
"""
import psycopg

from loans import Loan


class PostgresLoanStore:
    def __init__(self, url):
        self._db = psycopg.connect(url, autocommit=True)
        self._db.execute("CREATE TABLE IF NOT EXISTS loans (id SERIAL PRIMARY KEY, book_id TEXT NOT NULL, "
                         "member_id TEXT NOT NULL, returned BOOLEAN NOT NULL DEFAULT FALSE)")

    def add(self, book_id, member_id):
        row = self._db.execute("INSERT INTO loans (book_id, member_id) VALUES (%s, %s) RETURNING id",
                               (book_id, member_id)).fetchone()  # %s placeholders: psycopg's parameter style
        return Loan(row[0], book_id, member_id)

    def get(self, loan_id):
        row = self._db.execute("SELECT id, book_id, member_id, returned FROM loans WHERE id = %s",
                               (loan_id,)).fetchone()
        return Loan(row[0], row[1], row[2], bool(row[3])) if row else None

    def active(self):
        rows = self._db.execute("SELECT id, book_id, member_id FROM loans WHERE NOT returned ORDER BY id").fetchall()
        return [Loan(*row) for row in rows]

    def mark_returned(self, loan_id):
        self._db.execute("UPDATE loans SET returned = TRUE WHERE id = %s", (loan_id,))

    def close(self):
        self._db.close()
