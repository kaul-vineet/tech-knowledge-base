"""Try it (lesson 7): two small changes, run against the fake server. Run: python -m unittest -v test_try_it_07"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "L100", "01-setup"))
import rag  # noqa: E402
from fake_model_server import start_in_thread  # noqa: E402


class TryIt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.url = start_in_thread()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_1_smaller_chunks(self):
        # change chunk(max_words=40, overlap=10) to chunk(max_words=20, overlap=5)
        text = (rag.DOCS / "context-windows.md").read_text(encoding="utf-8")
        sizes = [len(c.split()) for c in rag.chunk(text, max_words=20, overlap=5)]
        print("\nobserved: chunk sizes", sizes)
        self.assertEqual(sizes, [20, 20, 10, 20, 14])

    def test_2_off_topic_question(self):
        chunks = rag.load_chunks()
        vectors = rag.embed([t for _, t in chunks], self.url)
        r = rag.answer("What is the capital of France?", chunks, vectors, base_url=self.url, model="m")
        print("\nobserved:", [(c, s) for c, _, s in r["hits"]], "->", r["answer"], "grounded =", r["grounded"])
        self.assertEqual([c for c, _, _ in r["hits"]], ["embeddings#1", "context-windows#1"])
        self.assertFalse(r["grounded"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
