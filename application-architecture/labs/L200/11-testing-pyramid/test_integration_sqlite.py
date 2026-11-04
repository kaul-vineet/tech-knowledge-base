"""Integration layer: the SQLite adapter against a real database file (one integration point at a time)."""
import pathlib
import tempfile
import unittest

from sqlite_store import SqliteLoanStore

HERE = pathlib.Path(__file__).resolve().parent


class StoreContract:
    """Every store adapter must pass these; test_integration_postgres.py reuses them."""

    def make_store(self):
        raise NotImplementedError

    def setUp(self):
        self.store = self.make_store()

    def test_ids_start_at_one(self):
        self.assertEqual([self.store.add("b1", "m1").id, self.store.add("b2", "m1").id], [1, 2])

    def test_get_round_trips_types(self):
        self.store.add("b1", "m1")
        loan = self.store.get(1)
        self.assertEqual((loan.id, loan.book_id, loan.member_id, loan.returned), (1, "b1", "m1", False))
        self.assertIs(type(loan.returned), bool)  # not 0/1 from the database
        self.assertIsNone(self.store.get(99))

    def test_active_excludes_returned_in_id_order(self):
        for book in ("b1", "b2", "b3"):
            self.store.add(book, "m1")
        self.store.mark_returned(2)
        self.assertEqual([l.book_id for l in self.store.active()], ["b1", "b3"])
        self.assertTrue(self.store.get(2).returned)


class SqliteStoreIntegrationTest(StoreContract, unittest.TestCase):
    def make_store(self):
        tmp = tempfile.TemporaryDirectory(dir=HERE)  # a real file, inside the lab folder
        self.addCleanup(tmp.cleanup)
        self.path = pathlib.Path(tmp.name) / "loans.db"
        store = SqliteLoanStore(str(self.path))
        self.addCleanup(store.close)
        return store

    def test_data_survives_a_restart(self):
        self.store.add("b1", "m1")
        self.store.mark_returned(1)
        self.store.close()
        reopened = SqliteLoanStore(str(self.path))
        self.addCleanup(reopened.close)
        self.assertTrue(reopened.get(1).returned)


if __name__ == "__main__":
    unittest.main()
