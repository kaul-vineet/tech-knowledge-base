"""Try it (lesson 9): a relay crash and a renamed field. Run: python try_it.py"""
from asyncapi_check import load, validate_event
from bus import InProcessBus
from consumers import NotificationConsumer
from events import new_event
from outbox import LoansWithOutbox, Relay


class CrashOnceRelay(Relay):
    """Crashes after handing the event to the bus but before recording it as published."""

    crashed = False

    def _mark_published(self, seq):
        if not self.crashed:
            self.crashed = True
            raise RuntimeError("relay process killed")
        super()._mark_published(seq)


class NaiveNotifier:
    def __init__(self):
        self.sent = []

    def __call__(self, event):
        self.sent.append(f"to {event['memberId']}: you borrowed {event['bookId']}")


def try_1_crash_between_publish_and_mark():
    loans, bus = LoansWithOutbox(), InProcessBus()
    naive, idempotent = NaiveNotifier(), NotificationConsumer()
    bus.subscribe("loanCreated", naive)
    bus.subscribe("loanCreated", idempotent)
    relay = CrashOnceRelay(loans.db, bus)
    loans.borrow("b1", "m1")
    try:
        relay.publish_pending()
    except RuntimeError as exc:
        print(f"[1] relay run 1 -> {exc}; outbox pending: {loans.pending()}")
    relay.publish_pending()
    print(f"[1] relay run 2 -> naive consumer sent {len(naive.sent)} mails, "
          f"idempotent consumer sent {len(idempotent.sent)} (ignored {idempotent.duplicates} duplicate)")


def try_2_rename_a_field():
    event = new_event("LoanCreated", {"loanId": 1, "bookId": "b1", "memberId": "m1"})
    event["book"] = event.pop("bookId")  # a producer "tidies up" a field name
    print(f"[2] bookId -> book: {validate_event(load(), 'loanCreated', event)}")


if __name__ == "__main__":
    try_1_crash_between_publish_and_mark()
    try_2_rename_a_field()
