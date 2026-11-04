"""Lab 15 - serial gateway on the PC (BEFORE hardening).

Reads the micro:bit's serial lines, turns each into a JSON message and forwards
it MQTT-style: one JSON line {"topic", "qos", "payload"} per reading. Works on a
clean transcript. On a real serial link (boot messages, a cable pulled
mid-line, a flipped bit) it either CRASHES on the first bad line or, worse,
forwards a wrong value: it never checks the length or the CRC.

Run:  python gateway.py --file serial.txt     (Windows: py gateway.py --file serial.txt)
"""
import argparse
import json
import sys

TOPIC = "microbit/{device}/telemetry"


class JsonLinesPublisher:
    """MQTT-style output without a broker: one JSON object per line."""

    def __init__(self, out=None):
        self.out = out or sys.stdout
        self.sent = []

    def publish(self, topic, payload, qos=1):
        msg = {"topic": topic, "qos": qos, "payload": payload}
        self.sent.append(msg)
        self.out.write(json.dumps(msg, sort_keys=True) + "\n")


def parse_line(line):
    body = line.strip()                     # "$LLL<payload>*CCCC"
    payload = body[4:].split("*")[0]        # trusts the format: no checks at all
    seq, temp, light = payload.split(",")
    return {"seq": int(seq), "temp": int(temp), "light": int(light)}


def run(lines, publisher, device="mb1"):
    for line in lines:
        if not line.strip():
            continue
        publisher.publish(TOPIC.format(device=device), parse_line(line))
    return publisher


def main(argv=None):
    ap = argparse.ArgumentParser(description="naive serial -> JSON-lines gateway")
    ap.add_argument("--file", required=True, help="serial transcript (text)")
    args = ap.parse_args(argv)
    with open(args.file, encoding="utf-8", errors="replace") as f:
        run(f, JsonLinesPublisher())


if __name__ == "__main__":
    main()
