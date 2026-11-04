"""HTTP adapter for the member portal (capstone). Binds 127.0.0.1. Learning-only identity: the caller's subject
arrives in an X-Subject header (in production it comes from the verified OIDC token, lesson 10).

GET  /tenants/{tenant}/members/{member}/loans -> {"memberId": "...", "loans": [{"loanId": 1, "bookId": "b1"}]}
POST /_contract/state {"state": "..."}         -> provider states for contract verification (test builds only);
                                                 the state also supplies the caller (the contract has no headers)
"""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from loans_service import Forbidden

MEMBER = {"id": "m1", "tenant": "lib00", "roles": ["member"]}


def start(make_service, port=0):
    state = {"service": make_service(), "subject": {}}

    class Handler(BaseHTTPRequestHandler):
        def _send(self, status, body):
            data = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            parts = self.path.strip("/").split("/")
            if len(parts) != 5 or parts[0] != "tenants" or parts[2] != "members" or parts[4] != "loans":
                return self._send(404, {"error": "not found"})
            subject = json.loads(self.headers.get("X-Subject") or "null") or state["subject"]
            try:
                loans = state["service"].loans_of(subject, parts[1], parts[3])
            except Forbidden as exc:
                return self._send(403, {"error": str(exc)})
            self._send(200, {"memberId": parts[3], "loans": loans})

        def do_POST(self):
            if self.path != "/_contract/state":
                return self._send(404, {"error": "not found"})
            name = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")["state"]
            state["service"] = make_service()
            if name == "member m1 of lib00 has one loan":
                state["service"].borrow(MEMBER, "lib00", "m1", "adult", "b1")
                state["subject"] = MEMBER  # provider state = data AND the authenticated caller
            self._send(200, {"state": name})

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}"
