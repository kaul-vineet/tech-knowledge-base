"""Build task check: relay retries a failing event, dead-letters it after 3 attempts, keeps the rest flowing.

By default this checks solution/outbox.py. To check your edited outbox.py instead:
    CHECK_MINE=1 python -m unittest test_build_task -v        (PowerShell: $env:CHECK_MINE = "1")
"""
import importlib.util
import os
import pathlib
import unittest

from bus import InProcessBus
from consumers import NotificationConsumer

HERE = pathlib.Path(__file__).resolve().parent
TARGET = HERE / ("outbox.py" if os.environ.get("CHECK_MINE") else "solution/outbox.py")
spec = importlib.util.spec_from_file_location("outbox_under_test", TARGET)
ob = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ob)


class FlakyMailer:
    """Fails for book 'b-poison' always, and for every other event the first time it sees it."""

    def __init__(self):
        self.failed_once = set()

    def __call__(self, event):
        if event["bookId"] == "b-poison":
            raise RuntimeError("mailbox does not exist")
        if event["eventId"] not in self.failed_once:
            self.failed_once.add(event["eventId"])
            raise TimeoutError("mail server slow")


class DeadLetterTest(unittest.TestCase):
    def setUp(self):
        self.loans = ob.LoansWithOutbox()
        self.bus, self.notify = InProcessBus(), NotificationConsumer()
        self.bus.subscribe("loanCreated", self.notify)  # succeeds, so it will see redeliveries
        self.bus.subscribe("loanCreated", FlakyMailer())
        self.relay = ob.Relay(self.loans.db, self.bus)
        self.loans.borrow("b-poison", "m1")
        self.loans.borrow("b2", "m2")

    def test_failure_does_not_block_later_events(self):
        self.assertEqual(self.relay.publish_pending(), 0)  # both fail on the first run
        self.assertEqual(self.relay.publish_pending(), 1)  # b2 succeeds on retry; poison fails again
        self.assertEqual(self.loans.pending(), 1)

    def test_poison_event_is_dead_after_three_attempts(self):
        for _ in range(3):
            self.relay.publish_pending()
        self.assertEqual(self.loans.pending(), 0)
        seq, attempts, error = self.loans.dead_letters()[0]
        self.assertEqual((seq, attempts, error), (1, 3, "RuntimeError: mailbox does not exist"))
        self.assertEqual(self.relay.publish_pending(), 0)  # dead rows are skipped

    def test_redelivery_stays_idempotent(self):
        for _ in range(3):
            self.relay.publish_pending()
        self.assertEqual(self.notify.sent, ["to m1: you borrowed b-poison", "to m2: you borrowed b2"])
        self.assertEqual(self.notify.duplicates, 3)


if __name__ == "__main__":
    unittest.main()
