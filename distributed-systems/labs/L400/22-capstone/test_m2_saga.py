"""Milestone 2: the L300 saga (compensation + recover) running on the outbox."""
import unittest

from checks import evaluate
from pipeline import Pipeline
from reuse import SAGA

COHORT = frozenset({"o3", "o7", "o11"})


class Saga(unittest.TestCase):
    def test_shipping_outage_is_compensated(self):
        p = Pipeline(22, ("shipping-outage",), COHORT).run()
        self.assertEqual({s: p.orders.status[s] for s in COHORT}, {s: "CANCELLED" for s in COHORT})
        self.assertEqual([p.revenue[s] for s in sorted(COHORT)], [0, 0, 0])
        self.assertEqual(SAGA.audit(p.orders, p.payments, p.shipping), [])

    def test_crash_after_charge_is_recovered(self):
        p = Pipeline(22, ("crash-after-charge",), COHORT).run()
        self.assertEqual(p.crashed, set(COHORT))
        recovered = {r["saga"] for r in p.log.entries() if r["status"] == "recovering"}
        self.assertEqual(recovered, set(COHORT))
        r = evaluate(p)
        self.assertTrue(r["no lost orders"][0] and r["money invariant (audit)"][0], r)


if __name__ == "__main__":
    unittest.main()
