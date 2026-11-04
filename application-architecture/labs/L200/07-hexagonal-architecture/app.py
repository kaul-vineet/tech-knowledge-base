"""Composition root: the ONE place that picks adapters. Run: python app.py --storage memory|sqlite"""
import argparse
import io
import json
import threading
import urllib.error
import urllib.request
from http.server import HTTPServer

from domain import LoanService
from driven_memory import InMemoryLoanStore
from driven_sqlite import SqliteLoanStore
from driving_cli import run_cli
from driving_http import make_handler

DRIVEN = {"memory": lambda path: InMemoryLoanStore(), "sqlite": lambda path: SqliteLoanStore(path)}


def build(storage, path=":memory:"):
    return LoanService(DRIVEN[storage](path))  # swap the driven adapter here; domain.py never changes


def http(base, method, path, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(base + path, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


def cli(service, *argv):
    out = io.StringIO()
    code = run_cli(list(argv), service, out)
    return code, out.getvalue().strip()


def demo(storage):
    service = build(storage)  # ONE hexagon, driven by two adapters below
    server = HTTPServer(("127.0.0.1", 0), make_handler(service))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}"
    print(f"storage={storage}")
    print("cli  borrow b1 m1      ->", *cli(service, "borrow", "b1", "m1"))
    print("http POST b1 by m2     ->", *http(base, "POST", "/loans", {"bookId": "b1", "memberId": "m2"}))
    print("cli  return 1          ->", *cli(service, "return", "1"))
    print("http GET /loans/1      ->", *http(base, "GET", "/loans/1"))
    print("cli  show 99           ->", *cli(service, "show", "99"))
    server.shutdown()
    server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--storage", choices=sorted(DRIVEN), default="memory")
    demo(parser.parse_args().storage)
