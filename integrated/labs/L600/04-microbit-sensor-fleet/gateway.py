"""Gateway: a micro:bit radio bridge + PC process (its radio is a stub Endpoint on the shared Air).

decode_frame() is the firmware-schema <-> backend contract: the schema byte selects the record layout and a
frame whose body is not a whole number of records is REJECTED (truncated by the radio, or a layout mismatch),
never half-parsed. A gateway acks only what its durable store holds: (boot, contiguous hw) per boot in the frame,
plus the exact dots of this frame that sit above that mark (selective ack).
"""
import _kb

radio = _kb.radio()
REC_LEN = {1: 8, 2: 9}                              # must match firmware/node.py (seam test)
HEADER = 3


def decode_frame(payload, trust_schema_byte=True):
    """-> (schema, dev, [(boot, seq, wall_s, temp, light)]) or raises ValueError."""
    if len(payload) < HEADER or payload[1] != ord("D"):
        raise ValueError("not a data frame")
    schema = payload[0] if trust_schema_byte else 2  # inject schema-drift: assume the newest layout
    if schema not in REC_LEN:
        raise ValueError("unknown schema %r" % payload[0])
    size, body = REC_LEN[schema], payload[HEADER:]
    if not body or len(body) % size:
        raise ValueError("body %d B is not a whole number of %d B records" % (len(body), size))
    recs = []
    for i in range(0, len(body), size):
        r = body[i:i + size]
        temp = r[7] - 256 if r[7] > 127 else r[7]
        light = r[8] if schema >= 2 else None
        recs.append((r[0], (r[1] << 8) | r[2], int.from_bytes(r[3:7], "big"), temp, light))
    return schema, payload[2], recs


def encode_ack(dev, epoch_s, boots_hw, dots=(), max_len=32):
    """Cumulative (boot, hw) entries first, then exact (boot, seq) entries while they fit in max_len bytes
    (never longer than the frame being answered, or 32 B, so the device's radio length can hold it)."""
    out = bytes([2, ord("A"), dev]) + int(epoch_s).to_bytes(4, "big") + bytes([len(boots_hw)])
    for boot, hw in boots_hw:
        out += bytes([boot]) + int(hw).to_bytes(2, "big")
    for boot, seq in dots:
        if len(out) + 3 > max_len:
            break
        out += bytes([boot]) + int(seq).to_bytes(2, "big")
    return out


class Gateway:
    def __init__(self, name, air, store, now_ms, skew_s=0, trust_schema_byte=True, on_new=None, selective=True):
        self.name, self.store, self.now_ms, self.skew_s = name, store, now_ms, skew_s
        self.trust, self.selective = trust_schema_byte, selective
        self.on_new = on_new or (lambda dot, gw: None)
        self.ep = radio.Endpoint(air, name)
        self.ep.config(length=251, queue=254)        # a bridge board: largest frame, deepest queue
        self.online = True
        self.rejected = 0
        self._busy = False

    def set_online(self, up):
        self.online = up
        self.ep.on() if up else self.ep.off()

    def poll(self):
        if self._busy or not self.online:
            return
        self._busy = True
        try:
            msg = self.ep.receive_bytes()
            while msg is not None:
                self.handle(msg)
                msg = self.ep.receive_bytes()
        finally:
            self._busy = False

    def handle(self, msg):
        if len(msg) < HEADER or msg[1] != ord("D"):
            return                                   # acks from the other gateway etc.
        try:
            schema, dev, recs = decode_frame(msg, self.trust)
        except ValueError:
            self.rejected += 1
            return
        boots, dots = [], []
        for boot, seq, wall, temp, light in recs:
            if self.store.add((dev, boot, seq), (wall, temp, light, schema)):
                self.on_new((dev, boot, seq), self.name)
            if boot not in boots:
                boots.append(boot)
            if self.selective and seq > self.store.contiguous(dev, boot):
                dots.append((boot, seq))             # stored, but above the contiguous mark: ack exactly
        epoch = self.now_ms() // 1000 + self.skew_s   # this gateway's clock: G2's runs 300 s slow
        hws = [(b, self.store.contiguous(dev, b)) for b in boots]
        self.ep.send_bytes(encode_ack(dev, epoch, hws, dots, max(len(msg), 32)))


class FleetAir(radio.Air):
    """The stub Air + (1) gateways answer as soon as a frame lands, (2) a radio partition by endpoint name."""

    def __init__(self, **faults):
        super().__init__(**faults)
        self.gateways, self.out_of_range = [], set()

    def _fault_deliver(self, ep, sender, payload):
        if sender.name in self.out_of_range or ep.name in self.out_of_range:
            return
        super()._fault_deliver(ep, sender, payload)

    def broadcast(self, sender, payload):
        super().broadcast(sender, payload)
        for gw in self.gateways:
            gw.poll()
