"""HTTP adapter + a tiny client, used by the end-to-end test."""
import json
import re
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

from loans import BookAlreadyOnLoan, LoanLimitReached, LoanNotFound

LOAN_PATH = re.compile(r"^/loans/(\d+)(/return)?$")
STATUS = {ValueError: 400, LoanNotFound: 404, BookAlreadyOnLoan: 409, LoanLimitReached: 409}


def to_json(loan):
    return {"id": loan.id, "bookId": loan.book_id, "memberId": loan.member_id,
            "status": "returned" if loan.returned else "active"}


def make_handler(service):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            match = LOAN_PATH.match(self.path)
            if self.path == "/loans":
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                self._call(201, lambda: service.borrow(body.get("bookId"), body.get("memberId")))
            elif match and match.group(2):
                self._call(200, lambda: service.give_back(int(match.group(1))))
            else:
                self._send(404, {"error": "no such route"})

        def do_GET(self):
            match = LOAN_PATH.match(self.path)
            if match and not match.group(2):
                self._call(200, lambda: service.get(int(match.group(1))))
            else:
                self._send(404, {"error": "no such route"})

        def _call(self, ok, action):
            try:
                self._send(ok, to_json(action()))
            except tuple(STATUS) as exc:
                self._send(STATUS[type(exc)], {"error": str(exc)})

        def _send(self, status, payload):
            data = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    return Handler


def serve(service):
    server = HTTPServer(("127.0.0.1", 0), make_handler(service))  # port 0: any free port
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}"


def call(base, method, path, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(base + path, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())
