"""Transactional outbox: a loan change and its event are written in ONE SQLite transaction.

A relay (polling publisher) later reads unpublished rows in order and hands them to the bus.
"""
import json
import sqlite3

from events import CHANNEL, new_event

SCHEMA = """
CREATE TABLE IF NOT EXISTS loans (id INTEGER PRIMARY KEY, book_id TEXT NOT NULL, member_id TEXT NOT NULL,
                                  returned INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS outbox (seq INTEGER PRIMARY KEY AUTOINCREMENT, channel TEXT NOT NULL,
                                   payload TEXT NOT NULL, published_at TEXT);
"""


class BookAlreadyOnLoan(Exception):
    pass


class LoansWithOutbox:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.executescript(SCHEMA)

    def borrow(self, book_id, member_id):
        with self.db:  # one transaction: loan row + outbox row, or neither
            if self.db.execute("SELECT 1 FROM loans WHERE book_id = ? AND returned = 0", (book_id,)).fetchone():
                raise BookAlreadyOnLoan(f"book {book_id} is already on loan")
            loan_id = self.db.execute("INSERT INTO loans (book_id, member_id) VALUES (?, ?)",
                                      (book_id, member_id)).lastrowid
            self._record("LoanCreated", loan_id, book_id, member_id)
        return loan_id

    def give_back(self, loan_id):
        with self.db:
            book_id, member_id = self.db.execute("SELECT book_id, member_id FROM loans WHERE id = ? AND returned = 0",
                                                 (loan_id,)).fetchone()
            self.db.execute("UPDATE loans SET returned = 1 WHERE id = ?", (loan_id,))
            self._record("LoanReturned", loan_id, book_id, member_id)

    def _record(self, event_type, loan_id, book_id, member_id):
        event = new_event(event_type, {"loanId": loan_id, "bookId": book_id, "memberId": member_id})
        # outbox: the event is stored, not sent - sending inside the transaction could not be rolled back
        self.db.execute("INSERT INTO outbox (channel, payload) VALUES (?, ?)",
                        (CHANNEL[event_type], json.dumps(event)))

    def pending(self):
        return self.db.execute("SELECT COUNT(*) FROM outbox WHERE published_at IS NULL").fetchone()[0]


class Relay:
    def __init__(self, db, bus):
        self.db, self.bus = db, bus

    def publish_pending(self):
        rows = self.db.execute("SELECT seq, channel, payload FROM outbox WHERE published_at IS NULL "
                               "ORDER BY seq").fetchall()  # order: E1 before E2, as committed
        for seq, channel, payload in rows:
            self.bus.publish(channel, json.loads(payload))
            self._mark_published(seq)  # a crash before this line => the event is sent again (at least once)
        return len(rows)

    def _mark_published(self, seq):
        with self.db:
            self.db.execute("UPDATE outbox SET published_at = datetime('now') WHERE seq = ?", (seq,))
