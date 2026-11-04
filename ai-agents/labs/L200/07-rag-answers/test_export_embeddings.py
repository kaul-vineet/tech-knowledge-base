import csv
import io
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "L100", "01-setup"))
import export_embeddings  # noqa: E402
import rag  # noqa: E402
from fake_model_server import start_in_thread  # noqa: E402


class ExportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, url = start_in_thread()
        cls.chunks = rag.load_chunks()
        cls.vectors = rag.embed([t for _, t in cls.chunks], url)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_csv_one_row_per_chunk(self):
        out = io.StringIO()
        export_embeddings.write_csv(out, self.chunks, self.vectors)
        rows = list(csv.reader(io.StringIO(out.getvalue())))
        self.assertEqual(rows[0][:3], ["id", "source", "e0"])
        self.assertEqual(len(rows), 1 + 6)
        self.assertEqual({len(r) for r in rows}, {2 + 64})

    def test_nearest_neighbour_is_never_itself(self):
        pairs = export_embeddings.nearest_neighbours(self.chunks, self.vectors)
        self.assertEqual(len(pairs), 6)
        self.assertTrue(all(a != b for a, b, _ in pairs))


if __name__ == "__main__":
    unittest.main()
