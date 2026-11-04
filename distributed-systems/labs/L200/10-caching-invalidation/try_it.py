"""tryIt experiments for lesson 10 (python try_it.py). Prints what actually happens."""
import cache as c
from helpers import SimClock

# tryIt 1: no invalidation; one read per second for 60 s; the price changes from 5 to 7 at t=0
for ttl in (30, 5):
    clock, db = SimClock(), c.PriceDB(delay=0)
    svc = c.PriceService(db, c.TTLCache(ttl, clock), invalidate=False)
    svc.get_price("apple")  # warm the cache with 5 just before the change
    svc.set_price("apple", 7)
    stale = 0
    for t in range(60):
        clock.t = t
        stale += svc.get_price("apple") != 7
    print(f"tryIt 1: TTL {ttl:>2} s -> {stale} stale reads of 60, {db.reads} db reads")

# tryIt 2: invalidate-on-write, but a slow reader fills the cache AFTER the writer deleted it
clock, db = SimClock(), c.PriceDB(delay=0)
svc = c.PriceService(db, c.TTLCache(30, clock), invalidate=True)
old = db.read("apple")         # reader A: cache miss, reads 5 from the DB ... (then stalls)
svc.set_price("apple", 11)     # writer B: DB = 11, deletes the (empty) cache entry
svc.cache.set("apple", old)    # reader A resumes and caches the OLD value
clock.t = 29
print(f"tryIt 2: race -> db has {db.prices['apple']}, cache serves {svc.get_price('apple')} until t=30 (TTL)")
