"""Run the whole edge-to-cloud path on stub boards (CPython only, simulated time).

sensors (stub boards, node.py or solution.py) --radio (LinkAir, seeded loss)--> relay board
--USB serial (bytes, lab 15 frames)--> gateway (lab 15 Framer, reused) --> MiniBroker (MQTT-style,
QoS 1) --> SQLite store --> dashboard summary.
Time is the stub clock in 10 ms ticks; serial time = bytes x 10 bits / 115200 baud. There is no
radio airtime, collision or range model: latency here is protocol latency (retries, queues).
"""
import contextlib
import io
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "_edge"))
from simnet import LinkAir, percentile, reuse, serial_ms  # noqa: E402
from minibroker import MiniBroker  # noqa: E402
from store import Store  # noqa: E402
from labtest import load_boards  # noqa: E402  (sim_stub is on sys.path via simnet)

l15 = reuse("L300/15-serial-gateway/solution.py", "l300_serial_gateway")   # Framer + crc16, reused
LOSS = {"n1": 0.05, "n2": 0.05, "n3": 0.10, "n4": 0.10, "n5": 0.15, "n6": 0.15}   # per sensor link


def scenario(i, t):
    """Classroom inputs per sensor: temperature, light, and a shake every 7 s on n1."""
    return 20 + i % 3, (100 + 10 * i) % 256, (i == 0 and t % 7000 == 0)


def parse(payload):
    dev, seq, t, temp, light, motion = payload.decode("ascii").split(",")
    return dict(dev=dev, seq=int(seq), t_sensor=int(t), temp=int(temp), light=int(light), motion=int(motion))


def run(filename="node.py", n=6, loss=None, seed=17, readings=30, drain_ms=10000, sources=None,
        loss_fn=None, inputs=scenario, on_row=None, setup=None, on_tick=None, on_payload=None):
    """Hooks for the capstone: setup(boards, states) after loading (provision keys), on_tick(air, t)
    before each tick (an attacker's radio), on_payload(bytes, t_store) replaces parse + publish."""
    random.seed(seed)                                   # the boards' jitter (solution.py) is seeded too
    names = ["n%d" % (i + 1) for i in range(n)] + ["relay"]
    air = LinkAir(loss=LOSS if loss is None else loss, seed=seed, loss_fn=loss_fn)
    boards = load_boards(HERE, names=names, filename=filename, air=air, sources=sources)
    states = [b.lab.new_state("relay" if b.name == "relay" else "sensor", b.name) for b in boards]
    if setup:
        setup(boards, states)
    framer, broker, store, lat = l15.Framer(), MiniBroker(), Store(), []
    t_store = [0]

    def consume(topic, msg):
        row = dict(msg, t_store=t_store[0])
        if store.add(row):
            lat.append(row["t_store"] - row["t_sensor"])
            if on_row:
                on_row(row)
    broker.subscribe("classroom/+/telemetry", consume)
    out = io.StringIO()
    end = readings * boards[0].lab.SAMPLE_MS
    with contextlib.redirect_stdout(out):
        for t in range(0, end + drain_ms, 10):
            air.now = t
            if on_tick:
                on_tick(air, t)
            for i, (b, st) in enumerate(zip(boards, states)):
                if b.name != "relay":
                    temp, light, shake = inputs(i, t)
                    b.mb._inject_temperature(temp)
                    b.mb.display.inject_light_level(light)
                    if shake:
                        b.mb.accelerometer.inject_gesture("shake")
                    if t >= end:
                        st["next_sample"] = 10 ** 12          # stop sampling, let queues drain
                b.lab.step(st, t)
                b.mb.sleep(10)
            chunk = out.getvalue().encode("ascii")
            out.seek(0)
            out.truncate()
            t_store[0] = t + 10 + round(serial_ms(len(chunk)))   # end of this tick + UART time
            for payload in framer.feed(chunk):
                if on_payload:
                    on_payload(payload, t_store[0])
                    continue
                msg = parse(payload)
                broker.publish("classroom/%s/telemetry" % msg["dev"], msg, qos=1)
    sens = [s for s in states if s["role"] == "sensor"]
    sampled = sum(s["seq"] + len(s["queue"]) for s in sens)
    tot = lambda k: sum(s["stats"][k] for s in sens)      # noqa: E731
    relay = [b for b in boards if b.name == "relay"][0]
    res = {"file": filename, "sensors": n, "sampled": sampled, "stored": len(store.rows()),
           "delivery_pct": round(100.0 * len(store.rows()) / max(sampled, 1), 1),
           "p50_ms": percentile(lat, 50), "p95_ms": percentile(lat, 95), "max_ms": max(lat) if lat else None,
           "tx": tot("tx"), "retx": tot("retx"), "gave_up": tot("gave_up"),
           "relay_queue_drops": relay.radio.dropped,
           "sensor_queue_drops": sum(b.radio.dropped for b in boards if b.name != "relay"),
           "bad_serial": framer.m["bad_crc"] + framer.m["bad_len"]}
    return res, store


if __name__ == "__main__":
    for f in ("node.py", "solution.py"):
        print(json.dumps(run(f)[0]))
