"""buildTask solution (lesson 16): send replications to workers in chunks, keep one stream per replication.

Fewer, bigger tasks cut pickling/IPC overhead; tying seeds to replication indices (not to workers or chunks)
keeps every result bit-identical whatever the worker count or chunk size.
python solution/chunked.py
"""
import multiprocessing as mp
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import perf  # noqa: E402


def run_chunk(chunk):
    """Worker: a list of (rep, SeedSequence) -> list of mean waits, computed in one vectorised call."""
    data = [perf.draws(seed_seq) for _, seed_seq in chunk]
    return perf.mean_wait_vectorised(np.array([s for s, _ in data]), np.array([g for _, g in data])).tolist()


def run_chunked(reps, workers, chunk_size):
    tasks = list(enumerate(np.random.SeedSequence(perf.SEED).spawn(reps)))  # seed i belongs to replication i
    chunks = [tasks[i:i + chunk_size] for i in range(0, reps, chunk_size)]
    with mp.get_context("spawn").Pool(workers) as pool:
        parts = pool.map(run_chunk, chunks)  # map keeps chunk order, so results stay in replication order
    return np.array([x for part in parts for x in part])


if __name__ == "__main__":
    a = run_chunked(40, 1, 40)
    b = run_chunked(40, 2, 7)
    print(f"1 worker x 1 chunk vs 2 workers x chunks of 7: identical = {np.array_equal(a, b)}; "
          f"mean wait {a.mean():.3f} min")
