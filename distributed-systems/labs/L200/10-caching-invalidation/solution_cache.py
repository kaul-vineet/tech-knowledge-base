"""SOLUTION for the lesson 10 build task (python solution_cache.py): cache.py + request coalescing.
L200 lesson 10 (python cache.py): cache-aside with a TTL in front of a slow price database.
Shows hits and misses, a stale read after a write WITHOUT invalidation, invalidate-on-write, and a
thundering herd: 50 concurrent misses on one cold key = 50 database reads. Simulated clock for TTLs."""
import threading, time

from helpers import SimClock


class PriceDB:
    """The source of truth (stands in for a remote database): slow on purpose, counts every read."""
    def __init__(self, delay=0.2):
        self.prices, self.reads, self.delay, self.lock = {"apple": 5}, 0, delay, threading.Lock()

    def read(self, sku):
        with self.lock:
            self.reads += 1
        time.sleep(self.delay)  # a slow query: the window in which a herd piles up
        return self.prices[sku]

    def write(self, sku, price):
        self.prices[sku] = price


class TTLCache:
    def __init__(self, ttl, clock):
        self.ttl, self.clock, self.data = ttl, clock, {}

    def get(self, key):  # None = absent or expired
        value, expires = self.data.get(key, (None, 0))
        return value if self.clock() < expires else None

    def set(self, key, value):
        self.data[key] = (value, self.clock() + self.ttl)

    def delete(self, key):
        self.data.pop(key, None)


class PriceService:
    """Cache-aside: the application reads the cache, falls back to the DB on a miss, then fills the cache."""
    def __init__(self, db, cache, invalidate=True):
        self.db, self.cache, self.invalidate = db, cache, invalidate
        self.lock, self.inflight = threading.Lock(), {}  # request coalescing: one DB read per key at a time

    def get_price(self, sku):
        value = self.cache.get(sku)
        if value is not None:
            return value
        with self.lock:  # miss: am I the first (leader) or does a read for this key already fly?
            flight = self.inflight.get(sku)
            leader = flight is None
            if leader:
                flight = self.inflight[sku] = {"done": threading.Event()}
        if not leader:
            flight["done"].wait()  # followers wait for the leader's result instead of hitting the DB
            return flight["value"]
        try:
            flight["value"] = self.db.read(sku)  # only the leader reads the source of truth
            self.cache.set(sku, flight["value"])
        finally:
            with self.lock:
                del self.inflight[sku]
            flight["done"].set()
        return flight["value"]

    def set_price(self, sku, price):
        self.db.write(sku, price)  # 1) write the database (the source of truth)
        if self.invalidate:
            self.cache.delete(sku)  # 2) invalidate-on-write: the next read misses and refetches


def herd(service, sku="apple", n=50):
    """n threads read one cold key at the same moment; returns (db reads, distinct values seen)."""
    start, seen, before = threading.Barrier(n), [], service.db.reads
    def reader():
        start.wait()
        seen.append(service.get_price(sku))
    threads = [threading.Thread(target=reader) for _ in range(n)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    return service.db.reads - before, sorted(set(seen))


def main():
    db, clock = PriceDB(), SimClock()
    svc = PriceService(db, TTLCache(30, clock), invalidate=False)
    print("cache-aside  :", [svc.get_price("apple") for _ in range(3)], f"-> db reads {db.reads} (1 miss, 2 hits)")
    svc.set_price("apple", 7)  # no invalidation: the cache keeps 5 until its TTL (30 s) runs out
    for t in (0, 10, 29, 30):
        clock.t = t
        price = svc.get_price("apple")
        print(f"no invalidate: t={t:>2}s read {price}", "(STALE, db has 7)" if price != 7 else "(fresh)")
    svc.invalidate, clock.t = True, 100
    svc.set_price("apple", 9)
    print(f"invalidate   : t=100s write 9 -> read {svc.get_price('apple')} (fresh)")
    svc.cache.delete("apple")  # the key just expired ...
    reads, values = herd(svc)  # ... and 50 requests arrive together
    print(f"herd         : 50 concurrent reads of a cold key -> {reads} db reads, values {values}")


if __name__ == "__main__":
    main()
