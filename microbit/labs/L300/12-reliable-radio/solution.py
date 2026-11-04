# Lab 12 - reliable radio link (AFTER hardening = build task solution).
# Same frames as main.py (sequence number + CRC-16), plus:
#   ack     the receiver answers every data frame with "A:<seq>"
#   ARQ     stop-and-wait: one frame in flight; no ack before the deadline -> resend,
#           doubling the timeout (backoff) up to MAX_TRIES, then give up and report it
#   dedupe  the receiver delivers each sequence number once, in order; old ones
#           (duplicates, late retransmits) are re-acked but not delivered again
from microbit import *
import radio

GROUP = 12
TIMEOUT_MS = 100                # first retransmit deadline; doubles each retry
MAX_TIMEOUT_MS = 800
MAX_TRIES = 8
radio.config(group=GROUP)


def crc16(text):
    # CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF): catches flipped bits
    crc = 0xFFFF
    for ch in text:
        crc ^= ord(ch) << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else (crc << 1)
            crc &= 0xFFFF
    return crc


def encode(kind, seq, payload):
    body = "{}:{}:{}".format(kind, seq, payload)
    return "{}:{:04X}".format(body, crc16(body))


def decode(text):
    body, sep, check = text.rpartition(":")
    if not sep or len(check) != 4:
        return None
    try:
        if int(check, 16) != crc16(body):
            return None
        kind, seq, payload = body.split(":", 2)
        return kind, int(seq), payload
    except ValueError:
        return None


KEYS = ("tx", "retx", "acked", "gave_up", "rx", "bad", "dup", "gap", "delivered")


def new_state():
    return {"seq": 0, "queue": [], "inflight": None, "expected": 1, "delivered": [],
            "stats": dict((k, 0) for k in KEYS)}


def jline(t, stats):
    return '{"t":%d,' % t + ",".join('"%s":%d' % (k, stats[k]) for k in KEYS) + "}"


def send(state, payload):
    state["queue"].append(payload)      # ARQ owns the radio: queue, then pump()


def pump(state, now):
    st, fl = state["stats"], state["inflight"]
    if fl is None and state["queue"]:
        state["seq"] += 1
        frame = encode("D", state["seq"], state["queue"].pop(0))
        state["inflight"] = fl = {"seq": state["seq"], "frame": frame, "tries": 0,
                                  "timeout": TIMEOUT_MS, "deadline": now}
    if fl is None or now < fl["deadline"]:
        return
    if fl["tries"] >= MAX_TRIES:        # bounded: report and move on, never hang
        st["gave_up"] += 1
        print(jline(now, st))
        state["inflight"] = None
        return
    if fl["tries"]:
        st["retx"] += 1
        fl["timeout"] = min(fl["timeout"] * 2, MAX_TIMEOUT_MS)   # backoff
    radio.send(fl["frame"])
    st["tx"] += 1
    fl["tries"] += 1
    fl["deadline"] = now + fl["timeout"]


def on_data(state, seq, payload):
    st = state["stats"]
    radio.send(encode("A", seq, ""))    # ack every copy: the last ack may be lost
    if seq < state["expected"]:
        st["dup"] += 1                  # duplicate suppression: seen it already
        return
    st["gap"] += seq - state["expected"]   # sender gave up on these: report the hole
    state["expected"] = seq + 1
    state["delivered"].append(payload)
    st["delivered"] += 1
    print("rx", seq, payload)


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
        elif msg[0] == "D":
            on_data(state, msg[1], msg[2])
        elif msg[0] == "A" and state["inflight"] and msg[1] == state["inflight"]["seq"]:
            state["stats"]["acked"] += 1
            state["inflight"] = None    # acks for other numbers are stale: ignore


def step(state):
    if button_a.was_pressed():
        send(state, temperature())
    receive(state)
    pump(state, running_time())


def main():
    print("link group", GROUP)
    state = new_state()
    while True:
        step(state)
        if button_b.was_pressed():
            print(jline(running_time(), state["stats"]))
        sleep(10)


if __name__ == "__main__":
    main()
