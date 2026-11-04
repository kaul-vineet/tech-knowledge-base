"""Build task solution: outbox.py plus retry bookkeeping and a dead-letter state in the relay.

A consumer failure no longer stops the relay: the row stays pending with attempts + 1 and the error text;
after MAX_ATTEMPTS it is marked dead (dead_at) and skipped, so one poison event cannot block the rest.
"""
import json
import sqlite3

from events import CHANNEL, new_event

MAX_ATTEMPTS = 3
SCHEMA = """
CREATE TABLE IF NOT EXISTS loans (id INTEGER PRIMARY KEY, book_id TEXT NOT NULL, member_id TEXT NOT NULL,
                                  returned INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS outbox (seq INTEGER PRIMARY KEY AUTOINCREMENT, channel TEXT NOT NULL,
                                   payload TEXT NOT NULL, published_at TEXT,
                                   attempts INTEGER NOT NULL DEFAULT 0, last_error TEXT, dead_at TEXT);
"""


class BookAlreadyOnLoan(Exception):
    pass


class LoansWithOutbox:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.executescript(SCHEMA)

    def borrow(self, book_id, member_id):
        with self.db:
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
        self.db.execute("INSERT INTO outbox (channel, payload) VALUES (?, ?)", (CHANNEL[event_type], json.dumps(event)))

    def pending(self):
        return self.db.execute("SELECT COUNT(*) FROM outbox WHERE published_at IS NULL AND dead_at IS NULL").fetchone()[0]

    def dead_letters(self):
        return self.db.execute("SELECT seq, attempts, last_error FROM outbox WHERE dead_at IS NOT NULL").fetchall()


class Relay:
    def __init__(self, db, bus, max_attempts=MAX_ATTEMPTS):
        self.db, self.bus, self.max_attempts = db, bus, max_attempts

    def publish_pending(self):
        rows = self.db.execute("SELECT seq, channel, payload FROM outbox WHERE published_at IS NULL "
                               "AND dead_at IS NULL ORDER BY seq").fetchall()
        published = 0
        for seq, channel, payload in rows:
            try:
                self.bus.publish(channel, json.loads(payload))
            except Exception as exc:  # record the failure and move on to the next event
                self._record_failure(seq, exc)
                continue
            self._mark_published(seq)
            published += 1
        return published

    def _record_failure(self, seq, exc):
        with self.db:
            self.db.execute("UPDATE outbox SET attempts = attempts + 1, last_error = ?, "
                            "dead_at = CASE WHEN attempts + 1 >= ? THEN datetime('now') END WHERE seq = ?",
                            (f"{type(exc).__name__}: {exc}", self.max_attempts, seq))

    def _mark_published(self, seq):
        with self.db:
            self.db.execute("UPDATE outbox SET published_at = datetime('now') WHERE seq = ?", (seq,))
