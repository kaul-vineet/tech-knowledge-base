"""tryIt experiments for lesson 14 (python try_it.py). Prints what actually happens."""
import choreography
import saga
import solution_saga as sol
from helpers import Crash, SagaLog, crash_once_after


def crash_during_refund(refund_is_idempotent):
    """Solution orchestrator; the orchestrator dies right after the first refund call, a new one recovers."""
    orders, payments, shipping = sol.Orders(), sol.Payments(), sol.Shipping(fail_rate=1.0)
    if not refund_is_idempotent:
        payments.refund = saga.Payments.refund.__get__(payments)  # the lesson's plain refund
    log = SagaLog()
    orch = sol.Orchestrator(orders, payments, shipping, log)
    orch.steps[1] = ("charge", payments.charge, crash_once_after(payments.refund))
    try:
        orch.run("o1", 10)
    except Crash as e:
        print("   ", e)
    sol.Orchestrator(orders, payments, shipping, log).recover()
    refunds = [a for s, a in payments.ledger if a < 0]
    return refunds, saga.audit(orders, payments, shipping) or "OK"


# tryIt 1: crash between "refund executed" and "refund logged", then recover from the saga log
for idem in (False, True):
    refunds, verdict = crash_during_refund(idem)
    print(f"tryIt 1: idempotent refund={idem}: refunds {refunds}, audit: {verdict}")

# tryIt 2: choreography over an at-least-once bus that duplicates about 20% of the events
for name, mod in (("lesson Payments", saga), ("solution Payments", sol)):
    services, delivered = choreography.run_choreography(dup_rate=0.2, mod=mod)
    print(f"tryIt 2: {name}: {len(delivered)} deliveries, audit:", *(saga.audit(*services) or ["OK"]), sep=" | ")
