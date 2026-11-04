"""Stand-in for the pager / ticket / deploy APIs (stdlib, SQLite, 127.0.0.1): the same Idempotency-Key contract
as lesson 15's payments_service - same key + same body -> stored response replayed; different body -> 422."""
import hashlib
import json
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload, **headers):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        for k, v in {"Content-Type": "application/json", "Content-Length": str(len(data)), **headers}.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        with self.server.lock:
            rows = self.server.db.execute("SELECT id, action, incident FROM effects ORDER BY id").fetchall()
        self._send(200, [{"id": i, "action": a, "incident": n} for i, a, n in rows])

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        req, key, fp = json.loads(body), self.headers.get("Idempotency-Key"), hashlib.sha256(body).hexdigest()
        with self.server.lock:
            row = self.server.db.execute("SELECT fp, response FROM idem WHERE key = ?", (key,)).fetchone() if key else None
            if row:
                return (self._send(422, {"error": "key reused with another body"}) if row[0] != fp
                        else self._send(200, json.loads(row[1]), **{"Idempotent-Replayed": "true"}))
            cur = self.server.db.execute("INSERT INTO effects (action, incident) VALUES (?, ?)", (req["action"], req["incident"]))
            response = {"effect_id": cur.lastrowid, **req}
            if key:
                self.server.db.execute("INSERT INTO idem VALUES (?, ?, ?)", (key, fp, json.dumps(response)))
            self.server.db.commit()
        self._send(201, response)

    def log_message(self, *args):
        pass


def start_in_thread():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.db = sqlite3.connect(":memory:", check_same_thread=False)
    server.db.executescript("CREATE TABLE effects (id INTEGER PRIMARY KEY, action TEXT, incident TEXT);"
                            "CREATE TABLE idem (key TEXT PRIMARY KEY, fp TEXT, response TEXT);")
    server.lock = threading.Lock()
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}"
