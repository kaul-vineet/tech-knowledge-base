"""Lab 19 - gateway: accept or reject radio frames before they enter the system (BEFORE).

The gateway is the trust boundary: everything behind it (broker, store, alarms, the local model)
believes what it lets through. This version checks what L300 checked - the frame parses and its
CRC-16 matches - so it detects NOISE. It cannot detect an ATTACKER: anyone in radio range can
compute a CRC, and a recorded frame replayed later is still a perfectly valid frame.
"""
import json

import frame_auth


class Verifier:
    def __init__(self, keys=None, mode="crc"):
        self.keys, self.mode = keys or {}, mode
        self.stats = {"accepted": 0, "rejected": 0}
        self.log = []                                   # JSON lines: why a frame was rejected

    def reject(self, reason, text):
        self.stats["rejected"] += 1
        self.log.append(json.dumps({"reject": reason, "frame": text[:40]}))
        return None

    def check(self, text):
        """Return (dev, ctr, payload) for an accepted frame, else None."""
        try:
            dev, ctr, payload, tag = text.split(":")
            ctr = int(ctr)
        except ValueError:
            return self.reject("format", text)
        if int(tag, 16) != frame_auth.crc16(frame_auth.body(dev, ctr, payload).encode()):
            return self.reject("crc", text)
        self.stats["accepted"] += 1                     # parse + CRC ok -> trusted
        return dev, ctr, payload
