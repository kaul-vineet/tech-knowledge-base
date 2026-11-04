"""Try it (lesson 2): two small experiments on the real layers. Run: python try_it.py"""
import threading
from http.server import HTTPServer

from app import call
from handler import make_handler
from repository import InMemoryLoanRepository, SqliteLoanRepository
from service import LoanLimitReached, LoanService


def try_1_limit_of_one():
    service = LoanService(InMemoryLoanRepository(), max_active_per_member=1)
    server = HTTPServer(("127.0.0.1", 0), make_handler(service))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}"
    call(base, "POST", "/loans", {"bookId": "b1", "memberId": "m1"})
    print("[1] HTTP    borrow b2 by m1 ->", *call(base, "POST", "/loans", {"bookId": "b2", "memberId": "m1"}))
    try:
        service.borrow("b3", "m1")
    except LoanLimitReached as exc:
        print(f"[1] service borrow b3 by m1 -> {type(exc).__name__}: {exc}")
    server.shutdown()
    server.server_close()


def try_2_swap_repository():
    for repo in (InMemoryLoanRepository(), SqliteLoanRepository()):
        service = LoanService(repo)
        for book in ("b1", "b2", "b3"):
            service.borrow(book, "m1")
        service.give_back(2)
        loan = service.borrow("b4", "m1")
        print(f"[2] {type(repo).__name__:<24} after returning loan 2, b4 gets loan id {loan.id}")


if __name__ == "__main__":
    try_1_limit_of_one()
    try_2_swap_repository()
