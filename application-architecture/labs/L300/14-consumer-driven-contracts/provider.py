"""Catalogue service (the PROVIDER): GET /books/{id} -> {"id", "title", "available"}. Stdlib http.server, 127.0.0.1.

Run: python provider.py 8081
"""
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BOOKS = {"b1": {"title": "Dune", "available": True}, "b2": {"title": "Emma", "available": False}}


def book_body(book_id, book, title_field="title"):
    return {"id": book_id, title_field: book["title"], "available": book["available"]}


def make_handler(books, title_field="title", states=False):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, status, payload):
            data = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            parts = self.path.strip("/").split("/")
            if len(parts) == 2 and parts[0] == "books" and parts[1] in books:
                return self._send(200, book_body(parts[1], books[parts[1]], title_field))
            self._send(404, {"error": "not found"})

        def do_POST(self):  # provider states: test-only hook the verifier calls before each interaction
            if not states or self.path != "/_contract/state":
                return self._send(404, {"error": "not found"})
            state = json.loads(self.rfile.read(int(self.headers["Content-Length"])))["state"]
            books.clear()
            if state.startswith("book ") and state.endswith(" exists"):
                books[state.split()[1]] = {"title": "Any title", "available": True}
            self._send(200, {"state": state})

        def log_message(self, *args):
            pass

    return Handler


def start(books=None, title_field="title", states=False, port=0):
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(dict(books or BOOKS), title_field, states))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}"


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8081
    print(f"catalogue provider on http://127.0.0.1:{port} (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", port), make_handler(dict(BOOKS))).serve_forever()
