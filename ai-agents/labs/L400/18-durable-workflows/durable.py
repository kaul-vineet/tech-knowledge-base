"""Durable agent workflow in SQLite: an event history (checkpoints), replay after a crash, a long-running human
approval with a fake clock, exactly-once effects (Idempotency-Key for the payments API, outbox row in the
checkpoint transaction for the notification). Same idea as Temporal's event history, in ~100 lines."""
import json
import os
import sqlite3
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent.parent / "L300" / "15-safe-tool-execution")]
import approval_policy  # noqa: E402  (build task: shipped without a deadline)

BASE_URL = os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("LOCAL_MODEL") or os.environ.get("MODEL", "qwen2.5:1.5b")
STEPS = ["lookup", "propose", "approval", "refund", "notify"]
ORDERS = {"A-1001": {"order_id": "A-1001", "paid": 25.0, "status": "delivered"}}
SCHEMA = """CREATE TABLE IF NOT EXISTS workflows (id TEXT PRIMARY KEY, status TEXT, input TEXT, waiting_since REAL);
CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, wf_id TEXT, step TEXT, event TEXT, data TEXT, ts REAL,
                                    UNIQUE (wf_id, step, event));
CREATE TABLE IF NOT EXISTS outbox (id INTEGER PRIMARY KEY, wf_id TEXT, kind TEXT, payload TEXT, UNIQUE (wf_id, kind));"""
WAITING = object()


class Crash(BaseException):
    """Simulated kill -9: a BaseException, so no `except Exception` in the engine can swallow it."""


class Clock:
    def __init__(self, hours=0.0):
        self.hours = hours


