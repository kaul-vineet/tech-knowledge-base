"""Build task solution (lesson 16): the overdue report in ONE query (JOIN), whatever the number of loans."""
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
    # one round trip: the database joins members and books and filters overdue loans (ISO dates sort as text)
    loans = conn.execute("""SELECT l.id, m.name, b.title, l.due FROM loans l
                            JOIN members m ON m.id = l.member_id JOIN books b ON b.id = l.book_id
                            WHERE l.returned = 0 AND l.due < ? ORDER BY l.id""", (today.isoformat(),)).fetchall()
    rows = []
    for loan_id, name, title, due in loans:
        days = days_overdue(date.fromisoformat(due), today)
        rows.append({"loan": loan_id, "member": name, "book": title, "days": days, "fine": fine(days)})
    return rows
