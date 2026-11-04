"""Plumbing for lab 17 (not the lesson's concept): a seeded discrete-event simulator (simulated milliseconds,
nothing sleeps), a zone-aware latency model with a slow-message tail, percentiles, and the history checks.
Same seed -> same output on every machine."""
import heapq, random

ZONE_MS = {"same": 1.0, "zone": 5.0, "region": 30.0}  # one-way base latency by distance (assumed, not measured)
REPLICA_ZONE = {"a": "A", "b": "B", "c": "C"}  # zones A and B share a region; C is another region
TAIL_P = 0.05  # share of messages that hit the slow tail (GC pause, retransmit): 20-80 ms extra


def distance(z1, z2):
    if z1 == z2:
        return "same"
    return "region" if "C" in (z1, z2) else "zone"


class Sim:
    """Event loop: at(t, fn, *args) schedules fn at simulated time t (ms); run() executes in time order."""
    def __init__(self, seed):
        self.rng, self.now, self.queue, self.seq, self.down = random.Random(seed), 0.0, [], 0, set()

    def at(self, t, fn, *args):
        self.seq += 1
        heapq.heappush(self.queue, (t, self.seq, fn, args))

    def delay(self, zone, replica):
        """One-way latency: base by distance + jitter, and 5% of messages hit a slow tail (GC, retransmit)."""
        d = ZONE_MS[distance(zone, REPLICA_ZONE[replica])] + self.rng.expovariate(1 / 1.0)
        return d + (self.rng.uniform(20, 80) if self.rng.random() < TAIL_P else 0.0)

    def send(self, zone, replica, fn, *args):
        """Request to a replica and its reply each take one delay; a down replica never answers (a timeout)."""
        if replica not in self.down:
            there = self.now + self.delay(zone, replica)
            self.at(there, fn, there + self.delay(zone, replica), *args)

    def run(self, until):
        while self.queue and self.queue[0][0] <= until:
            t, _, fn, args = heapq.heappop(self.queue)
            self.now = t
            fn(*args)


def pct(values, p):
    values = sorted(values)
    return round(values[min(len(values) - 1, int(p / 100 * len(values)))], 1) if values else None


def anomalies(history):
    """Single-writer register (versions 1, 2, 3 ... in write order). Counts per ok read:
    stale     = returned a version older than a write that FINISHED before the read STARTED;
    inversion = returned a version older than what an earlier, already finished read returned (new-then-old);
    ryw       = the writer read back something older than its own last acknowledged write;
    age_max   = longest time a stale read lagged: read start - end of the first write newer than what it returned.
    No stale and no inversion <=> linearizable for this history shape (cross-checked in test_quorum.py)."""
    ok = [op for op in history if op["ok"]]
    writes = sorted((op for op in ok if op["f"] == "write"), key=lambda o: o["end"])
    reads = sorted((op for op in ok if op["f"] == "read"), key=lambda o: o["start"])
    by_end = sorted(reads, key=lambda o: o["end"])
    stale = inversion = ryw = 0
    write_end, age_max = {w["value"]: w["end"] for w in writes}, 0.0
    wi = ri = 0
    done_write = seen_read = 0
    for r in reads:
        while wi < len(writes) and writes[wi]["end"] < r["start"]:
            done_write = max(done_write, writes[wi]["value"])
            wi += 1
        while ri < len(by_end) and by_end[ri]["end"] < r["start"]:
            seen_read = max(seen_read, by_end[ri]["value"])
            ri += 1
        stale += r["value"] < done_write
        if r["value"] < done_write:
            age_max = max(age_max, r["start"] - write_end.get(r["value"] + 1, r["start"]))
        inversion += r["value"] < seen_read
        ryw += r["process"] == "writer" and r["value"] < done_write
    return {"stale": stale, "inversions": inversion, "ryw": ryw, "reads": len(reads), "age_max": round(age_max, 1)}
