"""Lab 15 - serial gateway on the PC (AFTER hardening = build task solution).

Bytes in (any chunk size) -> frames out. Never crashes on input:
  * framing: find "$", read the 3-digit length, wait for the whole frame
  * validate: "*" at the expected place, CRC-16 matches, then a line end
  * resync: on any error drop ONE byte and search for the next "$" (counts it)
  * payload check: 3 integers in range, else "bad_payload"
  * observability: every N frames (and at the end) a metrics JSON line on
    topic microbit/gateway/metrics

Run:  python solution.py --demo                 (stub device + seeded noisy link)
      python solution.py --file serial.txt      (a saved serial transcript)
      python solution.py --serial COM3          (real board: needs pyserial)
      add --mqtt 127.0.0.1:1883 to publish to a broker (needs paho-mqtt)
"""
import argparse
import json
import sys

from gateway import TOPIC, JsonLinesPublisher

METRICS_TOPIC = "microbit/gateway/metrics"
MAX_LEN = 64
KEYS = ("frames_ok", "bad_len", "bad_crc", "bad_payload", "resyncs", "skipped_bytes")


def crc16(data):
    crc = 0xFFFF
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else (crc << 1)
            crc &= 0xFFFF
    return crc


class Framer:
    def __init__(self):
        self.buf = bytearray()
        self.m = dict((k, 0) for k in KEYS)

    def _skip(self, n):
        seg = self.buf[:n]                   # line ends between frames are not "skipped"
        self.m["skipped_bytes"] += n - seg.count(b"\r") - seg.count(b"\n")
        del self.buf[:n]

    def _resync(self, reason):
        self.m[reason] += 1
        self.m["resyncs"] += 1
        del self.buf[0]                      # drop one byte, look for the next "$"

    def feed(self, chunk):
        """Add bytes; yield each valid payload (bytes) as soon as it is complete."""
        self.buf += chunk
        while True:
            start = self.buf.find(b"$")
            if start < 0:
                self._skip(len(self.buf))
                return
            self._skip(start)
            if len(self.buf) < 4:
                return                       # wait for the length field
            head = bytes(self.buf[1:4])
            if not head.isdigit() or int(head) > MAX_LEN:
                self._resync("bad_len")
                continue
            n = int(head)
            end = 4 + n + 5                  # "$LLL" + payload + "*CCCC"
            if len(self.buf) < end + 1:
                return                       # partial frame: wait for more bytes
            payload, star, check = self.buf[4:4 + n], self.buf[4 + n:5 + n], bytes(self.buf[5 + n:end])
            if star != b"*" or self.buf[end:end + 1] not in (b"\r", b"\n"):
                self._resync("bad_len")      # bytes lost or added inside the frame
                continue
            try:
                ok = int(check, 16) == crc16(payload)
            except ValueError:
                ok = False
            if not ok:
                self._resync("bad_crc")
                continue
            del self.buf[:end]
            self.m["frames_ok"] += 1
            yield bytes(payload)             # generator: metrics stay exact per frame


def parse_payload(payload):
    try:
        seq, temp, light = (int(x) for x in payload.decode("ascii").split(","))
    except (ValueError, UnicodeDecodeError):
        return None
    if seq < 1 or not -40 <= temp <= 105 or not 0 <= light <= 255:
        return None
    return {"seq": seq, "temp": temp, "light": light}


def run(chunks, publisher, device="mb1", metrics_every=50):
    framer = Framer()
    for chunk in chunks:
        for payload in framer.feed(chunk):
            msg = parse_payload(payload)
            if msg is None:
                framer.m["bad_payload"] += 1
                continue
            publisher.publish(TOPIC.format(device=device), msg)
            if framer.m["frames_ok"] % metrics_every == 0:
                publisher.publish(METRICS_TOPIC, dict(framer.m))
    publisher.publish(METRICS_TOPIC, dict(framer.m))
    return framer.m


def chunks_from(args):
    if args.demo:
        import serial_link
        return serial_link.noisy(serial_link.device_bytes(), **serial_link.FAULTS)[0]
    if args.file:
        with open(args.file, "rb") as f:
            return [f.read()]
    import serial                           # pyserial, only for a real board
    port = serial.Serial(args.serial, 115200, timeout=1)
    return iter(lambda: port.read(64), b"")


def main(argv=None):
    ap = argparse.ArgumentParser(description="framed serial -> MQTT-style JSON gateway")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--demo", action="store_true")
    src.add_argument("--file")
    src.add_argument("--serial")
    ap.add_argument("--mqtt", help="host:port of an MQTT broker (paho-mqtt)")
    args = ap.parse_args(argv)
    if args.mqtt:
        from mqtt_bridge import MqttPublisher
        host, _, port = args.mqtt.partition(":")
        pub = MqttPublisher(host, int(port or 1883))
    else:
        pub = JsonLinesPublisher()
    try:
        run(chunks_from(args), pub)
    finally:
        if args.mqtt:
            pub.close()


if __name__ == "__main__":
    main()
