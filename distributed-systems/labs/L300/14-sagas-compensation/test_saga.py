"""python -m unittest -v : lesson 14 happy path, idempotent forward steps, saga log, choreography, the fault."""
import json
import unittest

import choreography
import saga


class HappyPath(unittest.TestCase):
    def test_all_orders_ship_and_audit_is_clean(self):
        results, services, log, _ = saga.run_orders()
        self.assertEqual(set(results.values()), {"completed"})
        self.assertEqual(saga.audit(*services), [])
        self.assertEqual(json.loads(log.lines[-1]), {"saga": "o6", "step": "saga", "status": "completed"})

    def test_forward_steps_are_idempotent(self):
        payments, shipping = saga.Payments(), saga.Shipping(fail_rate=0.5, seed=1)
        payments.charge("o1", 10)
        payments.charge("o1", 10)  # a retry after a timeout
        self.assertEqual(payments.net("o1"), 10)
        first = [self._ship(shipping, "o1") for _ in range(3)]
        self.assertEqual(len(set(first)), 1)  # same decision on every retry

    @staticmethod
    def _ship(shipping, saga_id):
        try:
            shipping.ship(saga_id, 10)
            return "shipped"
        except saga.StepFailed as e:
            return str(e)

    def test_choreography_reaches_the_same_outcome(self):
        services, delivered = choreography.run_choreography()
        _, orch_services, _, _ = saga.run_orders(fail_rate=0.3)
        self.assertEqual(services[2].shipped, orch_services[2].shipped)  # same seed -> same shipments
        self.assertEqual(saga.audit(*services), [])
        self.assertIn("PaymentRefunded", delivered)


class FailureLabSymptom(unittest.TestCase):
    def test_lesson_orchestrator_keeps_money_for_unshipped_orders(self):
        results, services, log, _ = saga.run_orders(fail_rate=0.3)
        self.assertEqual([s for s, r in results.items() if r == "failed"], ["o1", "o5", "o6"])
        self.assertEqual(len(saga.audit(*services)), 3)
        self.assertFalse([l for l in log.lines if "compensat" in l])


if __name__ == "__main__":
    unittest.main()
