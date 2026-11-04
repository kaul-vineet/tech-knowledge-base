"""tryIt experiments for the capstone (python try_it.py): switch one mechanism off and let the checks find it."""
from checks import evaluate
from outbox import IdempotentConsumer
from pipeline import Pipeline


class NoDedupe(IdempotentConsumer):  # tryIt 1: a consumer that applies every delivery
    def __call__(self, msg):
        self.processed.add(msg["id"])
        self.effect(msg)


class Amnesia(dict):  # tryIt 2: a gateway that forgets idempotency keys
    def __contains__(self, key):
        return False


for label, faults, patch in (("tryIt 1: consumers without dedupe, bus-duplicates", ("bus-duplicates",),
                              lambda p: setattr(p.bus, "subscribers", [NoDedupe(c.name, c.effect) for c in p.bus.subscribers])),
                             ("tryIt 2: gateway without idempotency keys, lost-acks", ("lost-acks",),
                              lambda p: setattr(p, "accepted", Amnesia()))):
    p = Pipeline(22, faults)
    patch(p)
    failed = {k: v for k, (ok, v) in evaluate(p.run()).items() if not ok}
    print(f"{label}: failed checks {failed or 'none'}")
