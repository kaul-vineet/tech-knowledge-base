"""Driving adapter: HTTP/JSON -> ForManagingLoans. Translates domain errors to status codes."""
import json
import re
from http.server import BaseHTTPRequestHandler

from domain import BookAlreadyOnLoan, LoanLimitReached, LoanNotFound

LOAN_PATH = re.compile(r"^/loans/(\d+)(/return)?$")
STATUS = {ValueError: 400, LoanNotFound: 404, BookAlreadyOnLoan: 409, LoanLimitReached: 409}


def to_json(loan):
    return {"id": loan.id, "bookId": loan.book_id, "memberId": loan.member_id,
            "status": "returned" if loan.returned else "active"}


def make_handler(loans):  # loans: anything that implements ports.ForManagingLoans
    class LoansHttpAdapter(BaseHTTPRequestHandler):
        def do_POST(self):
            match = LOAN_PATH.match(self.path)
            if self.path == "/loans":
                body = self._body()
                self._call(201, lambda: loans.borrow(body.get("bookId"), body.get("memberId")))
            elif match and match.group(2):
                self._call(200, lambda: loans.give_back(int(match.group(1))))
            else:
                self._send(404, {"error": "no such route"})

        def do_GET(self):
            match = LOAN_PATH.match(self.path)
            if match and not match.group(2):
                self._call(200, lambda: loans.get(int(match.group(1))))
            else:
                self._send(404, {"error": "no such route"})

        def _body(self):
            try:
                return json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            except json.JSONDecodeError:
                return {}

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

    return LoansHttpAdapter
