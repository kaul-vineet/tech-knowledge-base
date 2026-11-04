"""Milestone 4: bounded admission with 503 + Retry-After, and idempotent client retries."""
import unittest

from checks import evaluate
from pipeline import Pipeline


class Backpressure(unittest.TestCase):
    def test_burst_is_shed_and_retried_without_loss(self):
        p = Pipeline(22, ("burst",)).run()
        r = evaluate(p)
        self.assertTrue(r["bounded queue"][0] and r["no lost orders"][0], r)
        self.assertEqual(len(p.trace), 80)
        self.assertTrue(any(q == bound for q, bound in p.queue_seen))  # the bound was actually reached

    def test_lost_acks_do_not_create_second_orders(self):
        p = Pipeline(22, ("lost-acks",)).run()
        self.assertTrue(evaluate(p)["one order and one charge per key"][0])


if __name__ == "__main__":
    unittest.main()
