"""Capstone (python pipeline.py): an order pipeline built from the earlier labs, on simulated ticks, seeded.
gateway (bounded queue, 503 + Retry-After; L300 #16) -> workers -> orchestrated saga create/charge/ship with
compensation and recover() (L300 #14) -> every state change + its event in one outbox transaction -> relay ->
at-least-once bus -> idempotent consumers (email, revenue). Every order carries a W3C trace context (L300 #15);
the gateway's queue bound is replicated config committed through Raft (L300 #12). Faults are switched on by name."""
import random
from collections import Counter, defaultdict, deque

from outbox import Bus, IdempotentConsumer, OutboxDB, Relay
from reuse import BACKPRESSURE, RAFT, SAGA, TRACING

EVENTS = {"create": "order.created", "cancel": "order.cancelled", "charge": "payment.charged",
          "refund": "payment.refunded", "ship": "shipment.shipped"}
OWNER = {"create": "orders", "cancel": "orders", "charge": "payments", "refund": "payments", "ship": "shipping"}
CONFIG_CHANGES = {0: 8, 25: 12}  # tick -> wanted max_queue (an operator raises the bound at tick 25)
WORKERS, N_ORDERS, MAX_TICKS = 3, 60, 300


class Pipeline:
    def __init__(self, seed=22, faults=(), cohort=frozenset()):
        self.rng, self.t, self.faults, self.cohort = random.Random(seed), 0, set(faults), cohort
        self.raft, self.config = RAFT.lab_helpers.Cluster(RAFT.Node, seed), {"version": 0, "max_queue": 1}
        self.orders, self.payments, self.shipping = SAGA.Orders(), SAGA.Payments(), SAGA.Shipping(0.0, seed)
        self.log, self.dbs = SAGA.lab_helpers.SagaLog(), {n: OutboxDB(n) for n in ("orders", "payments", "shipping")}
        self.orch = SAGA.Orchestrator(self.orders, self.payments, self.shipping, self.log)
        self.orch.steps = [(n, self.outboxed(n, act), comp and self.outboxed(comp.__name__, comp))
                           for n, act, comp in self.orch.steps]  # every step and compensation goes through an outbox
        self.bus = Bus(self.rng, 0.2 if "bus-duplicates" in self.faults else 0.0)
        self.relay = Relay(list(self.dbs.values()), self.bus)
        self.emails, self.revenue, self.spans, self.trace, self.root = Counter(), defaultdict(int), [], {}, {}
        self.bus.subscribers += [IdempotentConsumer("email", self.email), IdempotentConsumer("revenue", self.book)]
        self.gateway, self.accepted, self.retries = BACKPRESSURE.Server(WORKERS, 1), {}, deque()
        self.queue_seen, self.waits, self.crashed, self.config_seen = [], [], set(), []

    def span(self, saga, name, parent):  # W3C-shaped ids from a seeded RNG (production: a CSPRNG)
        s = {"saga": saga, "name": name, "trace_id": self.trace[saga], "span_id": f"{self.rng.getrandbits(64):016x}",
             "parent_id": parent}
        self.spans.append(s)
        return s

    def outboxed(self, name, fn):
        """State change + its event in one local transaction, under a span whose traceparent rides on the event."""
        db = OWNER[name]
        state = {"orders": lambda s: self.orders.status.get(s), "payments": self.payments.net,
                 "shipping": lambda s: self.shipping.outcome.get(s)}[db]

        def step(saga, amount):
            faulty = saga in self.cohort
            if name == "ship" and faulty and "shipping-outage" in self.faults:
                self.shipping.outcome.setdefault(saga, "courier API down")  # fault: no courier for this order
            s = self.span(saga, f"{db}.{name}", self.root[saga])
            result = self.dbs[db].transact(lambda: fn(saga, amount), lambda: state(saga), EVENTS[name], saga,
                                           f"00-{s['trace_id']}-{s['span_id']}-01", amount=amount)
            if name == "charge" and faulty and "crash-after-charge" in self.faults and saga not in self.crashed:
                self.crashed.add(saga)
                raise SAGA.lab_helpers.Crash(f"orchestrator died after charge({saga})")  # fault: process dies
            return result
        step.__name__ = name
        return step

    def email(self, msg):
        self.consumer_span(msg, "email.send")
        self.emails[(msg["saga"], msg["type"])] += 1

    def book(self, msg):
        self.consumer_span(msg, "revenue.book")
        sign = {"payment.charged": 1, "payment.refunded": -1}.get(msg["type"], 0)
        self.revenue[msg["saga"]] += sign * msg["data"]["amount"]

    def consumer_span(self, msg, name):
        trace_id, parent, _ = TRACING.parse_traceparent(msg["traceparent"])  # context from the event header
        self.spans.append({"saga": msg["saga"], "name": name, "trace_id": trace_id,
                           "span_id": f"{self.rng.getrandbits(64):016x}", "parent_id": parent})

    def tick_config(self):
        """Operator: re-propose the wanted config until Raft commits it (the version makes retries idempotent);
        the pipeline applies only COMMITTED entries, and never an older version than it already has."""
        version = sum(k <= self.t for k in CONFIG_CHANGES)
        wanted = CONFIG_CHANGES[max(k for k in CONFIG_CHANGES if k <= self.t)]
        if "raft-leader-crash" in self.faults and self.t in (25, 40):
            if self.t == 25:
                self.downed = self.raft.leader().name
                self.raft.crash(self.downed)  # fault: the config leader dies just as the change arrives
            else:
                self.raft.restart(self.downed)
        leader = self.raft.leader()
        if leader:
            for _, cmd in leader.log[:leader.commit]:
                v, value = (int(x) for x in cmd.split(":"))
                if v > self.config["version"]:
                    self.config = {"version": v, "max_queue": value}
            if self.config["version"] < version and self.t % 5 == 0:
                leader.propose(f"{version}:{wanted}")
        self.gateway.max_queue = self.config["max_queue"]
        self.config_seen.append((self.t, self.config["version"]))
        self.raft.run(1)

    def submit(self, key, amount):
        """Client -> gateway with an idempotency key; on 503 the client retries after Retry-After (+ jitter)."""
        if key in self.accepted:
            return "duplicate"  # idempotent replay: the order exists, nothing new happens
        retry_after = self.gateway.admit(self.t)
        if retry_after is not None:  # bounded queue full: shed now, tell the client when to come back
            self.retries.append((self.t + retry_after + self.rng.randint(0, 2), key, amount))
            return "503"
        self.accepted[key] = amount
        self.gateway.queue.append((key, amount, self.t))
        self.span(key, "gateway.accept", self.root[key])
        if "lost-acks" in self.faults and self.rng.random() < 0.2:
            self.retries.append((self.t + 1, key, amount))  # the 200 got lost: the client retries anyway
        return "accepted"

    def run(self):
        arrivals = [(self.rng.randint(0, 30), f"o{i}", 10 * i) for i in range(1, N_ORDERS + 1)]
        arrivals += [(10, f"o{i}", 10 * i) for i in range(N_ORDERS + 1, N_ORDERS + 21)] if "burst" in self.faults else []
        for _, key, _ in arrivals:
            self.trace[key] = f"{self.rng.getrandbits(128):032x}"
            self.root[key] = self.span(key, "client.order", None)["span_id"]
        pending = deque(sorted(arrivals))
        while self.t < MAX_TICKS:
            self.tick_config()
            while pending and pending[0][0] <= self.t:
                self.submit(*pending.popleft()[1:])
            for due, key, amount in [self.retries.popleft() for _ in range(len(self.retries))]:
                if due <= self.t:
                    self.submit(key, amount)
                else:
                    self.retries.append((due, key, amount))
            self.queue_seen.append((len(self.gateway.queue), self.gateway.max_queue))
            for _ in range(min(WORKERS, len(self.gateway.queue))):
                key, amount, queued_at = self.gateway.queue.popleft()
                self.waits.append(self.t - queued_at)
                try:
                    self.orch.run(key, amount)
                except SAGA.lab_helpers.Crash:
                    self.orch.recover()  # the supervisor restarts it; it finishes from the saga log
            self.relay.crash_next = 1 if "relay-crash" in self.faults and self.t % 7 == 3 else 0
            self.relay.tick()
            self.t += 1
            settled = self.config["version"] == sum(k <= self.t for k in CONFIG_CHANGES)  # config change committed
            if settled and not (pending or self.retries or self.gateway.queue) and all(
                    r["sent"] for d in self.dbs.values() for r in d.rows):
                break
        self.raft.run(10)  # let followers learn the final commit index before anyone checks them
        return self


if __name__ == "__main__":
    p = Pipeline().run()
    done = Counter(r["status"] for r in p.log.entries() if r["step"] == "saga" and r["status"] != "started")
    print(f"ticks {p.t}, sagas {dict(done)}, events published {p.bus.published}, delivered {p.bus.delivered},"
          f" spans {len(p.spans)}, config {p.config}, audit: {SAGA.audit(p.orders, p.payments, p.shipping) or 'OK'}")
