"""L100 (python lamport.py): three nodes exchange HTTP messages carrying Lamport timestamps. Wall
clocks are skewed on purpose: sorting by wall time breaks cause->effect, Lamport order doesn't."""
import json, threading, urllib.request

from helpers import OPENER, QuietHandler, serve, show, violations  # plumbing + log printing

TRUE_TIME = [0.0]                                # simulated "real" time, +10 ms per event
SKEW_S = {"A": 0.000, "B": -0.080, "C": +0.040}  # clock skew: B runs 80 ms slow, C 40 ms fast
EVENTS = []                                      # (lamport, node, wall, text, msg_id)


class Node:
    def __init__(self, name):
        self.name, self.clock, self.lock, node = name, 0, threading.Lock(), self

        class Handler(QuietHandler):
            def do_POST(self):
                node.on_receive(json.loads(self.read_body()))
                self.send_response(204); self.end_headers()

        self.srv = serve(Handler)

    def record(self, text, msg_id=None):
        TRUE_TIME[0] += 0.010
        wall = round(TRUE_TIME[0] + SKEW_S[self.name], 3)  # what this node's own wall clock says
        EVENTS.append((self.clock, self.name, wall, text, msg_id))

    def local(self, text):
        with self.lock:
            self.clock += 1  # rule 1, local event: tick
            self.record(text)

    def send(self, other, text, msg_id):
        with self.lock:
            self.clock += 1  # rule 2, send: tick, then attach the timestamp to the message
            ts = self.clock
            self.record(f"send '{text}' to {other.name}", msg_id)
        body = json.dumps({"from": self.name, "ts": ts, "text": text, "id": msg_id}).encode()
        OPENER.open(urllib.request.Request(f"http://127.0.0.1:{other.srv.server_port}/msg", body,
                                           {"Content-Type": "application/json"}), timeout=2).close()

    def on_receive(self, msg):
        with self.lock:
            self.clock = max(self.clock, msg["ts"]) + 1  # rule 3, receive: max(local, received) + 1
            self.record(f"recv '{msg['text']}' from {msg['from']}", msg["id"])


def scenario(node_cls=Node):
    a, b, c = node_cls("A"), node_cls("B"), node_cls("C")
    a.local("user clicks Buy")
    a.send(b, "create order", "m1")
    b.local("reserve stock")
    b.send(c, "charge card", "m2")
    c.send(a, "payment ok", "m3")
    c.local("write audit log")
    a.local("show receipt")
    for n in (a, b, c):
        n.srv.shutdown(); n.srv.server_close()
    return EVENTS


if __name__ == "__main__":
    events = scenario()
    show("sorted by wall clock", sorted(events, key=lambda e: e[2]))
    # total order: (Lamport, node id) - consistent with causality; node id breaks ties
    show("sorted by (Lamport, node)", sorted(events, key=lambda e: (e[0], e[1])))
