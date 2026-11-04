"""Shared test fixture: one capstone service per test class, in a unique folder inside this lab (removed afterwards)."""
import random
import tempfile
import unittest
from pathlib import Path

import paths  # noqa: F401
import service

HERE = Path(__file__).resolve().parent


class ServiceCase(unittest.TestCase):
    docs = 4

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(dir=HERE, ignore_cleanup_errors=True)
        cls.ns = service.start(Path(cls.tmp.name))
        cls.ns.work = Path(cls.tmp.name)
        rng = random.Random(22)
        for i in range(1, cls.docs + 1):
            cls.ns.svc.put("alice", f"doc-{i}", f"contract {i}: price {rng.randrange(100, 999)}".encode(), readers=("bob", "mallory"))
            cls.ns.clock.advance(1)

    @classmethod
    def tearDownClass(cls):
        service.stop(cls.ns)
        cls.tmp.cleanup()
