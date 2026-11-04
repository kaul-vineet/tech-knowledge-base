"""Equivalent check (pending-ci): sqlite-vec must return the same top-k as numpy. Skipped when unavailable."""
import importlib.util
import os
import sqlite3
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "L100", "01-setup"))
import rag  # noqa: E402
from fake_model_server import start_in_thread  # noqa: E402

AVAILABLE = importlib.util.find_spec("sqlite_vec") is not None and hasattr(sqlite3.Connection, "enable_load_extension")


@unittest.skipUnless(AVAILABLE, "needs sqlite-vec==0.1.9 and a Python whose sqlite3 can load extensions")
class SqliteVecAgrees(unittest.TestCase):
    def test_same_top_k(self):
        from sqlite_vec_equivalent import top_k_sqlite_vec
        server, url = start_in_thread()
        try:
            chunks = rag.load_chunks()
            vectors = rag.embed([t for _, t in chunks], url)
            for q in ["Which tools need human approval?", "Can I compare vectors from two different models?"]:
                mine = [(cid, score) for cid, _, score in rag.search(q, chunks, vectors, 2, url)]
                theirs = top_k_sqlite_vec(chunks, vectors, rag.embed([q], url)[0], k=2)
                self.assertEqual([c for c, _ in mine], [c for c, _ in theirs])
                for (_, a), (_, b) in zip(mine, theirs):
                    self.assertAlmostEqual(a, b, places=2)  # float32 in SQLite vs float64 in numpy
        finally:
            server.shutdown()


if __name__ == "__main__":
    unittest.main()
