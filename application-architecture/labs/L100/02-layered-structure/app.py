"""Wiring: the one place that chooses concrete classes. Run: python app.py --storage sqlite"""
import argparse
import json
import threading
import urllib.error
import urllib.request
from http.server import HTTPServer

from handler import make_handler
from repository import InMemoryLoanRepository, SqliteLoanRepository
from service import LoanService


def build_service(storage):
    # Swapping storage changes ONLY this line - service and handler stay the same.
    repo = SqliteLoanRepository() if storage == "sqlite" else InMemoryLoanRepository()
    return LoanService(repo)


def call(base, method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--storage", choices=["memory", "sqlite"], default="memory")
    storage = parser.parse_args().storage
    server = HTTPServer(("127.0.0.1", 0), make_handler(build_service(storage)))  # port 0 = any free port
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}"
    print(f"storage={storage}")
    print("borrow b1 by m1 ->", *call(base, "POST", "/loans", {"bookId": "b1", "memberId": "m1"}))
    print("borrow b1 by m2 ->", *call(base, "POST", "/loans", {"bookId": "b1", "memberId": "m2"}))
    print("return loan 1   ->", *call(base, "POST", "/loans/1/return"))
    print("get loan 99     ->", *call(base, "GET", "/loans/99"))
    server.shutdown()


if __name__ == "__main__":
    main()
