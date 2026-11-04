# Lab 19 - device side: authenticate radio frames (pure functions: no radio, no microbit import,
# so the same file runs in MicroPython and on the PC gateway).
# micro:bit MicroPython documents no hashlib/hmac module, so the MAC is written in Python here.
#   siphash24  SipHash-2-4 (Aumasson & Bernstein 2012): a keyed PRF the authors designed as a MAC for
#              short messages; 128-bit key, 64-bit tag. Checked against the reference test vectors.
#   toy_tag    CRC-16 over key + message. NOT CRYPTOGRAPHICALLY SECURE: CRC is linear, so one
#              observed frame reveals a 16-bit state that forges any frame (attacks.py shows it).
#              Only good against accidents (a neighbouring class on the same group), never attackers.
# Frame on the radio:  <dev>:<ctr>:<payload>:<tag hex>   (ctr = per-device counter, never reused)
MASK = 0xFFFFFFFFFFFFFFFF


def _rotl(x, b):
    return ((x << b) | (x >> (64 - b))) & MASK


def _round(v0, v1, v2, v3):
    v0 = (v0 + v1) & MASK
    v1 = _rotl(v1, 13) ^ v0
    v0 = _rotl(v0, 32)
    v2 = (v2 + v3) & MASK
    v3 = _rotl(v3, 16) ^ v2
    v0 = (v0 + v3) & MASK
    v3 = _rotl(v3, 21) ^ v0
    v2 = (v2 + v1) & MASK
    v1 = _rotl(v1, 17) ^ v2
    v2 = _rotl(v2, 32)
    return v0, v1, v2, v3


def _le64(b):
    x = 0
    for i in range(len(b) - 1, -1, -1):
        x = (x << 8) | b[i]
    return x


def siphash24(key, msg):
    k0, k1 = _le64(key[0:8]), _le64(key[8:16])
    v0, v1 = k0 ^ 0x736F6D6570736575, k1 ^ 0x646F72616E646F6D
    v2, v3 = k0 ^ 0x6C7967656E657261, k1 ^ 0x7465646279746573
    n = len(msg)
    tail = bytes(msg[n - n % 8:]) + bytes(7 - n % 8) + bytes([n & 0xFF])
    blocks = [msg[i:i + 8] for i in range(0, n - n % 8, 8)] + [tail]
    for blk in blocks:                   # compression: 2 SipRounds per 8-byte word
        m = _le64(blk)
        v3 ^= m
        v0, v1, v2, v3 = _round(v0, v1, v2, v3)
        v0, v1, v2, v3 = _round(v0, v1, v2, v3)
        v0 ^= m
    v2 ^= 0xFF
    for _ in range(4):                   # finalization: 4 SipRounds
        v0, v1, v2, v3 = _round(v0, v1, v2, v3)
    return v0 ^ v1 ^ v2 ^ v3


def crc16(data, crc=0xFFFF):
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else (crc << 1)
            crc &= 0xFFFF
    return crc


def toy_tag(key, msg):
    return crc16(bytes(key) + bytes(msg))          # NOT SECURE - see the header


def body(dev, ctr, payload):
    return "{}:{}:{}".format(dev, ctr, payload)


def seal(dev, ctr, payload, key, mode="siphash"):
    b = body(dev, ctr, payload)
    if mode == "siphash":
        return "{}:{:016x}".format(b, siphash24(key, b.encode()))
    if mode == "toy":
        return "{}:{:04x}".format(b, toy_tag(key, b.encode()))
    return "{}:{:04x}".format(b, crc16(b.encode()))   # "crc": integrity only, no key at all


class Counter:
    """Per-device message counter that survives a reset: reserve blocks in flash.

    Writing flash on every frame wears it and costs time, so the device stores only the END of
    the block it is using; after a reset it starts at that stored value (skipping unused numbers).
    load/save are callables, e.g. reading/writing a small file with open() on the board.
    """

    def __init__(self, load, save, block=100):
        self.load, self.save, self.block = load, save, block
        self.next = load()
        self.limit = self.next
        self.writes = 0

    def take(self):
        if self.next >= self.limit:
            self.limit = self.next + self.block
            self.save(self.limit)           # persist BEFORE using numbers from the new block
            self.writes += 1
        self.next += 1
        return self.next
