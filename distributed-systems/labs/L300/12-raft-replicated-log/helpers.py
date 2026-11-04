"""Plumbing for lab 12 (not the lesson's concept): a deterministic simulated network, a safety checker that
remembers every committed entry, the cluster driver (ticks, crash, restart), log formatting and the narrated demo. Nothing here sleeps or uses sockets."""


def fmt(log):
    """[(1, 'x=1'), (2, 'x=9')] -> '1:x=1 2:x=9' (term:command per entry)."""
    return " ".join(f"{t}:{c}" for t, c in log) or "-"


class Network:
    """Messages arrive one tick after they are sent, in send order. Crashed nodes neither send nor receive;
    cut links drop messages silently (a partition looks exactly like a slow or dead peer)."""
    def __init__(self):
        self.now, self.queue, self.cut, self.down, self.events = 0, [], set(), set(), []

    def send(self, src, dst, msg):
        if src not in self.down and (src, dst) not in self.cut:
            self.queue.append((self.now + 1, src, dst, msg))

    def due(self):
        ready = [q for q in self.queue if q[0] <= self.now]
        self.queue = [q for q in self.queue if q[0] > self.now]
        return [(s, d, m) for _, s, d, m in ready if d not in self.down and (s, d) not in self.cut]

    def partition(self, *groups):
        for a in groups:
            for b in groups:
                if a is not b:
                    self.cut |= {(x, y) for x in a for y in b}

    def heal(self):
        self.cut.clear()

    def log(self, text):
        self.events.append(f"t={self.now} {text}")


class SafetyChecker:
    """State Machine Safety (Raft paper, Figure 3): once an index is committed on any node, no node may ever
    commit a different entry at that index. Remembers the first committed entry per index."""
    def __init__(self):
        self.committed, self.violations = {}, []

    def observe(self, now, nodes):
        for n in nodes:
            for i in range(1, n.commit + 1):
                now_there = n.log[i - 1] if i <= len(n.log) else None
                first = self.committed.setdefault(i, now_there)
                if now_there != first:
                    msg = f"LOST committed entry {i} ({fmt([first])}): {n.name} now has {fmt([now_there]) if now_there else 'nothing'} there"
                    if msg not in [v.split(" ", 1)[1] for v in self.violations]:
                        self.violations.append(f"t={now} {msg}")


class Cluster:
    """Drives the nodes: one tick = deliver due messages, then let every live node act (fixed order)."""
    def __init__(self, node_class, seed=7, names=("n1", "n2", "n3")):
        self.net, self.checker = Network(), SafetyChecker()
        self.nodes = {n: node_class(n, [p for p in names if p != n], self.net, seed) for n in names}

    def run(self, ticks):
        for _ in range(ticks):
            self.net.now += 1
            for src, dst, msg in self.net.due():
                self.nodes[dst].receive(src, msg)
            for name, node in self.nodes.items():
                if name not in self.net.down:
                    node.tick()
            self.checker.observe(self.net.now, self.nodes.values())

    def leader(self):
        live = [n for n in self.nodes.values() if n.role == "leader" and n.name not in self.net.down]
        return max(live, key=lambda n: n.term) if live else None

    def run_until_leader(self, limit=80):
        for _ in range(limit):
            if self.leader():
                return self.leader()
            self.run(1)
        raise RuntimeError("no leader elected")

    def crash(self, name):
        self.net.down.add(name)

    def restart(self, name):  # term, vote and log survive (persistent state); role and commit index do not
        self.net.down.discard(name)
        n = self.nodes[name]
        n.role, n.commit = "follower", 0
        n.reset_timer()

    def show(self):
        for n in self.nodes.values():
            state = "DOWN" if n.name in self.net.down else n.role
            print(f"   {n.name} term {n.term} {state:9} log [{fmt(n.log)}] commit {n.commit}")


def demo(node_class, scenario):
    """The narrated demo of raft.py / solution_raft.py: happy path, leader crash and re-election, restart and
    catch-up, then the failure-lab scenario with the safety checker's verdict."""
    c = Cluster(node_class, seed=7)
    leader = c.run_until_leader()
    for cmd in ("x=1", "x=2", "x=3"):
        leader.propose(cmd)
    c.run(6)
    print("\n".join(c.net.events))
    print("1) happy path: 3 entries replicated and committed")
    c.show()
    c.crash(leader.name)
    crashed_at, c.net.events = c.net.now, []
    new = c.run_until_leader()
    print("\n".join(c.net.events))
    print(f"2) {leader.name} crashed at t={crashed_at}; {new.name} leads term {new.term} after {c.net.now - crashed_at} ticks")
    new.propose("x=4")
    c.run(6)
    c.restart(leader.name)
    c.run(6)
    print(f"3) x=4 committed without {leader.name}; {leader.name} restarted and caught up:")
    c.show()
    print("safety violations:", len(c.checker.violations))
    s = scenario()
    print("\n".join(s.net.events))
    print("4) failure lab: stale follower elected, then writes x=9")
    s.show()
    print(f"safety violations: {len(s.checker.violations)}", *s.checker.violations, sep="\n   ")
