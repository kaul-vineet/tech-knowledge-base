import unittest

import broker as b
from helpers import SimClock, call, serve


class TestBrokerSemantics(unittest.TestCase):
    def setUp(self):
        self.clock = SimClock()
        b.Broker.reset(self.clock)
        self.srv = serve(b.Broker)
        self.url = f"http://127.0.0.1:{self.srv.server_port}"
        call(self.url + "/send", {"body": "x"})

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()

    def test_received_message_is_invisible_until_the_timeout_then_redelivered(self):
        first = call(self.url + "/receive", {})[1]
        self.assertEqual(call(self.url + "/receive", {})[0], 404)  # in flight -> hidden
        self.clock.advance(b.VISIBILITY)
        again = call(self.url + "/receive", {})[1]
        self.assertEqual((again["id"], again["receives"]), (first["id"], 2))  # same message, 2nd delivery

    def test_ack_deletes_and_a_stale_receipt_is_refused(self):
        first = call(self.url + "/receive", {})[1]
        self.clock.advance(b.VISIBILITY)
        second = call(self.url + "/receive", {})[1]
        self.assertEqual(call(self.url + "/ack", {"receipt": first["receipt"]})[0], 409)
        self.assertEqual(call(self.url + "/ack", {"receipt": second["receipt"]})[0], 200)
        self.clock.advance(b.VISIBILITY)
        self.assertEqual(call(self.url + "/receive", {})[0], 404)  # acked = gone for good

    def test_dead_letter_after_max_receives(self):
        for _ in range(b.MAX_RECEIVES):
            self.assertEqual(call(self.url + "/receive", {})[0], 200)
            self.clock.advance(b.VISIBILITY)
        self.assertEqual(call(self.url + "/receive", {})[0], 404)
        self.assertEqual([m["body"] for m in b.Broker.dlq], ["x"])


class TestDemo(unittest.TestCase):
    def test_every_order_charged_at_least_once_with_duplicates(self):
        out = b.run(quiet=True)
        ids = [i for i, _ in out["ledger"]]
        self.assertEqual(sorted(set(ids)), ["m1", "m2", "m3", "m4", "m5", "m6"])  # nothing lost
        self.assertEqual(len(ids), 9)  # ... but 3 duplicate charges (seed 9)
        self.assertEqual(out["dlq"], ["poison"])


if __name__ == "__main__":
    unittest.main()
