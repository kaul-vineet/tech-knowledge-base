"""SQLite repository for the overdue report. State after a 'tidy-up' refactor: correct output, but N+1 queries.

The refactor split one JOIN into "load loans, then look up each member and book" - readable, and 2N+1 queries.
"""
import random
import sqlite3
from datetime import date, timedelta

from domain import days_overdue, fine

SCHEMA = """
CREATE TABLE members (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT NOT NULL);
CREATE TABLE loans (id INTEGER PRIMARY KEY, member_id INTEGER NOT NULL REFERENCES members(id),
                    book_id INTEGER NOT NULL REFERENCES books(id), due TEXT NOT NULL, returned INTEGER NOT NULL);
"""
TODAY = date(2026, 10, 28)


def seeded_db(loans=200, seed=16):
    rng = random.Random(seed)  # seeded: the same library every run
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO members VALUES (?, ?)", [(i, f"Member {i}") for i in range(1, 51)])
    conn.executemany("INSERT INTO books VALUES (?, ?)", [(i, f"Book {i}") for i in range(1, 301)])
    conn.executemany("INSERT INTO loans VALUES (?, ?, ?, ?, ?)", [
        (i, rng.randint(1, 50), rng.randint(1, 300),
         (TODAY + timedelta(days=rng.randint(-20, 20))).isoformat(),
         int(rng.random() < 0.3)) for i in range(1, loans + 1)])
    conn.commit()
    return conn


def overdue_report(conn, today=TODAY):
    rows = []
    loans = conn.execute("SELECT id, member_id, book_id, due FROM loans WHERE returned = 0 ORDER BY id").fetchall()
    for loan_id, member_id, book_id, due in loans:
        days = days_overdue(date.fromisoformat(due), today)
        if days == 0:
            continue
        # N+1: two more queries per overdue loan - invisible with 5 test rows, 2N+1 round trips in production
        name = conn.execute("SELECT name FROM members WHERE id = ?", (member_id,)).fetchone()[0]
        title = conn.execute("SELECT title FROM books WHERE id = ?", (book_id,)).fetchone()[0]
        rows.append({"loan": loan_id, "member": name, "book": title, "days": days, "fine": fine(days)})
    return rows
