"""tryIt experiments for lesson 5 (python try_it.py). Prints what actually happens."""
import random, uuid

import idempotency as idem


def fresh_b(loss_rate):
    idem.PaymentB.enforce, idem.PaymentB.rng, idem.PaymentB.loss_rate = True, random.Random(3), loss_rate
    idem.PaymentB.ledger.clear(); idem.PaymentB.store.clear()
    srv = idem.serve(idem.PaymentB)
    return srv, f"http://127.0.0.1:{srv.server_port}/charges"


# tryIt 1: BUG - generate a new key on every attempt (inside the retry loop), 5 orders x 10
srv, url = fresh_b(0.4)
for order in range(5):
    while idem.pay(url, 10, str(uuid.uuid4()), max_attempts=1)[0] is None:  # new key per try
        pass
print(f"tryIt 1: new key per attempt -> ledger {len(idem.PaymentB.ledger)} charges, "
      f"total {sum(idem.PaymentB.ledger)} (expected 50)")
srv.shutdown(); srv.server_close()

# tryIt 2: no lost responses; send the SAME key 3 times
srv, url = fresh_b(0.0)
key = str(uuid.uuid4())
answers = [idem.pay(url, 10, key)[:2] for _ in range(3)]
print(f"tryIt 2: same key x3 -> {answers}; ledger {len(idem.PaymentB.ledger)} charge(s)")
srv.shutdown(); srv.server_close()
