"""Library Loans API implemented AFTER writing openapi.json. Run: python server.py [port]"""
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

LOANS = {}  # in-memory store keeps this lab focused on the contract


class LoansApi(BaseHTTPRequestHandler):
    def do_GET(self):
        match = re.fullmatch(r"/loans/(\d+)", self.path)
        if self.path == "/health":
            self.send_json(200, {"status": "ok"})
        elif match and int(match.group(1)) in LOANS:
            self.send_json(200, LOANS[int(match.group(1))])
        else:
            self.send_json(404, {"error": f"not found: {self.path}"})

    def do_POST(self):
        if self.path != "/loans":
            return self.send_json(404, {"error": f"not found: {self.path}"})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except json.JSONDecodeError:
            body = {}
        book, member = body.get("bookId"), body.get("memberId")
        if not isinstance(book, str) or not isinstance(member, str):
            # contract-first: 400, 409, 201 and 404 are all declared in openapi.json; an undeclared status is drift
            return self.send_json(400, {"error": "bookId and memberId must be strings"})
        if any(l["bookId"] == book and l["status"] == "active" for l in LOANS.values()):
            return self.send_json(409, {"error": f"book {book} is already on loan"})
        # response body must carry every field the Loan schema lists as required
        loan = {"id": len(LOANS) + 1, "bookId": book, "memberId": member, "status": "active"}
        LOANS[loan["id"]] = loan
        self.send_json(201, loan)

    def send_json(self, status, payload):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass  # quiet output for labs


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"Library Loans API on http://127.0.0.1:{port} (Ctrl+C to stop)")
    HTTPServer(("127.0.0.1", port), LoansApi).serve_forever()
