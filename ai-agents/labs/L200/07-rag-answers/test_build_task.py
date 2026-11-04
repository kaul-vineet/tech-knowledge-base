"""Build task (lesson 7): a min_score threshold that refuses without calling the model."""
import os
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "solution"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "L100", "01-setup"))
import rag  # noqa: E402
from fake_model_server import start_in_thread  # noqa: E402
from rag_min_score import answer_with_threshold  # noqa: E402


class BuildTask(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.url = start_in_thread()
        cls.chunks = rag.load_chunks()
        cls.vectors = rag.embed([t for _, t in cls.chunks], cls.url)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_weak_hits_refused_without_model_call(self):
        with mock.patch.object(rag, "ask", side_effect=AssertionError("model must not be called")):
            r = answer_with_threshold("What is the capital of France?", self.chunks, self.vectors, base_url=self.url)
        self.assertEqual(r["answer"], "I don't know: no chunk scored >= 0.2.")  # best hash-collision score was 0.183

    def test_strong_hits_still_answered(self):
        r = answer_with_threshold("Which tools need human approval?", self.chunks, self.vectors,
                                  base_url=self.url, model="m")
        self.assertTrue(r["grounded"])


if __name__ == "__main__":
    unittest.main()
