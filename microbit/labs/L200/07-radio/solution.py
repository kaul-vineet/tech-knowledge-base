# Lab 07 - SOLUTION of the build task: acknowledge every message.
# Lab 07 - radio between two boards. Flash the SAME main.py on both.
# A sends "btn:<seq>:A", B sends "tmp:<seq>:<temperature>"; the other board
# decodes, drops duplicates and garbage, and prints what it received.
from microbit import *
import radio

GROUP = 7                  # group: both boards must use the same number (0-255)
KINDS = ("btn", "tmp", "ack")  # message format "<kind>:<seq>:<value>", text only
radio.config(group=GROUP)  # radio is already on after `import radio` (V2)


def encode(kind, seq, value):
    # one line of text; ":" separates fields, so values must not contain ":"
    return "{}:{}:{}".format(kind, seq, value)


def decode(text):
    # validate everything that came over the air: format, kind, sequence number
    parts = text.split(":")
    if len(parts) != 3 or parts[0] not in KINDS:
        return None
    try:
        seq = int(parts[1])
    except ValueError:
        return None
    return parts[0], seq, parts[2]


def new_state():
    return {"seq": 0, "last_rx": 0, "bad": 0}


def send(state, kind, value):
    state["seq"] += 1
    radio.send(encode(kind, state["seq"], value))   # send(str) adds b'\x01\x00\x01'
    print("tx", kind, state["seq"], value)


def receive(state):
    try:
        text = radio.receive()          # None when the queue is empty
    except ValueError:                  # bytes that are not a radio.send() string
        text = "?"
    if text is None:
        return None
    msg = decode(text)
    if msg is None:
        state["bad"] += 1
        print("rx bad", state["bad"])
        return None
    kind, seq, value = msg
    if kind == "ack":                   # build task: the other board confirms OUR seq
        print("acked", seq)
        return msg
    radio.send(encode("ack", seq, ""))  # build task: reply even to duplicates
    if seq <= state["last_rx"]:         # duplicate or old sequence number: ignore
        return None
    state["last_rx"] = seq
    print("rx", kind, seq, value)
    display.show(value if kind == "btn" else Image.YES, wait=False)
    return msg


def step(state):
    if button_a.was_pressed():
        send(state, "btn", "A")
    if button_b.was_pressed():
        send(state, "tmp", temperature())
    return receive(state)


def main():
    print("radio group", GROUP)
    state = new_state()
    while True:
        step(state)
        sleep(50)                       # poll often: the receive queue holds 3 messages


if __name__ == "__main__":
    main()
