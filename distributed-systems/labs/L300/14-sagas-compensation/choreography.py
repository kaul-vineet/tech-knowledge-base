"""Same saga, CHOREOGRAPHY style (python choreography.py): no orchestrator; each service reacts to events on a
bus and publishes the next one. The bus delivers at least once: with dup_rate > 0 (seeded) some events arrive
twice, so every handler - including the compensations - must be an idempotent consumer (lesson 8)."""
import random
from collections import deque

import saga as default


def run_choreography(n=6, fail_rate=0.3, dup_rate=0.0, seed=14, mod=default):
    orders, payments, shipping = mod.Orders(), mod.Payments(), mod.Shipping(fail_rate, seed)
    bus, rng, delivered = deque(), random.Random(seed + 1), []

    def ship(saga, amount):
        try:
            shipping.ship(saga, amount)
            return "Shipped"
        except mod.StepFailed:
            return "ShippingFailed"

    handlers = {  # event -> (service action, next event)
        "OrderPlaced": lambda s, a: (orders.create(s, a), payments.charge(s, a), "PaymentCharged")[-1],
        "PaymentCharged": ship,
        "Shipped": lambda s, a: orders.status.__setitem__(s, "APPROVED"),
        "ShippingFailed": lambda s, a: (payments.refund(s, a), "PaymentRefunded")[-1],  # compensation
        "PaymentRefunded": lambda s, a: orders.cancel(s, a),  # compensation
    }
    for i in range(1, n + 1):
        bus.append(("OrderPlaced", f"o{i}", 10 * i))
    while bus:
        event, saga, amount = bus.popleft()
        copies = 2 if rng.random() < dup_rate else 1  # at-least-once: sometimes the same event twice
        for _ in range(copies):
            delivered.append(event)
            nxt = handlers[event](saga, amount)
            if nxt:
                bus.append((nxt, saga, amount))
    return (orders, payments, shipping), delivered


if __name__ == "__main__":
    services, delivered = run_choreography()
    print(f"choreography: {len(delivered)} events delivered, audit:", default.audit(*services) or "OK")
