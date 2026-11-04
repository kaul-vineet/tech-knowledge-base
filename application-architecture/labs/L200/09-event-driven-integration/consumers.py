"""Consumers react to events. They must be idempotent: the same event can arrive twice."""
from collections import Counter


class IdempotentConsumer:
    def __init__(self):
        self.seen = set()  # real systems keep this in their own table (an "inbox"), not in memory
        self.duplicates = 0

    def __call__(self, event):
        if event["eventId"] in self.seen:  # idempotency: a redelivered event changes nothing
            self.duplicates += 1
            return
        self.handle(event)
        self.seen.add(event["eventId"])

    def handle(self, event):
        raise NotImplementedError


class NotificationConsumer(IdempotentConsumer):
    def __init__(self):
        super().__init__()
        self.sent = []

    def handle(self, event):
        verb = "you borrowed" if event["eventType"] == "LoanCreated" else "thanks for returning"
        self.sent.append(f"to {event['memberId']}: {verb} {event['bookId']}")


class ActiveLoansProjection(IdempotentConsumer):
    """A read model built only from events: active loans per member."""

    def __init__(self):
        super().__init__()
        self.active = Counter()

    def handle(self, event):
        self.active[event["memberId"]] += 1 if event["eventType"] == "LoanCreated" else -1
