"""Milestone 1: outbox + at-least-once bus + idempotent consumers."""
import random, unittest

from checks import evaluate
from outbox import Bus, IdempotentConsumer, OutboxDB, Relay
from pipeline import Pipeline


class Outbox(unittest.TestCase):
    def test_event_only_when_the_state_changed(self):
        db, state = OutboxDB("payments"), {"x": 0}
        db.transact(lambda: state.update(x=10), lambda: state["x"], "payment.charged", "o1", "tp")
        db.transact(lambda: None, lambda: state["x"], "payment.charged", "o1", "tp")  # idempotent no-op
        with self.assertRaises(ValueError):
            db.transact(lambda: int("boom"), lambda: state["x"], "payment.charged", "o1", "tp")  # failed change
        self.assertEqual(len(db.rows), 1)

    def test_relay_crash_republishes_and_the_consumer_absorbs_it(self):
        db, seen = OutboxDB("orders"), []
        db.transact(lambda: seen.append("created"), lambda: len(seen), "order.created", "o1", "tp")
        bus = Bus(random.Random(1))
        consumer = IdempotentConsumer("email", lambda m: seen.append(m["id"]))
        bus.subscribers.append(consumer)
        relay = Relay([db], bus)
        relay.crash_next = 1
        relay.tick()
        relay.tick()
        self.assertEqual((bus.published, consumer.duplicates, seen.count("orders-1")), (2, 1, 1))

    def test_pipeline_effects_once_under_duplicates_and_relay_crashes(self):
        p = Pipeline(22, ("relay-crash", "bus-duplicates")).run()
        r = evaluate(p)
        self.assertTrue(r["exactly-once effects"][0] and r["outbox delivered"][0], r)
        self.assertGreater(sum(c.duplicates for c in p.bus.subscribers), 0)


if __name__ == "__main__":
    unittest.main()
