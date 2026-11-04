"""Stub of the micro:bit MicroPython `radio` module, with a shared "air" so
two (or more) stub boards can talk to each other in unit tests.

API per https://microbit-micropython.readthedocs.io/en/v2-docs/radio.html
  * on by default after `import radio` (since v1.1 / V2 v2.1.0-beta.1)
  * config(length=32, queue=3, channel=7, power=6, address=0x75626974,
    group=0, data_rate=RATE_1MBIT); send/receive need the radio on
  * send(str) = send_bytes(b'\\x01\\x00\\x01' + utf8); receive() strips those
    three bytes and raises ValueError if the message is not such a string
  * a full queue drops new messages
Behaviour taken from the MicroPython source (bbcmicrobit/micropython
modradio.cpp; the V2 port is assumed to match): a message longer than the
configured `length` is truncated by the sender, and the receiver truncates to
its own `length`; "radio is not enabled" ValueError when off.
Stub-only values (not from the docs): RATE_* numbers, RSSI = -45, timestamp =
running_time() * 1000. No real timing, collisions or range.

Single board:  `import radio` -> module functions use a default endpoint;
               tests use radio._inject(b"...") and radio.sent.
Two boards:    labtest.load_boards() gives each board its own Endpoint on one Air.
"""

STRING_HEADER = b"\x01\x00\x01"
RATE_1MBIT, RATE_2MBIT = 0, 1        # placeholders; the docs also allow 2 (250 kbit, V1 compat)
_DEFAULTS = dict(length=32, queue=3, channel=7, power=6, address=0x75626974,
                 group=0, data_rate=RATE_1MBIT)
_RANGES = dict(length=(1, 251), queue=(1, 254), channel=(0, 83), power=(0, 7),
               address=(0, 0xFFFFFFFF), group=(0, 255), data_rate=(0, 2))


class Air:
    """Everything sent by one endpoint reaches every other endpoint in range.

    L300 fault injection (stub only, seeded => the same faults on every run):
    loss / dup / reorder / corrupt are per-delivery probabilities. reorder holds a
    packet back and delivers it after the next packet to that board; corrupt flips
    one bit (bits 0-6, so text stays ASCII) in one byte after the 3-byte header.
    """

    def __init__(self, loss=0.0, dup=0.0, reorder=0.0, corrupt=0.0, seed=0):
        import random
        self.endpoints = []
        self.log = []            # (sender name, group, payload bytes) for tests
        self.loss, self.dup, self.reorder, self.corrupt = loss, dup, reorder, corrupt
        self.rng = random.Random(seed)
        self.faults = {"sent": 0, "lost": 0, "duplicated": 0, "reordered": 0, "corrupted": 0}
        self._held = {}          # endpoint name -> payload held back (reorder)

    def broadcast(self, sender, payload):
        self.log.append((sender.name, sender._cfg["group"], payload))
        self.faults["sent"] += 1
        for ep in self.endpoints:
            if ep is not sender:
                self._fault_deliver(ep, sender, payload)

    def _fault_deliver(self, ep, sender, payload):
        rng, f = self.rng, self.faults
        if not (self.loss or self.dup or self.reorder or self.corrupt):
            ep._deliver(sender, payload)
            return
        if rng.random() < self.loss:
            f["lost"] += 1
            return
        if rng.random() < self.corrupt and len(payload) > 3:
            i = rng.randrange(3, len(payload))
            payload = payload[:i] + bytes([payload[i] ^ (1 << rng.randrange(7))]) + payload[i + 1:]
            f["corrupted"] += 1
        copies = 2 if rng.random() < self.dup else 1
        f["duplicated"] += copies - 1
        if ep.name not in self._held and rng.random() < self.reorder:
            self._held[ep.name] = (sender, payload)   # delivered after the next one
            f["reordered"] += 1
            copies -= 1
        for _ in range(copies):
            ep._deliver(sender, payload)
        if copies and ep.name in self._held:
            held_sender, held = self._held.pop(ep.name)
            ep._deliver(held_sender, held)


class Endpoint:
    """One board's radio. Has the same public functions as the module."""
    RATE_1MBIT, RATE_2MBIT = RATE_1MBIT, RATE_2MBIT

    def __init__(self, air, name="board", clock=None):
        self.air, self.name, self._clock = air, name, clock or (lambda: 0)
        air.endpoints.append(self)
        self._reset()

    def _reset(self):
        self._cfg = dict(_DEFAULTS)
        self._on = True          # import turns the radio on
        self._queue = []         # [(bytes, rssi, timestamp_us)]
        self.sent = []           # payload bytes as sent (after truncation)
        self.dropped = 0         # messages lost because the queue was full

    # ---- real API
    def on(self):
        self._on = True

    def off(self):
        self._on = False
        self._queue = []

    def config(self, **kwargs):
        for key, value in kwargs.items():
            if key not in _DEFAULTS:
                raise TypeError("unexpected keyword argument '%s'" % key)
            lo, hi = _RANGES[key]
            if not lo <= value <= hi:
                raise ValueError("value out of range")
        self._cfg.update(kwargs)

    def reset(self):
        self._cfg = dict(_DEFAULTS)

    def send_bytes(self, message):
        self._check_on()
        payload = bytes(message)[: self._cfg["length"]]   # sender truncates to `length`
        self.sent.append(payload)
        self.air.broadcast(self, payload)

    def send(self, message):
        self.send_bytes(STRING_HEADER + str(message).encode("utf-8"))

    def receive_full(self):
        self._check_on()
        return self._queue.pop(0) if self._queue else None

    def receive_bytes(self):
        full = self.receive_full()
        return None if full is None else full[0]

    def receive_bytes_into(self, buffer):
        msg = self.receive_bytes()
        if msg is None:
            return None
        n = min(len(msg), len(buffer))
        buffer[:n] = msg[:n]
        return len(msg)

    def receive(self):
        msg = self.receive_bytes()
        if msg is None:
            return None
        if not msg.startswith(STRING_HEADER):
            raise ValueError("received packet is not a string")
        return msg[3:].decode("utf-8")     # UnicodeDecodeError is a ValueError too

    # ---- internals / test helpers
    def _check_on(self):
        if not self._on:
            raise ValueError("radio is not enabled")

    def _hears(self, sender):
        a, b = self._cfg, sender._cfg
        return (self._on and a["channel"] == b["channel"] and a["address"] == b["address"]
                and a["group"] == b["group"] and a["data_rate"] == b["data_rate"])

    def _deliver(self, sender, payload):
        if self._hears(sender):
            self._inject(payload)

    def _inject(self, payload):
        """Queue raw bytes as if received (drops when the queue is full)."""
        if not self._on:
            return
        if len(self._queue) >= self._cfg["queue"]:
            self.dropped += 1
            return
        self._queue.append((bytes(payload)[: self._cfg["length"]], -45, self._clock() * 1000))

    def _inject_str(self, text):
        self._inject(STRING_HEADER + text.encode("utf-8"))


# ---- module-level API for single-board use (`import radio`)
def _clock():
    import microbit
    return microbit.running_time()


_air = Air()
_default = Endpoint(_air, "default", _clock)
sent = _default.sent

on, off, config, reset = _default.on, _default.off, _default.config, _default.reset
send, send_bytes = _default.send, _default.send_bytes
receive, receive_bytes, receive_bytes_into, receive_full = (
    _default.receive, _default.receive_bytes, _default.receive_bytes_into, _default.receive_full)
_inject, _inject_str = _default._inject, _default._inject_str


def _reset():
    global sent
    _default._reset()
    sent = _default.sent
