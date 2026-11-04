"""Capstone plumbing (CPython only): the classroom scenario and the gateway, built from earlier labs.

Reused: lab 17 edge_sim (stub boards + relay + lab 15 framer), lab 19 Verifier (SipHash + window),
_edge MiniBroker / Store / exports, lab 20 twin, lab 18 fleet sim, lab 21 alarms + assistant.
Scenario (seed 22, 600 s): six boards; per-link loss 5-15 %; n5's link degrades from 300 s
(0.15 -> 0.50); sun on n4 from 560 s (31 C); students shake n1-n3 every 15 s between 120 and 480 s;
Eve (another micro:bit) replays 10 recorded frames and forges 10 "45 C" frames from 200 s.
"""
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
L400 = HERE.parent
sys.path.insert(0, str(L400 / "_edge"))
from simnet import reuse  # noqa: E402
from minibroker import MiniBroker  # noqa: E402
from store import Store  # noqa: E402
import radio as radio_stub  # noqa: E402

edge = reuse("L400/17-edge-to-cloud/edge_sim.py", "l400_edge_sim")
fa = reuse("L400/19-radio-auth/frame_auth.py", "frame_auth")
verifier = reuse("L400/19-radio-auth/solution.py", "l400_verifier")
twin_model = reuse("L400/20-digital-twin/twin_model.py", "twin_model")
sys.path[:] = [p for p in sys.path if "20-digital-twin" not in p and "19-radio-auth" not in p]

SEED, DURATION_S = 22, 600
DEVICES = ["n%d" % i for i in range(1, 7)]
LOSS = {"n1": 0.05, "n2": 0.05, "n3": 0.10, "n4": 0.10, "n5": 0.15, "n6": 0.15}
OFFSETS = [0.4, -0.3, 0.2, 0.8, -0.5, 0.1]
HOT_FROM_MS, DRIFT_FROM_MS = 560000, 300000


def keys(seed=SEED):
    rng = random.Random(seed)       # demo keys; real ones: secrets.token_bytes(16), provisioned over USB
    return dict((d, bytes(rng.getrandbits(8) for _ in range(16))) for d in DEVICES)


def loss_fn(a, b, t):
    dev = a if a in LOSS else b
    p = LOSS.get(dev, 0.1)
    if dev == "n5" and t >= DRIFT_FROM_MS:
        p += 0.35 * min(1.0, (t - DRIFT_FROM_MS) / (DURATION_S * 1000 - DRIFT_FROM_MS))
    return p


def make_inputs(seed=SEED):
    rng = random.Random(seed)

    def inputs(i, t):
        temp = twin_model.room_temp(t) + OFFSETS[i] + rng.gauss(0, 0.3)
        if i == 3 and t >= HOT_FROM_MS:
            temp = 31.0                                        # sun on the window bench
        shake = i < 3 and 120000 <= t < 480000 and t % 15000 == 0
        return int(round(temp)), (60 + 20 * i + (t // 60000) * 5) % 256, shake
    return inputs


class Gateway:
    """The trust boundary: lab 15 frames in, lab 19 verification, MQTT QoS 1, idempotent store."""

    def __init__(self, key_table):
        self.verifier = verifier.Verifier(key_table)
        self.broker, self.store, self.rows = MiniBroker(), Store(), []
        self.broker.subscribe("classroom/+/telemetry", self._store)

    def _store(self, topic, row):
        if self.store.add(row):
            self.rows.append(row)

    def feed(self, payload, t_store):
        dev, seq, rest = payload.decode("ascii", "replace").split(",", 2)
        ok = self.verifier.check("%s:%s:%s" % (dev, seq, rest))
        if ok is None:
            return
        t, temp, light, motion = (int(x) for x in ok[2].split(","))
        self.broker.publish("classroom/%s/telemetry" % dev, dict(dev=dev, seq=ok[1], t_sensor=t, t_store=t_store,
                                                                  temp=temp, light=light, motion=motion), qos=1)


class Eve:
    """An attacker's micro:bit on the same group: records frames, replays some, forges others."""

    def __init__(self, seed=SEED):
        self.rng, self.ep, self.heard, self.encode = random.Random(seed + 1), None, [], None
        self.sent = {"replayed": 0, "forged": 0}

    def tick(self, air, t):
        if self.ep is None:
            self.ep = radio_stub.Endpoint(air, "eve", lambda: t)
            self.ep.config(group=17, length=96, queue=50)
        while True:
            msg = self.ep.receive()
            if msg is None:
                break
            if msg.startswith("D:"):
                self.heard.append(msg)
        if t >= 200000 and t % 20000 == 0 and self.sent["forged"] < 10 and self.heard:
            self.ep.send(self.heard[self.rng.randrange(len(self.heard))])
            self.sent["replayed"] += 1
            last = max(int(m.split(":")[2]) for m in self.heard if m.startswith("D:n1:"))
            payload = "%d,45,100,0:%016x" % (t, self.rng.getrandbits(64))      # no key: a guessed tag
            self.ep.send(self.encode("D", "n1", last + 1, payload))             # valid CRC, fresh seq
            self.sent["forged"] += 1


def run_network(source, seed=SEED, duration_s=DURATION_S):
    k, eve = keys(seed), Eve(seed)
    gw = Gateway(k)

    def setup(boards, states):
        eve.encode = boards[0].lab.encode
        for b, st in zip(boards, states):
            st["key"] = k.get(b.name)                          # provisioning: each board knows only its key
    res, _ = edge.run("solution.py", seed=seed, readings=duration_s, drain_ms=5000, loss_fn=loss_fn,
                      inputs=make_inputs(seed), sources=dict((n, source) for n in DEVICES + ["relay"]),
                      setup=setup, on_tick=eve.tick, on_payload=gw.feed)
    return res, gw, eve
