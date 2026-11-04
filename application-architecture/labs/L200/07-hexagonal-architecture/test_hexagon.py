import ast
import pathlib
import tempfile
import threading
import unittest
from http.server import HTTPServer

from app import build, cli, http
from domain import BookAlreadyOnLoan, LoanLimitReached, LoanNotFound, LoanService
from driven_memory import InMemoryLoanStore
from driven_sqlite import SqliteLoanStore
from driving_http import make_handler
from ports import ForStoringLoans

HERE = pathlib.Path(__file__).resolve().parent
TECH = {"sqlite3", "http", "http.server", "argparse", "urllib", "urllib.request"}
ADAPTERS = {"driven_memory", "driven_sqlite", "driving_http", "driving_cli", "app"}


def imports_of(filename):
    tree = ast.parse((HERE / filename).read_text(encoding="utf-8"))
    names = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    return names | {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}


class StoreContract:
    """Port contract: every ForStoringLoans adapter must pass these. Reused by test_build_task.py."""

    def make_store(self):
        raise NotImplementedError

    def setUp(self):
        self.store = self.make_store()

    def test_is_a_storing_port(self):
        self.assertIsInstance(self.store, ForStoringLoans)

    def test_add_numbers_from_one(self):
        self.assertEqual([self.store.add("b1", "m1").id, self.store.add("b2", "m1").id], [1, 2])

    def test_get_unknown_is_none(self):
        self.assertIsNone(self.store.get(42))

    def test_returned_loans_are_not_active(self):
        self.store.add("b1", "m1")
        self.store.add("b2", "m2")
        self.store.mark_returned(1)
        self.assertEqual([(l.id, l.book_id) for l in self.store.active()], [(2, "b2")])
        self.assertTrue(self.store.get(1).returned)


class InMemoryStoreTest(StoreContract, unittest.TestCase):
    def make_store(self):
        return InMemoryLoanStore()


class SqliteStoreTest(StoreContract, unittest.TestCase):
    def make_store(self):
        store = SqliteLoanStore(":memory:")
        self.addCleanup(store.close)
        return store

    def test_survives_reopen(self):
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:  # inside the lab folder, never /tmp
            path = str(pathlib.Path(tmp) / "loans.db")
            first = SqliteLoanStore(path)
            first.add("b1", "m1")
            first.close()
            again = SqliteLoanStore(path)
            self.assertEqual(again.get(1).book_id, "b1")
            again.close()


class DomainRulesTest(unittest.TestCase):
    def setUp(self):
        self.loans = LoanService(InMemoryLoanStore(), max_active_per_member=2)

    def test_rules(self):
        self.loans.borrow("b1", "m1")
        self.assertRaises(BookAlreadyOnLoan, self.loans.borrow, "b1", "m2")
        self.loans.borrow("b2", "m1")
        self.assertRaises(LoanLimitReached, self.loans.borrow, "b3", "m1")
        self.assertRaises(LoanNotFound, self.loans.get, 9)
        self.assertTrue(self.loans.give_back(1).returned)


class DrivingAdaptersTest(unittest.TestCase):
    def test_cli_and_http_drive_the_same_hexagon(self):
        for storage in ("memory", "sqlite"):
            with self.subTest(storage=storage):
                service = build(storage)
                server = HTTPServer(("127.0.0.1", 0), make_handler(service))
                threading.Thread(target=server.serve_forever, daemon=True).start()
                base = f"http://127.0.0.1:{server.server_port}"
                self.assertEqual(cli(service, "borrow", "b1", "m1")[0], 0)
                self.assertEqual(http(base, "POST", "/loans", {"bookId": "b1", "memberId": "m2"})[0], 409)
                self.assertEqual(cli(service, "show", "99")[0], 3)
                self.assertEqual(http(base, "POST", "/loans", {"bookId": "b2"})[0], 400)
                server.shutdown()
                server.server_close()


class DependencyRuleTest(unittest.TestCase):
    """Fitness function: dependencies point INTO the hexagon, never out of it."""

    def test_hexagon_imports_no_technology_and_no_adapter(self):
        for name in ("domain.py", "ports.py"):
            bad = sorted(imports_of(name) & (TECH | ADAPTERS))
            self.assertFalse(bad, f"{name} must depend on ports only, but imports {bad}")

    def test_adapters_do_not_import_each_other(self):
        for name in ("driven_memory.py", "driven_sqlite.py", "driving_http.py"):
            bad = sorted(imports_of(name) & ADAPTERS)
            self.assertFalse(bad, f"{name} imports another adapter: {bad}")


if __name__ == "__main__":
    unittest.main()
