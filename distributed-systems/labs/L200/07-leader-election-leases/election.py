"""L200 lesson 7 (python election.py): three nodes compete for a lease in a shared KV store (TTL +
compare-and-swap). The leader renews every tick; when it pauses, the lease expires, another node takes
over with a HIGHER fencing token, and storage rejects the old leader's late write. Simulated clock."""
from helpers import SimClock, call, serve
from kv_store import KVStore

KEY, TTL = "leader", 3.0  # lease TTL 3 s; nodes act once per 1 s tick, so the leader renews at TTL/3


class Node:
    def __init__(self, name, url):
        self.name, self.url, self.rev, self.token, self.paused = name, url, 0, None, False

    def pause(self):  # e.g. a long GC pause: the node stops acting but still BELIEVES it leads
        self.paused = True

    def resume(self):
        self.paused = False

    def step(self, t, storage, log):
        if self.paused:
            return
        if self.token is not None:  # I think I am the leader: do the work, then renew
            log(f"t={t} {self.name} writes with token {self.token}: {storage.write(self.token, f'{self.name}@t{t}')}")
            status, body, _ = call(self.url + "/cas", {"key": KEY, "expect": self.rev, "value": self.name, "ttl": TTL})
            if status == 200:
                self.rev = body["rev"]  # renewed: CAS on MY revision, TTL restarts
            else:
                log(f"t={t} {self.name} renew failed (rev {self.rev} != {body['rev']}) -> steps down")
                self.token = None
            return
        status, _, _ = call(self.url + "/get", {"key": KEY})
        if status == 404:  # lease free (never taken, or expired): try to create it, expect rev 0
            status, body, _ = call(self.url + "/cas", {"key": KEY, "expect": 0, "value": self.name, "ttl": TTL})
            if status == 200:  # only one CAS can win; the losers see 409
                self.rev, self.token = body["rev"], body["created"]  # fencing token = creation revision
                log(f"t={t} {self.name} acquired the lease, fencing token {self.token}")


class FencedStorage:
    """The protected resource: rejects a write whose token is lower than the highest it has seen."""
    def __init__(self, fencing=True):
        self.fencing, self.max_token, self.value = fencing, 0, None

    def write(self, token, value):
        if self.fencing and token < self.max_token:
            return f"REJECTED (token {token} < {self.max_token})"
        self.max_token, self.value = max(self.max_token, token), value
        return "accepted"


def simulate(ticks=9, events=None, fencing=True, quiet=False):
    """events: {tick: (node_name, method_name)}. Returns {'log', 'holders', 'storage'}."""
    clock, lines, holders = SimClock(), [], []
    KVStore.reset(clock)
    srv = serve(KVStore)
    url, storage = f"http://127.0.0.1:{srv.server_port}", FencedStorage(fencing)
    nodes = {n: Node(n, url) for n in ("n1", "n2", "n3")}
    log = lines.append if quiet else (lambda s: (lines.append(s), print(s)))
    for t in range(ticks):
        if t in (events or {}):
            name, action = events[t]
            getattr(nodes[name], action)()  # the lab's events: pause / resume (build task: resign)
            log(f"t={t} {name} {action}")
        for node in nodes.values():  # fixed order n1, n2, n3 -> deterministic
            node.step(t, storage, log)
        status, body, _ = call(url + "/get", {"key": KEY})
        holders.append((t, body.get("value"), body.get("created")) if status == 200 else (t, None, None))
        clock.advance(1.0)
    srv.shutdown()
    srv.server_close()
    return {"log": lines, "holders": holders, "storage": storage}


if __name__ == "__main__":
    out = simulate(events={3: ("n1", "pause"), 7: ("n1", "resume")})
    print("lease holder per tick:", " ".join(f"{t}:{h or '-'}" for t, h, _ in out["holders"]))
    print("storage value:", out["storage"].value, "| highest token seen:", out["storage"].max_token)
