import ast
import pathlib
import threading
import unittest
from http.server import HTTPServer

from app import build_service, call
from handler import make_handler
from repository import InMemoryLoanRepository, SqliteLoanRepository
from service import BookAlreadyOnLoan, LoanLimitReached, LoanNotFound, LoanService

HERE = pathlib.Path(__file__).parent


class ServiceRules:
    """Same rule tests run against BOTH repositories: proves storage is swappable."""

    def make_repo(self):
        raise NotImplementedError

    def setUp(self):
        self.service = LoanService(self.make_repo(), max_active_per_member=2)

    def test_borrow_returns_active_loan(self):
        loan = self.service.borrow("b1", "m1")
        self.assertEqual((loan.id, loan.returned), (1, False))

    def test_same_book_cannot_be_borrowed_twice(self):
        self.service.borrow("b1", "m1")
        with self.assertRaises(BookAlreadyOnLoan):
            self.service.borrow("b1", "m2")

    def test_member_loan_limit(self):
        self.service.borrow("b1", "m1")
        self.service.borrow("b2", "m1")
        with self.assertRaises(LoanLimitReached):
            self.service.borrow("b3", "m1")

    def test_return_frees_the_book(self):
        loan = self.service.borrow("b1", "m1")
        self.assertTrue(self.service.give_back(loan.id).returned)
        self.assertEqual(self.service.borrow("b1", "m2").book_id, "b1")

    def test_unknown_loan(self):
        with self.assertRaises(LoanNotFound):
            self.service.get(42)


class InMemoryRulesTest(ServiceRules, unittest.TestCase):
    def make_repo(self):
        return InMemoryLoanRepository()


class SqliteRulesTest(ServiceRules, unittest.TestCase):
    def make_repo(self):
        return SqliteLoanRepository(":memory:")


class HttpTest(unittest.TestCase):
    def setUp(self):
        self.server = HTTPServer(("127.0.0.1", 0), make_handler(build_service("sqlite")))
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def test_borrow_conflict_get_and_errors(self):
        status, body = call(self.base, "POST", "/loans", {"bookId": "b1", "memberId": "m1"})
        self.assertEqual((status, body["status"]), (201, "active"))
        self.assertEqual(call(self.base, "POST", "/loans", {"bookId": "b1", "memberId": "m2"})[0], 409)
        self.assertEqual(call(self.base, "GET", "/loans/1")[0], 200)
        self.assertEqual(call(self.base, "GET", "/loans/99")[0], 404)
        self.assertEqual(call(self.base, "POST", "/loans", {"bookId": "b2"})[0], 400)


class DependencyDirectionTest(unittest.TestCase):
    """Tiny fitness function: the service layer must not import HTTP or SQL modules."""

    def test_service_has_no_infrastructure_imports(self):
        tree = ast.parse((HERE / "service.py").read_text(encoding="utf-8"))
        imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        imported |= {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
        self.assertFalse(imported & {"sqlite3", "http.server", "handler", "repository"})


if __name__ == "__main__":
    unittest.main()
