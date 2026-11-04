"""End-to-end layer: one journey through a real HTTP server, the domain and a SQLite file."""
import pathlib
import tempfile
import unittest

from http_api import call, serve
from loans import LoanService
from sqlite_store import SqliteLoanStore

HERE = pathlib.Path(__file__).resolve().parent


class LoanJourneyE2ETest(unittest.TestCase):
    def test_borrow_conflict_return_and_lookup(self):
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            store = SqliteLoanStore(str(pathlib.Path(tmp) / "loans.db"))
            server, base = serve(LoanService(store))
            try:
                self.assertEqual(call(base, "POST", "/loans", {"bookId": "b1", "memberId": "m1"})[0], 201)
                self.assertEqual(call(base, "POST", "/loans", {"bookId": "b1", "memberId": "m2"}),
                                 (409, {"error": "book b1 is already on loan"}))
                self.assertEqual(call(base, "POST", "/loans/1/return")[1]["status"], "returned")
                self.assertEqual(call(base, "GET", "/loans/1")[1]["status"], "returned")
                self.assertEqual(call(base, "GET", "/loans/2")[0], 404)
            finally:
                server.shutdown()
                server.server_close()
                store.close()


if __name__ == "__main__":
    unittest.main()
