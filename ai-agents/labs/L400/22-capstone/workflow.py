"""Lesson 18's durable pattern, generalised: named steps checkpointed in SQLite, replay after a crash, signals."""
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "18-durable-workflows"))
from durable import Clock, Crash  # noqa: E402,F401  (same crash type and fake clock as lesson 18)

WAITING = object()


class Workflow:
    def __init__(self, db_path, clock=None, crash_at=()):
        self.db, self.clock, self.crash_at = sqlite3.connect(db_path), clock or Clock(), set(crash_at)
        self.db.executescript("""CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, wf_id TEXT, step TEXT,
            event TEXT, data TEXT, ts REAL, UNIQUE (wf_id, step, event));
            CREATE TABLE IF NOT EXISTS waits (wf_id TEXT PRIMARY KEY, since REAL);""")

    def crash(self, point):
        if point in self.crash_at:
            raise Crash(point)

    def signal(self, wf_id, name, by):
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO history (wf_id, step, event, data, ts) VALUES (?, 'approval', ?, ?, ?)",
                            (wf_id, f"signal:{name}", json.dumps({"by": by}), self.clock.hours))

    def signals(self, wf_id):
        return [(e.split(":", 1)[1], json.loads(d)["by"], ts) for e, d, ts in self.db.execute(
            "SELECT event, data, ts FROM history WHERE wf_id = ? AND event LIKE 'signal:%' ORDER BY id", (wf_id,))]

    def waiting_since(self, wf_id):
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO waits VALUES (?, ?)", (wf_id, self.clock.hours))
        return self.db.execute("SELECT since FROM waits WHERE wf_id = ?", (wf_id,)).fetchone()[0]

    def run(self, wf_id, steps):
        """steps: [(name, fn(done) -> result | WAITING)]. Completed steps are replayed from the history."""
        done = {s: json.loads(d) for s, d in self.db.execute(
            "SELECT step, data FROM history WHERE wf_id = ? AND event = 'completed'", (wf_id,))}
        for name, fn in steps:
            if name in done:
                continue
            result = fn(done)
            if result is WAITING:
                return "waiting", done
            with self.db:
                self.db.execute("INSERT INTO history (wf_id, step, event, data, ts) VALUES (?, ?, 'completed', ?, ?)",
                                (wf_id, name, json.dumps(result), self.clock.hours))
            self.crash(f"after:{name}")
            done[name] = result
        return "done", done
