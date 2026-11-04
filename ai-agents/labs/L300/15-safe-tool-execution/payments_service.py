"""Stand-in payments API (stdlib, SQLite, 127.0.0.1). POST /refunds commits the refund, THEN answers.

Fault (seeded by order): slow_first=True -> the first POST sleeps slow_s AFTER committing, so a client with a
shorter timeout sees a timeout although the money already moved (the classic retry-duplicates bug).
Idempotency-Key header (IETF draft-ietf-httpapi-idempotency-key-header): same key + same body -> the stored
response is replayed (no second refund); same key + different body -> 422.
"""
import hashlib
import json
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload, **headers):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        for k, v in {"Content-Type": "application/json", "Content-Length": str(len(data)), **headers}.items():
            self.send_header(k, v)
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass  # client already timed out

    def do_GET(self):
        with self.server.lock:
            rows = self.server.db.execute("SELECT id, order_id, amount FROM refunds ORDER BY id").fetchall()
        self._send(200, [{"id": i, "order_id": o, "amount": a} for i, o, a in rows])

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        req, key = json.loads(body), self.headers.get("Idempotency-Key")
        fingerprint = hashlib.sha256(body).hexdigest()
        with self.server.lock:
            db = self.server.db
            if key:
                row = db.execute("SELECT fingerprint, response FROM idem WHERE key = ?", (key,)).fetchone()
                if row and row[0] != fingerprint:
                    return self._send(422, {"error": "Idempotency-Key reused with a different request"})
                if row:
                    return self._send(200, json.loads(row[1]), **{"Idempotent-Replayed": "true"})
            cur = db.execute("INSERT INTO refunds (order_id, amount) VALUES (?, ?)", (req["order_id"], req["amount"]))
            response = {"refund_id": cur.lastrowid, "order_id": req["order_id"], "amount": req["amount"]}
            if key:  # stored in the same transaction as the refund
                db.execute("INSERT INTO idem (key, fingerprint, response) VALUES (?, ?, ?)", (key, fingerprint, json.dumps(response)))
            db.commit()
            self.server.posts += 1
            slow = self.server.slow_first and self.server.posts == 1
        if slow:
            time.sleep(self.server.slow_s)  # money moved; the answer is late
        self._send(201, response)

    def log_message(self, *args):
        pass


def start_in_thread(slow_first=False, slow_s=0.6):
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.db = sqlite3.connect(":memory:", check_same_thread=False)
    server.db.executescript("CREATE TABLE refunds (id INTEGER PRIMARY KEY, order_id TEXT, amount REAL);"
                            "CREATE TABLE idem (key TEXT PRIMARY KEY, fingerprint TEXT, response TEXT);")
    server.lock, server.posts, server.slow_first, server.slow_s = threading.Lock(), 0, slow_first, slow_s
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}"
