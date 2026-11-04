# Lab 12 - a radio link for sensor readings (BEFORE hardening). Flash the SAME
# main.py on both boards. Press A: send the next reading. Every frame carries a
# sequence number and a CRC-16, so corrupted frames are rejected - but nothing
# notices a LOST frame: it works on a quiet bench and silently drops data in a
# noisy room. The build task adds acks, retransmit and duplicate suppression.
from microbit import *
import radio

GROUP = 12
radio.config(group=GROUP)       # default length=32 bytes, queue=3 frames


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
    body = "{}:{}:{}".format(kind, seq, payload)    # kind D = data, A = ack
    return "{}:{:04X}".format(body, crc16(body))    # checksum over the whole body


def decode(text):
    # returns (kind, seq, payload) or None; nothing from the air is trusted
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


def new_state():
    return {"seq": 0, "delivered": [],
            "stats": {"tx": 0, "rx": 0, "bad": 0, "delivered": 0}}


def jline(t, stats):
    # observability: one JSON line per report, keys in a fixed order
    keys = ("tx", "rx", "bad", "delivered")
    return '{"t":%d,' % t + ",".join('"%s":%d' % (k, stats[k]) for k in keys) + "}"


def send(state, payload):
    state["seq"] += 1
    radio.send(encode("D", state["seq"], payload))  # fire and forget
    state["stats"]["tx"] += 1


def deliver(state, seq, payload):
    state["delivered"].append(payload)
    state["stats"]["delivered"] += 1
    print("rx", seq, payload)


def receive(state):
    while True:                         # drain the queue: it holds only 3 frames
        try:
            text = radio.receive()
        except ValueError:              # not a radio.send() string
            text = "?"
        if text is None:
            return
        state["stats"]["rx"] += 1
        msg = decode(text)
        if msg is None:
            state["stats"]["bad"] += 1  # wrong CRC or format: drop it
        elif msg[0] == "D":
            deliver(state, msg[1], msg[2])


def step(state):
    if button_a.was_pressed():
        send(state, temperature())
    receive(state)


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
