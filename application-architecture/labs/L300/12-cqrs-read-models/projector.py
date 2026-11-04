"""Read side: a projector turns events into a query-shaped read model. Run the demo: python app.py

Works on the happy path. Hidden weakness (the failureLab): the checkpoint moves BEFORE the read model changes,
in a separate transaction, and the counters are not idempotent. A crash in between skips an event for good.
"""
import json
import sqlite3
import sys
import time

READ_SCHEMA = """
CREATE TABLE IF NOT EXISTS member_loans (member_id TEXT PRIMARY KEY, active INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS book_status (book_id TEXT PRIMARY KEY, member_id TEXT);
CREATE TABLE IF NOT EXISTS checkpoint (projector TEXT PRIMARY KEY, seq INTEGER NOT NULL);
"""


class SimulatedCrash(Exception):
    """Seeded fault: the projector process dies at a chosen event."""


def json_log(record, stream=sys.stdout):
    print(json.dumps(record, sort_keys=True), file=stream)  # structured log: one JSON object per line


class Projector:
    name = "loans_view"

    def __init__(self, store, read_db=None, log=json_log, crash_at_seq=None):
        self.store, self.log, self.crash_at_seq = store, log, crash_at_seq
        self.db = read_db or sqlite3.connect(":memory:", check_same_thread=False)  # read model: its own database
        self.db.executescript(READ_SCHEMA)

    def position(self):  # checkpoint: the last event seq this projector has handled
        row = self.db.execute("SELECT seq FROM checkpoint WHERE projector = ?", (self.name,)).fetchone()
        return row[0] if row else 0

    def _save_checkpoint(self, seq):
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO checkpoint VALUES (?, ?)", (self.name, seq))

    def apply(self, event_type, data):
        member, book = data["memberId"], data["bookId"]
        delta = 1 if event_type == "LoanCreated" else -1  # NOT idempotent: applying twice counts twice
        self.db.execute("INSERT INTO member_loans VALUES (?, 0) ON CONFLICT(member_id) DO NOTHING", (member,))
        self.db.execute("UPDATE member_loans SET active = active + ? WHERE member_id = ?", (delta, member))
        self.db.execute("INSERT OR REPLACE INTO book_status VALUES (?, ?)",
                        (book, member if event_type == "LoanCreated" else None))

    def run_once(self):
        events = self.store.read_after(self.position())
        for seq, event_type, data, recorded_at in events:
            self._save_checkpoint(seq)  # weakness: position moves first, in its own transaction ...
            if seq == self.crash_at_seq:
                raise SimulatedCrash(f"projector died at seq {seq}")
            with self.db:  # ... the read model changes in a second transaction
                self.apply(event_type, data)
            # consistency window: time from the write-side commit to this event being visible in the view
            self.log({"evt": "projected", "projector": self.name, "seq": seq, "type": event_type,
                      "lag_ms": round((time.time() - recorded_at) * 1000, 1)})
        return len(events)

    def rebuild(self):
        """Drop the view and replay every event from seq 0: the read model is disposable, the log is not."""
        with self.db:
            self.db.execute("DELETE FROM member_loans")
            self.db.execute("DELETE FROM book_status")
            self.db.execute("DELETE FROM checkpoint WHERE projector = ?", (self.name,))
        replayed = 0
        while (count := self.run_once()):
            replayed += count
        self.log({"evt": "rebuilt", "projector": self.name, "replayed": replayed, "position": self.position()})
        return replayed


class LoansView:
    """Queries: cheap, shaped for the screen, and possibly a few milliseconds behind the write side."""

    def __init__(self, db):
        self.db = db

    def active_loans(self, member_id):
        row = self.db.execute("SELECT active FROM member_loans WHERE member_id = ?", (member_id,)).fetchone()
        return row[0] if row else 0

    def holder(self, book_id):
        row = self.db.execute("SELECT member_id FROM book_status WHERE book_id = ?", (book_id,)).fetchone()
        return row[0] if row else None

    def snapshot(self):
        return {"member_loans": dict(self.db.execute("SELECT * FROM member_loans ORDER BY member_id").fetchall()),
                "book_status": dict(self.db.execute("SELECT * FROM book_status ORDER BY book_id").fetchall())}


def drift(store, view_db, projector_cls=None):
    """Projection check: rebuild into a scratch database and list every row where the live view differs."""
    fresh = (projector_cls or Projector)(store, log=lambda record: None)
    fresh.rebuild()
    live, truth = LoansView(view_db).snapshot(), LoansView(fresh.db).snapshot()
    return [f"{table}[{key}]: view {live[table].get(key)!r}, events say {truth[table].get(key)!r}"
            for table in truth for key in sorted(set(truth[table]) | set(live[table]))
            if live[table].get(key) != truth[table].get(key)]
