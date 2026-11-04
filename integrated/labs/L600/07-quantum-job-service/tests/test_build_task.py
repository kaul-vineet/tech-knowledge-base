"""Build task: a fenced, idempotent ledger. Checks solution/ledger.py by default.

Your file: copy ledger.py to my_ledger.py (lab folder) and fix Ledger.new_slot/write/read.
  macOS:   BUILD_TARGET=mine python -m unittest discover -s tests -p "test_build_task.py" -v
  Windows: $env:BUILD_TARGET = "mine"; python -m unittest discover -s tests -p "test_build_task.py" -v
Fail-before proof: an unmodified copy of ledger.py fails 3 of 4 (lease expiry, replayed attempt, stale token).
"""
import unittest

import shared  # noqa: F401
import scenarios
from ledger_loader import ledger_class


class BuildTask(unittest.TestCase):
    def setUp(self):
        self.ledger = ledger_class()()
        self.ledger.open("j", 2)

    def test_lease_expiry_exact_shots(self):
        lab = scenarios.lease_expiry()                              # uses ledger_class(): your ledger with BUILD_TARGET=mine
        self.assertEqual(lab["returned"], lab["requested"])

    def test_stale_token_rejected(self):
        t1, t2 = self.ledger.grant("j", 0), self.ledger.grant("j", 0)
        self.assertTrue(self.ledger.commit("j", 0, t2, 1, {"00": 600, "11": 400})[0].startswith("accepted"))
        self.assertFalse(self.ledger.commit("j", 0, t1, 1, {"00": 600, "11": 400})[0].startswith("accepted"))
        self.assertEqual(sum(self.ledger.counts("j").values()), 1000)

    def test_replayed_attempt_is_idempotent(self):
        t = self.ledger.grant("j", 1)
        for _ in range(3):
            self.ledger.commit("j", 1, t, 1, {"01": 1000})
        self.assertEqual(self.ledger.counts("j"), {"01": 1000})

    def test_chunk_done_only_after_a_write(self):
        self.assertFalse(self.ledger.chunk_done("j", 0))
        self.ledger.commit("j", 0, self.ledger.grant("j", 0), 1, {"00": 1000})
        self.assertTrue(self.ledger.chunk_done("j", 0))
        self.assertFalse(self.ledger.complete("j"))


if __name__ == "__main__":
    unittest.main()
