import os
import subprocess
import sys
import unittest

import numpy as np
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "L100", "01-setup"))
import rag  # noqa: E402
from fake_model_server import start_in_thread  # noqa: E402


class RagTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.url = start_in_thread()
        cls.chunks = rag.load_chunks()
        cls.vectors = rag.embed([t for _, t in cls.chunks], cls.url)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_chunking_windows_overlap(self):
        words = " ".join(f"w{i}" for i in range(50))
        parts = rag.chunk(words, max_words=20, overlap=5)
        self.assertEqual([len(p.split()) for p in parts], [20, 20, 20])
        self.assertEqual(parts[1].split()[0], "w15")  # 5 words shared with the previous window
        self.assertEqual(rag.chunk("# Title\n\nshort para"), ["short para"])

    def test_vectors_are_unit_length(self):
        self.assertEqual(self.vectors.shape, (6, 64))
        self.assertTrue(np.allclose(np.linalg.norm(self.vectors, axis=1), 1.0))

    def test_both_embedding_routes_agree(self):
        v1 = requests.post(f"{self.url}/embeddings", json={"model": "m", "input": "context window"}, timeout=5).json()
        native = self.url.replace("/v1", "/api/embed")
        v2 = requests.post(native, json={"model": "m", "input": ["context window"]}, timeout=5).json()
        self.assertEqual(v1["data"][0]["embedding"], v2["embeddings"][0])
        self.assertEqual(requests.post(f"{self.url}/embeddings", json={"model": "m"}, timeout=5).status_code, 400)

    def test_answer_is_grounded_and_cited(self):
        r = rag.answer("Which tools need human approval?", self.chunks, self.vectors, base_url=self.url, model="m")
        self.assertEqual([h[0] for h in r["hits"]], ["tool-safety#1", "tool-safety#0"])
        self.assertEqual(r["cited"], ["tool-safety#1"])
        self.assertTrue(r["grounded"])

    def test_uncited_answer_is_not_grounded(self):
        r = rag.answer("What is the capital of France?", self.chunks, self.vectors, base_url=self.url, model="m")
        self.assertEqual((r["answer"], r["grounded"]), ("I don't know based on the provided context.", False))

    def test_cli_runs(self):
        env = dict(os.environ, LOCAL_MODEL_URL=self.url, LOCAL_MODEL="fake-model", PYTHONIOENCODING="utf-8")
        out = subprocess.run([sys.executable, "rag.py"], cwd=HERE, env=env, capture_output=True,
                             encoding="utf-8", check=True).stdout
        self.assertIn("6 chunks, vectors (6, 64)", out)
        self.assertIn("4096-token context window by default", out)


if __name__ == "__main__":
    unittest.main()
