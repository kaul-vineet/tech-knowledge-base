"""Build task check (failureLab proof). Default: tests solution_retire.py.
Test YOUR version:  macOS  BUILD_IMPL=envelope python -m unittest -v test_build_task
                    Windows  $env:BUILD_IMPL="envelope"; python -m unittest -v test_build_task"""
import importlib
import os
import unittest

import envelope as env

impl = importlib.import_module(os.environ.get("BUILD_IMPL", "solution_retire"))
QUIET = lambda line: None  # noqa: E731


def crashed_store(n=6, crash_after=2):
    ring = env.Keyring()
    store = {f"r{i}": env.seal(ring, f"secret {i}".encode(), f"r{i}") for i in range(n)}
    ring.rotate()
    try:
        env.rewrap_job(ring, store, log=QUIET, crash_after=crash_after)  # injected fault: job dies part-way
    except RuntimeError:
        pass
    return ring, store


class TestRetireAfterRewrap(unittest.TestCase):
    def test_retire_refused_while_records_use_the_version(self):
        ring, store = crashed_store()
        with self.assertRaises(env.KeyInUse):
            impl.retire(ring, store, 1)
        self.assertIn(1, ring.versions)
        self.assertEqual(env.try_all(ring, store), "6/6 decrypt")  # nothing lost

    def test_retire_succeeds_after_resumed_rewrap(self):
        ring, store = crashed_store()
        self.assertEqual(env.rewrap_job(ring, store, log=QUIET), 4)  # resumes: only the 4 not yet moved
        impl.retire(ring, store, 1)
        self.assertNotIn(1, ring.versions)
        self.assertEqual(env.try_all(ring, store), "6/6 decrypt")

    def test_primary_cannot_be_retired(self):
        ring = env.Keyring()
        with self.assertRaises(env.KeyInUse):
            impl.retire(ring, {}, ring.primary)


if __name__ == "__main__":
    unittest.main()
