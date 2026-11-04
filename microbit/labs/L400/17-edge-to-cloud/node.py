# Lab 17 - classroom sensor node and radio relay (BEFORE the design review).
# Flash the SAME file on every board. ROLE = "relay" on the one board on the PC's USB
# cable, "sensor" on the others (set DEV to a unique name; on a board use machine.unique_id()).
# Sensor: every SAMPLE_MS take temp/light/motion, send it with lab 12's stop-and-wait ARQ.
# Relay: ack every data frame, drop duplicates per device, print a lab 15 serial frame.
# Works for ONE sensor. In a classroom of six it does not: see the README.
from microbit import *
import radio

GROUP = 17
SAMPLE_MS = 1000
TIMEOUT_MS = 100                 # first retransmit deadline; doubles, capped
MAX_TIMEOUT_MS = 800
MAX_TRIES = 6
QUEUE = 3                        # radio default: 3 frames, the rest are dropped
radio.config(group=GROUP, queue=QUEUE)
KEYS = ("tx", "retx", "acked", "gave_up", "rx", "bad", "dup", "fwd")


def crc16(text):
    # CRC-16/CCITT-FALSE, as in labs 12 and 15
    crc = 0xFFFF
    for ch in text:
        crc ^= ord(ch) << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else (crc << 1)
            crc &= 0xFFFF
    return crc


def encode(kind, dev, seq, payload=""):
    body = "{}:{}:{}:{}".format(kind, dev, seq, payload)    # D = data, A = ack
    return "{}:{:04X}".format(body, crc16(body))


def decode(text):
    body, sep, check = text.rpartition(":")
    if not sep or len(check) != 4:
        return None
    try:
        if int(check, 16) != crc16(body):
            return None
        kind, dev, seq, payload = body.split(":", 3)
        return kind, dev, int(seq), payload
    except ValueError:
        return None


def new_state(role, dev, start_ms=0):
    return {"role": role, "dev": dev, "seq": 0, "queue": [], "inflight": None,
            "next_sample": start_ms, "last": {}, "stats": dict((k, 0) for k in KEYS)}


def sample(now):
    motion = 1 if accelerometer.was_gesture("shake") else 0
    return "{},{},{},{}".format(now, temperature(), display.read_light_level(), motion)


def first_timeout(state):
    return TIMEOUT_MS            # identical on every board: retries stay in lock-step


def pump(state, now):
    st, fl = state["stats"], state["inflight"]
    if fl is None and state["queue"]:
        state["seq"] += 1
        fl = state["inflight"] = {"seq": state["seq"], "tries": 0, "deadline": now,
                                  "timeout": first_timeout(state),
                                  "frame": encode("D", state["dev"], state["seq"], state["queue"].pop(0))}
    if fl is None or now < fl["deadline"]:
        return
    if fl["tries"] >= MAX_TRIES:
        st["gave_up"] += 1
        state["inflight"] = None
        return
    if fl["tries"]:
        st["retx"] += 1
        fl["timeout"] = min(fl["timeout"] * 2, MAX_TIMEOUT_MS)
    radio.send(fl["frame"])
    st["tx"] += 1
    fl["tries"] += 1
    fl["deadline"] = now + fl["timeout"]


def forward(state, dev, seq, payload):
    line = "{},{},{}".format(dev, seq, payload)                 # serial frame from lab 15
    print("${:03d}{}*{:04X}".format(len(line), line, crc16(line)))
    state["stats"]["fwd"] += 1


def on_frame(state, msg):
    st, (kind, dev, seq, payload) = state["stats"], msg
    if state["role"] == "relay" and kind == "D":
        radio.send(encode("A", dev, seq))                       # ack every copy
        if seq <= state["last"].get(dev, 0):
            st["dup"] += 1
            return
        state["last"][dev] = seq
        forward(state, dev, seq, payload)
    elif kind == "A" and dev == state["dev"]:
        fl = state["inflight"]
        if fl and seq == fl["seq"]:
            st["acked"] += 1
            state["inflight"] = None


def receive(state):
    while True:
        try:
            text = radio.receive()
        except ValueError:
            text = "?"
        if text is None:
            return
        state["stats"]["rx"] += 1
        msg = decode(text)
        if msg is None:
            state["stats"]["bad"] += 1
        else:
            on_frame(state, msg)


def step(state, now):
    if state["role"] == "sensor" and now >= state["next_sample"]:
        state["queue"].append(sample(now))
        state["next_sample"] += SAMPLE_MS
    receive(state)
    if state["role"] == "sensor":
        pump(state, now)


def main(role="sensor", dev="n1"):
    state = new_state(role, dev)
    while True:
        step(state, running_time())
        sleep(10)


if __name__ == "__main__":
    main()
