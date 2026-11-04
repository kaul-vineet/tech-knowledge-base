"""Write side (command model): the lesson-8 Member aggregate, rebuilt from an append-only event log in SQLite.

Commands go here; queries never do. The `events` table is the source of truth for both sides.
"""
import json
import sqlite3
import threading
import time


class LoanRuleViolation(Exception):
    pass


class Member:  # aggregate root: rules are checked here, before an event is recorded
    def __init__(self, member_id, max_loans=3):
        self.member_id, self.max_loans, self.books = member_id, max_loans, set()

    def apply(self, event_type, data):  # state = fold over the member's past events
        (self.books.add if event_type == "LoanCreated" else self.books.discard)(data["bookId"])

    def borrow(self, book_id):
        if book_id in self.books:
            raise LoanRuleViolation(f"{self.member_id} already has {book_id}")
        if len(self.books) >= self.max_loans:
            raise LoanRuleViolation(f"{self.member_id} already has {self.max_loans} loans")
        return "LoanCreated", {"memberId": self.member_id, "bookId": book_id}

    def give_back(self, book_id):
        if book_id not in self.books:
            raise LoanRuleViolation(f"{self.member_id} has no loan of {book_id}")
        return "LoanReturned", {"memberId": self.member_id, "bookId": book_id}


class EventStore:
    def __init__(self):
        self.db = sqlite3.connect(":memory:", check_same_thread=False)
        self.lock = threading.Lock()  # one writer at a time; the projector thread reads concurrently
        self.db.execute("CREATE TABLE events (seq INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT NOT NULL, "
                        "member_id TEXT NOT NULL, data TEXT NOT NULL, recorded_at REAL NOT NULL)")

    def append(self, event_type, data):
        with self.lock, self.db:
            return self.db.execute("INSERT INTO events (type, member_id, data, recorded_at) VALUES (?, ?, ?, ?)",
                                   (event_type, data["memberId"], json.dumps(data), time.time())).lastrowid

    def read_after(self, seq, limit=500):
        with self.lock:
            rows = self.db.execute("SELECT seq, type, data, recorded_at FROM events WHERE seq > ? ORDER BY seq LIMIT ?",
                                   (seq, limit)).fetchall()
        return [(s, t, json.loads(d), at) for s, t, d, at in rows]

    def load_member(self, member_id):
        member = Member(member_id)
        with self.lock:
            rows = self.db.execute("SELECT type, data FROM events WHERE member_id = ? ORDER BY seq", (member_id,))
            for event_type, data in rows.fetchall():
                member.apply(event_type, json.loads(data))
        return member


class LoanCommands:
    """Command handlers: load the aggregate, let it decide, append the event. Returns the event's seq."""

    def __init__(self, store):
        self.store = store

    def borrow(self, member_id, book_id):
        return self.store.append(*self.store.load_member(member_id).borrow(book_id))

    def give_back(self, member_id, book_id):
        return self.store.append(*self.store.load_member(member_id).give_back(book_id))