class Engine:
    def __init__(self, db_path, payments_url, base_url=BASE_URL, model=MODEL, clock=None, crash_at=(),
                 use_keys=True, policy=approval_policy, timeout_h=48):
        self.db = sqlite3.connect(db_path)  # a file: the history survives the process
        self.db.executescript(SCHEMA)
        self.payments_url, self.base_url, self.model, self.clock = payments_url, base_url, model, clock or Clock()
        self.crash_at, self.use_keys, self.policy, self.timeout_h = set(crash_at), use_keys, policy, timeout_h

    def _crash(self, point):
        if point in self.crash_at:
            raise Crash(point)

    def start(self, wf_id, order_id):
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO workflows VALUES (?, 'running', ?, NULL)", (wf_id, json.dumps({"order_id": order_id})))

    def signal(self, wf_id, name, by):
        with self.db:  # a signal is an event in the history: durable and de-duplicated
            self.db.execute("INSERT OR IGNORE INTO history (wf_id, step, event, data, ts) VALUES (?, 'approval', ?, ?, ?)",
                            (wf_id, f"signal:{name}", json.dumps({"by": by}), self.clock.hours))

    def status(self, wf_id):
        return self.db.execute("SELECT status FROM workflows WHERE id = ?", (wf_id,)).fetchone()[0]

    def run(self, wf_id):
        """Replay the history, then execute the next steps. Returns the workflow status."""
        status, inp, since = self.db.execute("SELECT status, input, waiting_since FROM workflows WHERE id = ?", (wf_id,)).fetchone()
        if status != "running":
            return status
        done = {s: json.loads(d) for s, d in self.db.execute(
            "SELECT step, data FROM history WHERE wf_id = ? AND event = 'completed'", (wf_id,))}
        for step in STEPS:
            if step in done:
                continue  # replay: a recorded result is reused, the step is NOT executed again
            self._crash(f"before:{step}")
            result = getattr(self, f"_{step}")(wf_id, json.loads(inp), done, since)
            if result is WAITING:
                return "waiting"
            if isinstance(result, str):  # terminal outcome decided by code: rejected / escalated
                return result
            with self.db:  # checkpoint: result (+ outbox row) committed in ONE transaction
                self.db.execute("INSERT INTO history (wf_id, step, event, data, ts) VALUES (?, ?, 'completed', ?, ?)",
                                (wf_id, step, json.dumps(result), self.clock.hours))
                if step == "notify":
                    self.db.execute("INSERT OR IGNORE INTO outbox (wf_id, kind, payload) VALUES (?, 'refund_done', ?)",
                                    (wf_id, json.dumps(result)))
                    self.db.execute("UPDATE workflows SET status = 'done' WHERE id = ?", (wf_id,))
            self._crash(f"after:{step}")
            done[step] = result
        return "done"

    def _lookup(self, wf_id, inp, done, since):
        return ORDERS[inp["order_id"]]  # read-only: safe to repeat

    def _propose(self, wf_id, inp, done, since):
        prompt = f"Propose a refund as JSON.\n<refund_proposal>order {inp['order_id']} paid {done['lookup']['paid']}</refund_proposal>"
        r = requests.post(f"{self.base_url}/chat/completions", timeout=60, json={
            "model": self.model, "messages": [{"role": "user", "content": prompt}], "temperature": 0})
        proposal = json.loads(r.json()["choices"][0]["message"]["content"])
        self._crash("after_model:propose")  # model answered, nothing recorded yet: a resume asks again
        return {"amount": min(float(proposal["amount"]), done["lookup"]["paid"])}  # code caps the model's number

    def _approval(self, wf_id, inp, done, since):
        if since is None:
            with self.db:
                self.db.execute("UPDATE workflows SET waiting_since = ? WHERE id = ?", (self.clock.hours, wf_id))
            since = self.clock.hours
        signals = [(e.split(":", 1)[1], json.loads(d)["by"], ts) for e, d, ts in self.db.execute(
            "SELECT event, data, ts FROM history WHERE wf_id = ? AND event LIKE 'signal:%' ORDER BY id", (wf_id,))]
        state = self.policy.state(signals, since, self.clock.hours, self.timeout_h)
        if state == "waiting":
            return WAITING  # long-running: nothing in memory, the next run() re-reads the history
        if state == "approved":
            return {"by": next(by for name, by, _ in signals if name == "approve")}
        outcome = "rejected" if state == "rejected" else "escalated"
        with self.db:
            self.db.execute("UPDATE workflows SET status = ? WHERE id = ?", (outcome, wf_id))
            if outcome == "escalated":
                self.db.execute("INSERT OR IGNORE INTO outbox (wf_id, kind, payload) VALUES (?, 'approval_timeout', '{}')", (wf_id,))
        return outcome

    def _refund(self, wf_id, inp, done, since):
        headers = {"Idempotency-Key": f"{wf_id}:refund"} if self.use_keys else {}  # same step -> same key, always
        r = requests.post(f"{self.payments_url}/refunds", timeout=5, headers=headers,
                          json={"order_id": inp["order_id"], "amount": done["propose"]["amount"]})
        r.raise_for_status()
        self._crash("after_effect:refund")  # money moved, checkpoint not written yet: the dangerous gap
        return {"refund_id": r.json()["refund_id"], "replayed": r.headers.get("Idempotent-Replayed") == "true"}

    def _notify(self, wf_id, inp, done, since):
        return {"order_id": inp["order_id"], "amount": done["propose"]["amount"]}  # outbox row written with the checkpoint


if __name__ == "__main__":
    import tempfile
    import payments_service
    from naive_workflow import run_naive
    from harness import drive
    import durable  # the harness catches durable.Crash, so build engines from the imported module
    pay, pay_url = payments_service.start_in_thread()
    print("naive, crash after the refund :", run_naive("A-1001", pay_url, crash_at={"after_effect:refund"}),
          "->", len(requests.get(f"{pay_url}/refunds").json()), "refunds")
    pay, pay_url = payments_service.start_in_thread()
    with tempfile.TemporaryDirectory(dir=HERE) as d:
        db = Path(d) / "workflows.db"
        make = lambda crash: durable.Engine(db, pay_url, crash_at=crash)
        make(()).start("wf-1", "A-1001")
        status, crashes, eng = drive(make, "wf-1", crash_at={"after_effect:refund"})
        print("durable, same crash          :", status, crashes, "->", len(requests.get(f"{pay_url}/refunds").json()), "refund")
        for step, event, data in eng.db.execute("SELECT step, event, data FROM history WHERE wf_id = 'wf-1' ORDER BY id"):
            print(json.dumps({"step": step, "event": event, **json.loads(data)}))
        print("outbox:", eng.db.execute("SELECT kind FROM outbox").fetchall())
        eng.db.close()
