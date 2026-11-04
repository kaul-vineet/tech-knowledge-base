"""Lab 19 - gateway verifier (AFTER = build task solution).

Order of checks for every frame (cheap and safe first, state changes last):
  1. format  dev:ctr:payload:tag, ctr an integer, dev in the key table (unknown device -> reject)
  2. MAC     SipHash-2-4 with THAT device's 128-bit key; compare with hmac.compare_digest
  3. replay  per-device sliding window (64 counters, like IPsec ESP's anti-replay window):
             newer than the highest seen -> accept and slide; inside the window and not yet seen
             -> accept (radio reordering); seen, or older than the window -> reject
Only a frame that passed the MAC may move the window (a forged frame must not shift it).
"""
import hmac
import json

import frame_auth

WINDOW = 64


class Verifier:
    def __init__(self, keys, mode="siphash"):
        self.keys, self.mode = keys, mode
        self.high, self.seen = {}, {}                   # per device: highest ctr, bitmap of the window
        self.stats = {"accepted": 0, "rejected": 0}
        self.log = []

    def reject(self, reason, text):
        self.stats["rejected"] += 1
        self.log.append(json.dumps({"reject": reason, "frame": text[:40]}))
        return None

    def mac_ok(self, key, dev, ctr, payload, tag):
        expect = frame_auth.seal(dev, ctr, payload, key, self.mode).rpartition(":")[2]
        return hmac.compare_digest(expect.encode(), tag.encode())   # constant-time compare

    def fresh(self, dev, ctr):
        high, bits = self.high.get(dev, 0), self.seen.get(dev, 0)
        if ctr > high:
            shift = ctr - high
            self.seen[dev] = ((bits << shift) | 1) & ((1 << WINDOW) - 1)
            self.high[dev] = ctr
            return True
        age = high - ctr
        if age >= WINDOW or bits >> age & 1:
            return False
        self.seen[dev] = bits | (1 << age)
        return True

    def check(self, text):
        try:
            dev, ctr, payload, tag = text.split(":")
            ctr = int(ctr)
        except ValueError:
            return self.reject("format", text)
        key = self.keys.get(dev)
        if key is None:
            return self.reject("unknown_device", text)
        if not self.mac_ok(key, dev, ctr, payload, tag):
            return self.reject("mac", text)
        if not self.fresh(dev, ctr):
            return self.reject("replay", text)
        self.stats["accepted"] += 1
        return dev, ctr, payload
