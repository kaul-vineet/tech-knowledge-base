"""Capstone building block: transactional outbox + at-least-once bus + idempotent consumers.
A service's state change and the event describing it are written in ONE local transaction (the outbox row); a relay
publishes unsent rows and marks them sent - if it dies in between, the row is published again (at-least-once).
Consumers keep the ids of processed events in the same transaction as their effect, so duplicates change nothing
(L100 #5 idempotency keys, L200 #8 idempotent consumer, application-architecture L200 #9 outbox)."""
import json


class OutboxDB:
    """One service's database: business rows are done by the wrapped call; outbox rows are appended with them."""
    def __init__(self, name):
        self.name, self.rows, self.seq = name, [], 0

    def transact(self, change, snapshot, event_type, saga, traceparent, **data):
        """Run the state change; append its event only if it succeeded AND changed something (an idempotent
        no-op, e.g. a refund re-run by recover(), must not publish a second 'refunded' event)."""
        before = snapshot()
        result = change()  # raises -> no event (the change did not happen)
        if snapshot() != before:
            self.seq += 1
            self.rows.append({"id": f"{self.name}-{self.seq}", "type": event_type, "saga": saga,
                              "traceparent": traceparent, "data": data, "sent": False})
        return result


class Bus:
    """At-least-once delivery: every published message reaches every subscriber, some of them twice (seeded)."""
    def __init__(self, rng, dup_rate=0.0):
        self.rng, self.dup_rate, self.subscribers, self.published, self.delivered = rng, dup_rate, [], 0, 0

    def publish(self, msg):
        self.published += 1
        for _ in range(2 if self.rng.random() < self.dup_rate else 1):
            for handler in self.subscribers:
                self.delivered += 1
                handler(json.loads(json.dumps(msg)))  # consumers get a copy, as over a real network


class Relay:
    """Polls the outboxes, publishes unsent rows, then marks them sent. crash_next simulates dying in between."""
    def __init__(self, dbs, bus):
        self.dbs, self.bus, self.crash_next = dbs, bus, 0

    def tick(self):
        for db in self.dbs:
            for row in [r for r in db.rows if not r["sent"]]:
                self.bus.publish({k: row[k] for k in ("id", "type", "saga", "traceparent", "data")})
                if self.crash_next:
                    self.crash_next -= 1
                    return  # relay died after publishing, before marking: this row goes out again next tick
                row["sent"] = True


class IdempotentConsumer:
    """Applies each event id once: the processed-id set and the effect change together."""
    def __init__(self, name, effect):
        self.name, self.effect, self.processed, self.duplicates = name, effect, set(), 0

    def __call__(self, msg):
        if msg["id"] in self.processed:
            self.duplicates += 1
            return
        self.processed.add(msg["id"])
        self.effect(msg)
