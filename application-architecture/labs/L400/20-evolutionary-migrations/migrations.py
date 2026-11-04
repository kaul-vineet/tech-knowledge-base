"""Expand/contract (parallel change) for splitting members.name into given_name + family_name (lesson 20 lab code).

expand   add the new columns (old code keeps working: it never names them)
backfill copy old -> new in small batches (short transactions; dual-writing code keeps new rows in sync)
contract drop the old column - only when NOTHING still reads or writes it (can_contract)
Weakness (the failureLab): can_contract() only checks the backfill, not which code versions still run.
"""
import sqlite3

USES_OLD_COLUMN = {1: True, 2: True, 3: False}  # app version -> reads/writes members.name ?


def connect():
    db = sqlite3.connect(":memory:", isolation_level=None)
    db.execute("CREATE TABLE members (id INTEGER PRIMARY KEY, name TEXT)")  # nullable: v3 stops writing it
    return db


def columns(db):
    return [row[1] for row in db.execute("PRAGMA table_info(members)")]


def expand(db):
    if "given_name" not in columns(db):  # idempotent: safe to re-run after a failed deploy
        db.execute("ALTER TABLE members ADD COLUMN given_name TEXT")
        db.execute("ALTER TABLE members ADD COLUMN family_name TEXT")


def split(name):
    given, _, family = name.partition(" ")
    return given, family


def backfill(db, batch=50):
    """Copy name -> given/family for rows not yet migrated, one short transaction per batch."""
    done = 0
    while True:
        rows = db.execute("SELECT id, name FROM members WHERE given_name IS NULL LIMIT ?", (batch,)).fetchall()
        if not rows:
            return done
        db.execute("BEGIN")
        for member_id, name in rows:
            db.execute("UPDATE members SET given_name = ?, family_name = ? WHERE id = ?", (*split(name), member_id))
        db.execute("COMMIT")  # short transactions: readers and writers are never blocked for long
        done += len(rows)


def missing_new_values(db):
    if "given_name" not in columns(db):
        return None
    return db.execute("SELECT COUNT(*) FROM members WHERE given_name IS NULL").fetchone()[0]


def can_contract(db, fleet_versions):
    """Is it safe to drop members.name? Returns (ok, reasons)."""
    reasons = []
    if missing_new_values(db) != 0:
        reasons.append(f"{missing_new_values(db)} rows not backfilled")
    return not reasons, reasons  # weakness: running v1/v2 instances still use members.name


def contract(db):
    if "name" in columns(db):
        db.execute("ALTER TABLE members DROP COLUMN name")  # rewrites the table: time grows with rows
