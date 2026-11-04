"""tryIt experiments for lesson 6 (python try_it.py). Prints what actually happens."""
import lamport


def run(node_cls=lamport.Node):
    lamport.EVENTS.clear(); lamport.TRUE_TIME[0] = 0.0
    return list(lamport.scenario(node_cls))


# tryIt 1: BUG - forget max() on receive (just tick)
class NoMaxNode(lamport.Node):
    def on_receive(self, msg):
        with self.lock:
            self.clock += 1
            self.record(f"recv '{msg['text']}' from {msg['from']}", msg["id"])


events = run(NoMaxNode)
by_lamport = sorted(events, key=lambda e: (e[0], e[1]))
m1 = {e[3].split()[0]: e[0] for e in events if e[4] == "m1"}
print(f"tryIt 1: without max(): m1 send L={m1['send']}, recv L={m1['recv']}; "
      f"(Lamport, node) order has {lamport.violations(by_lamport)} violation(s)")

# tryIt 2: C's clock correct, B's clock only 5 ms or 15 ms slow (events are 10 ms apart)
lamport.SKEW_S["C"] = 0.0
for skew_ms in (5, 15):
    lamport.SKEW_S["B"] = -skew_ms / 1000
    events = run()
    print(f"tryIt 2: B {skew_ms:>2} ms slow -> wall-clock order "
          f"{lamport.violations(sorted(events, key=lambda e: e[2]))} violation(s), (Lamport, node) "
          f"order {lamport.violations(sorted(events, key=lambda e: (e[0], e[1])))}")
