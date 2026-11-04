"""Build-task check: compensate in reverse order, refund idempotently, recover from the saga log after a crash.
Default target = solution_saga.py. Test YOUR saga.py:  BUILD_TARGET=mine python -m unittest test_build_task -v
(PowerShell: $env:BUILD_TARGET="mine"; python -m unittest test_build_task -v)"""
import importlib.util, os, unittest
from pathlib import Path

from helpers import Crash, SagaLog, crash_once_after

HERE = Path(__file__).resolve().parent
FILE = "saga.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution_saga.py"
spec = importlib.util.spec_from_file_location("target_saga", HERE / FILE)
sg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sg)


class Compensation(unittest.TestCase):
    def test_failed_shipping_refunds_and_cancels(self):
        results, services, log, _ = sg.run_orders(fail_rate=0.3)
        self.assertEqual(sg.audit(*services), [])
        self.assertEqual(services[0].status["o1"], "CANCELLED")

    def test_compensations_run_in_reverse_order(self):
        _, _, log, _ = sg.run_orders(fail_rate=0.3)
        steps = [(r["step"], r["status"]) for r in log.entries("o1") if r["status"].startswith("compensat")]
        self.assertEqual(steps, [("charge", "compensating"), ("charge", "compensated"),
                                 ("create", "compensating"), ("create", "compensated"), ("saga", "compensated")])

    def test_crash_after_refund_then_recover_refunds_once(self):
        orders, payments, shipping = sg.Orders(), sg.Payments(), sg.Shipping(fail_rate=1.0)
        log = SagaLog()
        orch = sg.Orchestrator(orders, payments, shipping, log)
        orch.steps[1] = ("charge", payments.charge, crash_once_after(payments.refund))
        with self.assertRaises(Crash):
            orch.run("o1", 10)
        sg.Orchestrator(orders, payments, shipping, log).recover()
        self.assertEqual([a for s, a in payments.ledger if a < 0], [-10])
        self.assertEqual(sg.audit(orders, payments, shipping), [])
        sg.Orchestrator(orders, payments, shipping, log).recover()  # recovering twice changes nothing
        self.assertEqual(len(payments.ledger), 2)

    def test_crash_before_charge_is_logged_is_also_safe(self):
        orders, payments, shipping = sg.Orders(), sg.Payments(), sg.Shipping()
        log = SagaLog()
        orch = sg.Orchestrator(orders, payments, shipping, log)
        orch.steps[1] = ("charge", crash_once_after(payments.charge), payments.refund)
        with self.assertRaises(Crash):
            orch.run("o2", 20)
        sg.Orchestrator(orders, payments, shipping, log).recover()  # charge is in doubt -> compensated
        self.assertEqual(payments.net("o2"), 0)
        self.assertEqual(orders.status["o2"], "CANCELLED")


if __name__ == "__main__":
    unittest.main()
