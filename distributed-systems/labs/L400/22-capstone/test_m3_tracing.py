"""Milestone 3: one W3C trace per order, across the saga steps, the outbox, the bus and the consumers."""
import unittest

from checks import evaluate
from pipeline import Pipeline


class Tracing(unittest.TestCase):
    def setUp(self):
        self.p = Pipeline(22).run()

    def test_one_trace_per_order_no_orphans(self):
        self.assertTrue(evaluate(self.p)["one trace per order"][0])
        self.assertEqual(len(self.p.spans), 60 * 11)  # client, gateway, 3 steps, 2 consumers x 3 events

    def test_consumer_spans_hang_under_the_step_that_emitted_the_event(self):
        by_id = {s["span_id"]: s for s in self.p.spans}
        parents = {by_id[s["parent_id"]]["name"] for s in self.p.spans if s["name"] == "revenue.book"}
        self.assertEqual(parents, {"orders.create", "payments.charge", "shipping.ship"})

    def test_a_broken_header_is_caught(self):
        self.p.dbs["orders"].rows[0]["traceparent"] = "00-xyz"
        self.assertFalse(evaluate(self.p)["one trace per order"][0])


if __name__ == "__main__":
    unittest.main()
