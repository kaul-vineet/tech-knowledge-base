"""Plumbing for lab 19 (not the lesson's concept): the region latency model, the seeded write stream, FIFO links,
percentiles and the multi-leader conflict counter. One-way base latencies are ASSUMPTIONS for the exercise (round
numbers of the right order for us-east / eu-west / ap-south), not measurements: replace them with your own."""
import random

REGIONS = ("us", "eu", "ap")
ONE_WAY_MS = {("us", "eu"): 40.0, ("us", "ap"): 110.0, ("eu", "ap"): 70.0}
TRAFFIC = {"us": 0.50, "eu": 0.35, "ap": 0.15}  # share of users (and writes) per region


def base(a, b):
    return 1.0 if a == b else ONE_WAY_MS.get((a, b)) or ONE_WAY_MS[(b, a)]


class Net:
    """d(a, b): one-way delay = base + jitter (mean 2 ms) + a 2% slow tail (50-150 ms). Replication streams are
    FIFO, like one TCP connection: an entry never overtakes an earlier one (needed for the log-prefix argument)."""
    def __init__(self, seed):
        self.rng, self.last = random.Random(seed), {}

    def d(self, a, b):
        tail = self.rng.uniform(50, 150) if self.rng.random() < 0.02 else 0.0
        return base(a, b) + self.rng.expovariate(1 / 2.0) + tail

    def send(self, a, b, t, fifo=False):
        """Arrival time at b of a message sent from a at time t; fifo=True for a replication stream."""
        arrive = t + self.d(a, b)
        if fifo:
            arrive = self.last[(a, b)] = max(arrive, self.last.get((a, b), 0.0))
        return arrive


def write_stream(seed, rate_per_s=100.0, duration_ms=20000.0, keys=100):
    """Poisson writes: (time ms, origin region, key). Keys are skewed (a few hot ones), like a product catalogue."""
    rng, t, out = random.Random(f"{seed}-writes"), 0.0, []
    weights = [1 / (k + 1) for k in range(keys)]
    while True:
        t += rng.expovariate(rate_per_s / 1000)
        if t >= duration_ms:
            return out
        origin = rng.choices(REGIONS, [TRAFFIC[r] for r in REGIONS])[0]
        out.append((t, origin, rng.choices(range(keys), weights)[0]))


def pct(values, p):
    values = sorted(values)
    return round(values[min(len(values) - 1, int(p / 100 * len(values)))], 1) if values else None


def conflicts(writes):
    """Concurrent writes to one key from different regions: w2 was accepted before w1 had reached w2's region.
    Last-writer-wins would silently drop one of them (a lost update)."""
    by_key, count = {}, 0
    for w in sorted(writes, key=lambda w: w["accepted"]):
        others = by_key.setdefault(w["key"], [])
        count += any(o["origin"] != w["origin"] and o["arrive"][w["origin"]] > w["accepted"] for o in others[-5:])
        others.append(w)
    return count
