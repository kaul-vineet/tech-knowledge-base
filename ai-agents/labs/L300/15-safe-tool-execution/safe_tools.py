"""Safe execution of side-effecting tools: approval queue + audit log in SQLite, dry-run, idempotency keys."""
import hashlib
import json
import os
import sqlite3
import time
from pathlib import Path

import requests

BASE_URL = os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("LOCAL_MODEL") or os.environ.get("MODEL", "qwen2.5:1.5b")
# Tool metadata in the style of MCP annotations; the gate trusts OUR table, never hints sent by a server.
TOOLS = {"lookup_order": {"readOnly": True}, "send_refund": {"readOnly": False, "idempotent": False}}
SCHEMA = """CREATE TABLE IF NOT EXISTS approvals (id INTEGER PRIMARY KEY, tool TEXT, args TEXT, idem_key TEXT UNIQUE,
              status TEXT, approver TEXT, result TEXT);
            CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, ts REAL, actor TEXT, event TEXT, detail TEXT);"""


class ToolGate:
    def __init__(self, db_path, payments_url, dry_run=False, timeout=0.3, retries=2):
        self.db = sqlite3.connect(db_path)  # file on disk: survives a crash or restart
        self.db.executescript(SCHEMA)
        self.payments_url, self.dry_run, self.timeout, self.retries = payments_url, dry_run, timeout, retries

    def audit(self, actor, event, **detail):  # append-only audit log
        self.db.execute("INSERT INTO audit (ts, actor, event, detail) VALUES (?, ?, ?, ?)",
                        (time.time(), actor, event, json.dumps(detail, sort_keys=True)))
        self.db.commit()

    def request(self, tool, args, run_id, call_id):
        """Called by the agent loop for every tool call the model makes."""
        if TOOLS[tool]["readOnly"]:
            self.audit("agent", "read", tool=tool, args=args)
            return json.dumps({"order_id": args["order_id"], "status": "delivered", "paid": 25.0})
        if self.dry_run:  # dry-run: show exactly what would happen, change nothing
            self.audit("agent", "dry_run", tool=tool, args=args)
            return f"DRY RUN: would call {tool} with {json.dumps(args, sort_keys=True)}"
        key = hashlib.sha256(f"{run_id}:{call_id}:{tool}".encode("utf-8")).hexdigest()[:32]  # same call -> same key
        self.db.execute("INSERT OR IGNORE INTO approvals (tool, args, idem_key, status) VALUES (?, ?, ?, 'pending')",
                        (tool, json.dumps(args, sort_keys=True), key))
        row_id = self.db.execute("SELECT id FROM approvals WHERE idem_key = ?", (key,)).fetchone()[0]
        self.audit("agent", "queued", approval=row_id, tool=tool, args=args, key=key)
        return f"queued for human approval as #{row_id}; nothing has been sent yet"

    def decide(self, approval_id, approver, approve):
        status = "approved" if approve else "rejected"
        self.db.execute("UPDATE approvals SET status = ?, approver = ? WHERE id = ? AND status = 'pending'",
                        (status, approver, approval_id))
        self.audit(approver, status, approval=approval_id)

    def execute_approved(self):
        done = []
        for row_id, tool, args, key in self.db.execute(
                "SELECT id, tool, args, idem_key FROM approvals WHERE status = 'approved' ORDER BY id").fetchall():
            self.db.execute("UPDATE approvals SET status = 'executing' WHERE id = ?", (row_id,))
            self.db.commit()  # a crash after this line leaves 'executing' + the key: safe to resume
            result = self._send(json.loads(args), key)
            self.db.execute("UPDATE approvals SET status = 'done', result = ? WHERE id = ?", (json.dumps(result), row_id))
            self.audit("executor", "executed", approval=row_id, tool=tool, key=key, result=result)
            done.append(result)
        return done

    def _send(self, args, key):
        for attempt in range(self.retries + 1):
            try:
                r = requests.post(f"{self.payments_url}/refunds", json=args, timeout=self.timeout,
                                  headers={"Idempotency-Key": key})  # retries are now safe
                r.raise_for_status()
                return {**r.json(), "replayed": r.headers.get("Idempotent-Replayed") == "true"}
            except requests.Timeout:
                self.audit("executor", "timeout_retry", key=key, attempt=attempt)
        raise RuntimeError(f"payments API timed out {self.retries + 1} times (key {key})")


def run_agent(task, gate, run_id, base_url=BASE_URL, model=MODEL, max_steps=4):
    tools = [{"type": "function", "function": {"name": n, "description": n, "parameters": {"type": "object"}}} for n in TOOLS]
    messages = [{"role": "user", "content": task}]
    for _ in range(max_steps):
        reply = requests.post(f"{base_url}/chat/completions", timeout=60, json={
            "model": model, "messages": messages, "tools": tools, "temperature": 0}).json()["choices"][0]["message"]
        messages.append(reply)
        if not reply.get("tool_calls"):
            return reply["content"]
        for call in reply["tool_calls"]:
            result = gate.request(call["function"]["name"], json.loads(call["function"]["arguments"]), run_id, call["id"])
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
    return "stopped: max_steps"


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import payments_service
    from naive_refund import send_refund_naive
    pay, pay_url = payments_service.start_in_thread(slow_first=True)
    send_refund_naive(pay_url, "A-1001", 25.0)
    print("naive, 1 slow response :", requests.get(f"{pay_url}/refunds").json())
    pay, pay_url = payments_service.start_in_thread(slow_first=True)
    db = Path(__file__).resolve().parent / "approvals.db"
    db.unlink(missing_ok=True)
    gate = ToolGate(db, pay_url)
    print("agent   :", run_agent("Refund order A-1001 for 25.00, it arrived broken.", gate, run_id="run-1"))
    print("refunds before approval:", requests.get(f"{pay_url}/refunds").json())
    gate.decide(1, "alice", approve=True)
    print("executed:", gate.execute_approved())
    print("refunds after approval :", requests.get(f"{pay_url}/refunds").json())
    for actor, event, detail in gate.db.execute("SELECT actor, event, detail FROM audit ORDER BY id"):
        print(json.dumps({"actor": actor, "event": event, **json.loads(detail)}))
