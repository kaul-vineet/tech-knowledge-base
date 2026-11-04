"""Backend/gateway storage: a delta-state CRDT keyed by dots, and the naive wall-clock LWW store (failure lab).

ReadingStore = grow-only map dot -> reading, dot = (dev, boot, seq). Its causal context is compacted like a
delta-CRDT (Almeida et al.): a version vector of contiguous high-water marks per (dev, boot) - the
distributed-systems L400 #18 GCounter, whose merge is the per-slot max - plus a "dot cloud" of dots above it.
Readings are immutable, so merge is set union; if two different values ever claim one dot, max() picks the same
winner on every replica (still a join) and the conflict is counted.

WallClockLWWStore = what a time-series table keyed (device, timestamp) does on a duplicate key: last write wins
(InfluxDB docs: same measurement + tag set + timestamp -> the new field value). Rows use the L400 #18 LWWRegister.
"""
import _kb

GCounter = _kb.crdts().GCounter
LWWRegister = _kb.crdts().LWWRegister
REC_BYTES = 9                                        # one record on the radio (schema 2)


def key(dev, boot):
    return "%d.%d" % (dev, boot)


class ReadingStore:
    kind = "dots"

    def __init__(self):
        self.by_key = {}                             # (dev, boot) -> {seq: value}
        self.vv = GCounter()                         # "dev.boot" -> contiguous hw (merge = per-slot max)
        self.cloud = set()                           # dots received above the hw
        self.conflicts = 0

    def covered(self, dot):
        dev, boot, seq = dot
        return seq <= self.vv.slots.get(key(dev, boot), 0) or dot in self.cloud

    def add(self, dot, value):
        """Idempotent: a duplicate (radio dup, retry, two gateways, gossip) changes nothing. True if new."""
        dev, boot, seq = dot
        rows = self.by_key.setdefault((dev, boot), {})
        if seq in rows:
            if rows[seq] != value:
                self.conflicts += 1
                rows[seq] = max(rows[seq], value, key=repr)
            return False
        rows[seq] = value
        self.cloud.add(dot)
        self._compact(dev, boot)
        return True

    def _compact(self, dev, boot):
        """Move dots that extend the contiguous prefix from the cloud into the version vector."""
        hw = self.vv.slots.get(key(dev, boot), 0)
        while (dev, boot, hw + 1) in self.cloud:
            self.cloud.discard((dev, boot, hw + 1))
            hw += 1
        self.vv.slots[key(dev, boot)] = hw

    def contiguous(self, dev, boot):
        return self.vv.slots.get(key(dev, boot), 0)

    def digest(self):
        return dict(self.vv.slots), frozenset(self.cloud)

    def delta_for(self, digest):
        """Only what the peer lacks (delta-state anti-entropy)."""
        vv, cloud = digest
        out = {}
        for (dev, boot), rows in self.by_key.items():
            hw = vv.get(key(dev, boot), 0)
            for seq, value in rows.items():
                if seq > hw and (dev, boot, seq) not in cloud:
                    out[(dev, boot, seq)] = value
        return out

    def merge_delta(self, delta):
        return sum(self.add(dot, value) for dot, value in sorted(delta.items()))

    def merge(self, other):
        """Full-state join (used by the law tests): vv = per-slot max, readings = union, cloud re-compacted."""
        out = ReadingStore()
        out.vv = self.vv.merge(other.vv)             # L400 #18 GCounter.merge
        for s in (self, other):
            for k, rows in s.by_key.items():
                mine = out.by_key.setdefault(k, {})
                for seq, value in rows.items():
                    mine[seq] = max(mine[seq], value, key=repr) if seq in mine else value
        out.cloud = {d for d in self.cloud | other.cloud if d[2] > out.vv.slots.get(key(d[0], d[1]), 0)}
        for dev, boot in out.by_key:
            out._compact(dev, boot)
        out.conflicts = self.conflicts + other.conflicts
        return out

    def rows(self, dev=None):
        """[(dot, value)] ordered by (dev, boot, seq): per-device order never uses wall time."""
        return [((d, b, s), v) for (d, b), rows in sorted(self.by_key.items()) if dev in (None, d)
                for s, v in sorted(rows.items())]

    def dots(self):
        return {dot for dot, _ in self.rows()}

    def contiguous_rows(self, dev, boot):
        hw = self.contiguous(dev, boot)
        return [((dev, boot, s), v) for s, v in sorted(self.by_key.get((dev, boot), {}).items()) if s <= hw]

    def state(self):
        return self.rows(), sorted(self.vv.slots.items()), sorted(self.cloud)


class WallClockLWWStore:
    """FAILURE LAB: rows keyed (dev, device wall second); a later write to the same key overwrites."""
    kind = "lww"
    _clock = [0]                                     # arrival order, unique across replicas (no ties)

    def __init__(self):
        self.regs = {}                               # (dev, wall_s) -> LWWRegister(value=(dot, value))
        self.seen = ReadingStore()                   # what the gateway acknowledges: dots it RECEIVED

    def add(self, dot, value):
        new = self.seen.add(dot, value)
        if new:
            WallClockLWWStore._clock[0] += 1
            k = (dot[0], value[0])                   # value[0] = device wall clock (seconds)
            self.regs[k] = LWWRegister((dot, value), WallClockLWWStore._clock[0], "r")
        return new

    def contiguous(self, dev, boot):
        return self.seen.contiguous(dev, boot)

    def digest(self):
        return self.seen.digest()

    def delta_for(self, digest):
        return {"regs": dict(self.regs), "seen": self.seen.delta_for(digest)}   # full state of the rows

    def merge_delta(self, delta):
        for k, reg in delta["regs"].items():
            self.regs[k] = self.regs[k].merge(reg) if k in self.regs else reg
        return self.seen.merge_delta(delta["seen"])

    def rows(self, dev=None):
        got = sorted(r.value() for r in self.regs.values())
        return [(dot, value) for dot, value in got if dev in (None, dot[0])]

    def dots(self):
        return {dot for dot, _ in self.rows()}

    def contiguous_rows(self, dev, boot):
        return [(d, v) for d, v in self.rows(dev) if d[1] == boot and d[2] <= self.contiguous(dev, boot)]


def make_store(kind):
    return WallClockLWWStore() if kind == "lww" else ReadingStore()
