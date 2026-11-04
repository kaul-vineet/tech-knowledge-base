"""L300 lesson 14 (python saga.py): an order saga across three services - orders, payments, shipping - each
owning its own data (no shared database, no distributed transaction). An orchestrator runs the steps in order
and records each one in a saga log (JSON lines). Happy path: every order ships. Fault (seeded): the shipping
service has no courier slot for some orders. Watch what the lesson code does with the money."""
import random

from helpers import SagaLog, StepFailed


class Orders:
    def __init__(self):
        self.status, self.amount = {}, {}

    def create(self, saga, amount):
        self.status[saga], self.amount[saga] = "PENDING", amount

    def cancel(self, saga, amount):  # compensation for create
        self.status[saga] = "CANCELLED"


class Payments:
    def __init__(self):
        self.ledger = []  # (saga, +amount) for a charge, (saga, -amount) for a refund

    def charge(self, saga, amount):  # idempotency key = saga id (lesson 5): a retried charge is a no-op
        if not any(s == saga and a > 0 for s, a in self.ledger):
            self.ledger.append((saga, amount))

    def refund(self, saga, amount):  # compensation for charge (semantic undo: a new entry, not a delete)
        self.ledger.append((saga, -amount))

    def net(self, saga):
        return sum(a for s, a in self.ledger if s == saga)


class Shipping:
    def __init__(self, fail_rate=0.0, seed=14):
        self.rng, self.fail_rate, self.outcome = random.Random(seed), fail_rate, {}

    def ship(self, saga, amount):  # the last step: once it succeeds the saga cannot be undone (pivot)
        if saga not in self.outcome:  # idempotent: decide once per saga, a retry gets the same answer
            failed = self.rng.random() < self.fail_rate  # fault injection: seeded -> same orders fail every run
            self.outcome[saga] = "no courier slot" if failed else "shipped"
        if self.outcome[saga] != "shipped":
            raise StepFailed(self.outcome[saga])

    @property
    def shipped(self):
        return {s for s, o in self.outcome.items() if o == "shipped"}


class Orchestrator:
    def __init__(self, orders, payments, shipping, log):
        self.orders, self.payments, self.log = orders, payments, log
        self.steps = [("create", orders.create, orders.cancel), ("charge", payments.charge, payments.refund),
                      ("ship", shipping.ship, None)]  # (step, action, compensating action)

    def run(self, saga, amount):
        self.log.write(saga, "saga", "started", amount=amount)
        for name, action, _compensation in self.steps:
            try:
                action(saga, amount)
            except StepFailed as e:
                self.log.write(saga, name, "failed", error=str(e))
                self.orders.status[saga] = "FAILED"  # tell the customer ... and keep their money?
                return "failed"
            self.log.write(saga, name, "done")
        self.orders.status[saga] = "APPROVED"
        self.log.write(saga, "saga", "completed")
        return "completed"


def audit(orders, payments, shipping):
    """Invariant, checked from each service's own data: a shipped order is APPROVED and paid in full; an order
    that did not ship is not APPROVED and the shop keeps none of its money. Returns the violations."""
    bad = []
    for s, status in sorted(orders.status.items()):
        shipped = s in shipping.shipped
        if payments.net(s) != (orders.amount[s] if shipped else 0) or (status == "APPROVED") != shipped:
            bad.append(f"{s}: {status}, shipped={shipped}, money kept={payments.net(s)} of {orders.amount[s]}")
    return bad


def run_orders(n=6, fail_rate=0.0, seed=14, orchestrator_class=Orchestrator):
    services = Orders(), Payments(), Shipping(fail_rate, seed)
    log = SagaLog()
    orch = orchestrator_class(*services, log)
    results = {f"o{i}": orch.run(f"o{i}", 10 * i) for i in range(1, n + 1)}
    return results, services, log, orch


if __name__ == "__main__":
    results, services, log, _ = run_orders()
    print("happy path:", results, "| audit:", audit(*services) or "OK")
    results, services, log, _ = run_orders(fail_rate=0.3)
    print("fault (30% of shipments fail, seed 14):", results)
    failed = [s for s, r in results.items() if r != "completed"]
    print(f"saga log of {failed[0]} (JSON lines):", *(l for l in log.lines if f'"{failed[0]}"' in l), sep="\n  ")
    print("audit:", *(audit(*services) or ["OK"]), sep="\n  ")
