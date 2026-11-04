"""Presentation layer: turns HTTP requests into service calls and results into JSON."""
import json
import re
from http.server import BaseHTTPRequestHandler

from service import BookAlreadyOnLoan, LoanLimitReached, LoanNotFound

LOAN_PATH = re.compile(r"^/loans/(\d+)(/return)?$")
# presentation layer: translate domain errors into HTTP status codes here, and only here
ERROR_STATUS = {ValueError: 400, LoanNotFound: 404, BookAlreadyOnLoan: 409, LoanLimitReached: 409}


def to_json(loan):
    return {"id": loan.id, "bookId": loan.book_id, "memberId": loan.member_id,
            "status": "returned" if loan.returned else "active"}


def make_handler(service):
    class LoanHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            match = LOAN_PATH.match(self.path)
            if self.path == "/loans":
                self._call(201, lambda: service.borrow(*self._fields("bookId", "memberId")))
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

        def _fields(self, *names):
            length = int(self.headers.get("Content-Length", 0))
            try:
                body = json.loads(self.rfile.read(length) or b"{}")
            except json.JSONDecodeError:
                raise ValueError("body must be JSON")
            return [body.get(name) for name in names]

        def _call(self, ok_status, action):
            try:
                self._send(ok_status, to_json(action()))
            except tuple(ERROR_STATUS) as exc:
                self._send(ERROR_STATUS[type(exc)], {"error": str(exc)})

        def _send(self, status, payload):
            data = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass  # keep lab output quiet

    return LoanHandler
