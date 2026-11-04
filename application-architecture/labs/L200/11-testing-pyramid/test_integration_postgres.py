"""Integration layer, real PostgreSQL via Testcontainers (pending-ci).

Skipped unless LOANS_TESTCONTAINERS=1. CI (ubuntu-latest, Docker available) runs:
    pip install -r requirements-ci.txt
    LOANS_TESTCONTAINERS=1 python -m unittest -v test_integration_postgres
"""
import os
import unittest

from test_integration_sqlite import StoreContract

RUN = os.environ.get("LOANS_TESTCONTAINERS") == "1"


@unittest.skipUnless(RUN, "set LOANS_TESTCONTAINERS=1 (needs requirements-ci.txt and Docker/Podman)")
class PostgresStoreIntegrationTest(StoreContract, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from testcontainers.postgres import PostgresContainer

        cls.pg = PostgresContainer("postgres:16-alpine", driver=None)  # driver=None: plain postgresql:// URL
        cls.pg.start()
        cls.addClassCleanup(cls.pg.stop)

    def make_store(self):
        from postgres_store import PostgresLoanStore

        store = PostgresLoanStore(self.pg.get_connection_url())
        store._db.execute("TRUNCATE loans RESTART IDENTITY")  # fresh table per test, ids from 1
        self.addCleanup(store.close)
        return store


if __name__ == "__main__":
    unittest.main()
