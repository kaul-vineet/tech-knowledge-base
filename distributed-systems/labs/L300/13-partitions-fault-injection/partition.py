"""L300 lesson 13 (python partition.py): fault injection with a Toxiproxy-style proxy. Three nodes reach the
lease store (lesson 7) and a shared register ("storage") only through the proxy. Happy path: one leader serves
client writes and reads. Fault: a partition cuts n1 off the lease store; n2 takes the lease and for a while
TWO nodes believe they lead and both write. The client history is printed as JSON lines and checked for
linearizability (checker.py). Seeded, simulated ticks: identical output on every run."""
import random

from checker import check_register, describe, stale_reads
from helpers import LeaseStore, jsonl

TTL = 3.0


class Timeout(Exception):
    pass


class Proxy:
    """Toxiproxy concepts: a link per (src, dst); 'down' (enabled=false) and 'drop' (toxicity) lose the request,
    'latency' delays it. A lost request is a Timeout to the caller: it cannot tell 'down' from 'slow'."""
    def __init__(self, seed=13):
        self.rng, self.toxics = random.Random(seed), {}

    def add(self, src, dst, **toxic):
        self.toxics.setdefault((src, dst), {}).update(toxic)

    def partition(self, side_a, side_b):
        for a in side_a:
            for b in side_b:
                self.add(a, b, down=True)
                self.add(b, a, down=True)

    def heal(self):
        self.toxics.clear()

    def call(self, src, dst, fn, *args):
        t = self.toxics.get((src, dst), {})
        if t.get("down") or self.rng.random() < t.get("drop", 0.0):
            raise Timeout(f"{src}->{dst}")
        return fn(*args), t.get("latency", 0.0)


class Storage:
    """The shared register every leader writes. (Build task: make it check fencing tokens.)"""
    def __init__(self):
        self.value, self.writes = 0, []

    def write(self, token, value):
        self.value = value
        self.writes.append((token, value))
        return "accepted"

    def read(self, token):
        return self.value


class Node:
    def __init__(self, name, proxy, lease, storage, log):
        self.name, self.proxy, self.lease, self.storage, self.log = name, proxy, lease, storage, log
        self.token, self.cache = None, None  # cache: leaders answer reads locally while they hold the lease

    def step(self, now):  # once per tick: renew my lease, or try to take a free one
        try:
            if self.token is None:
                (ok, token), _ = self.proxy.call(self.name, "lease", self.lease.acquire, self.name, now, TTL)
                if ok:
                    self.token = token
                    self.cache, _ = self.proxy.call(self.name, "storage", self.storage.read, token)
                    self.log(f"t={now} {self.name} acquired the lease, token {token}, loaded value {self.cache}")
            else:
                (ok, _) = self.proxy.call(self.name, "lease", self.lease.renew, self.name, self.token, now, TTL)
                if not ok:
                    self.log(f"t={now} {self.name} renew refused -> steps down")
                    self.token = None
        except Timeout as e:
            if self.token is not None:  # no answer is not a "no": n1 keeps believing it leads
                self.log(f"t={now} {self.name} renew timed out ({e}) -> still thinks it leads")

    def handle(self, now, process, f, value):
        op = {"process": process, "node": self.name, "f": f, "value": value, "start": now, "end": now + 0.5, "ok": False}
        if self.token is None:
            op["error"] = "not leader"
        elif f == "read":
            op.update(value=self.cache, ok=True)  # local read: fast, and only correct if I really still lead
        else:
            try:
                result, latency = self.proxy.call(self.name, "storage", self.storage.write, self.token, value)
                op["end"] += latency
                if result == "accepted":
                    self.cache, op["ok"] = value, True
            except Timeout as e:
                op["error"] = str(e)
        return op


def run(ops, faults, seed=13, ticks=11, storage=None):
    """ops: {tick: (process, node, f, value)}; faults: {tick: callable(proxy)}. Returns events, history, leaders."""
    proxy, lease, storage, events, history, leaders = Proxy(seed), LeaseStore(), storage or Storage(), [], [], []
    nodes = {n: Node(n, proxy, lease, storage, events.append) for n in ("n1", "n2", "n3")}
    for t in range(ticks):
        if t in faults:
            events.append(f"t={t} fault: {faults[t](proxy)}")
        for node in nodes.values():
            node.step(t)
        leaders.append(sorted(n.name for n in nodes.values() if n.token is not None))
        if t in ops:
            process, node, f, value = ops[t]
            history.append(nodes[node].handle(t, process, f, value))
    return events, history, leaders


OPS = {1: ("c1", "n1", "write", 1), 6: ("c2", "n2", "write", 2), 7: ("c1", "n1", "write", 3), 8: ("c2", "n2", "read", None)}
FAULTS = {2: lambda p: (p.partition({"n1"}, {"lease"}), p.add("n1", "storage", latency=0.3), "partition n1 | lease store; latency 0.3 n1->storage")[2],
          9: lambda p: (p.heal(), "heal")[1]}

if __name__ == "__main__":
    events, history, leaders = run(OPS, {})
    print("happy path (no faults): leaders per tick", " ".join("+".join(l) or "-" for l in leaders))
    print("  linearizable:", check_register(history)[0])
    events, history, leaders = run(OPS, FAULTS)
    print("\n".join(events))
    print("leaders per tick:", " ".join(f"{t}:{'+'.join(l) or '-'}" for t, l in enumerate(leaders)))
    print("history (JSON lines):", *jsonl(history), sep="\n  ")
    print("linearizable:", check_register(history)[0])
    for read, write in stale_reads(history):
        print(f"  stale read: {describe(read)}, but {describe(write)} had already finished")
