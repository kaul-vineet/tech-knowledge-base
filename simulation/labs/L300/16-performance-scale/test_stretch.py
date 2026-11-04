"""Stretch check (lesson 16): chunked, reproducible parallel replications.

By default this checks solution/chunked.py. To check your own chunked.py (in this folder) instead:
    BUILD_TARGET=mine python -m unittest test_stretch -v        (PowerShell: $env:BUILD_TARGET = "mine")
"""
import os
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE if os.environ.get("BUILD_TARGET") == "mine" else HERE / "solution"))
import chunked as SOLUTION  # noqa: E402
import perf  # noqa: E402


class TestChunked(unittest.TestCase):
    def test_same_results_for_any_worker_count_and_chunk_size(self):
        reference = perf.mean_wait_vectorised(*map(np.array, zip(*[perf.draws(c) for c in
                                                                    np.random.SeedSequence(perf.SEED).spawn(10)])))
        for workers, chunk in ((1, 10), (2, 3), (3, 4)):
            with self.subTest(workers=workers, chunk=chunk):
                np.testing.assert_array_equal(SOLUTION.run_chunked(10, workers, chunk), reference)


if __name__ == "__main__":
    unittest.main()
