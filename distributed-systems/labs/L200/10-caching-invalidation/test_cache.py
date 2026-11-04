import unittest

import cache as c
from helpers import SimClock


class TestCacheAside(unittest.TestCase):
    def setUp(self):
        self.clock, self.db = SimClock(), c.PriceDB(delay=0)

    def test_miss_then_hits_and_ttl_expiry(self):
        svc = c.PriceService(self.db, c.TTLCache(30, self.clock))
        self.assertEqual([svc.get_price("apple") for _ in range(3)], [5, 5, 5])
        self.assertEqual(self.db.reads, 1)
        self.clock.t = 30  # expires exactly at 30 s
        svc.get_price("apple")
        self.assertEqual(self.db.reads, 2)

    def test_stale_without_invalidation_fresh_with_it(self):
        stale = c.PriceService(self.db, c.TTLCache(30, self.clock), invalidate=False)
        stale.get_price("apple")
        stale.set_price("apple", 7)
        self.assertEqual(stale.get_price("apple"), 5)  # served from cache: stale
        fresh = c.PriceService(self.db, c.TTLCache(30, self.clock), invalidate=True)
        fresh.get_price("apple")
        fresh.set_price("apple", 9)
        self.assertEqual(fresh.get_price("apple"), 9)

    def test_thundering_herd_without_coalescing(self):
        svc = c.PriceService(c.PriceDB(delay=0.2), c.TTLCache(30, self.clock))
        reads, values = c.herd(svc, n=20)
        self.assertGreater(reads, 1)  # usually 20: every concurrent miss goes to the DB
        self.assertEqual(values, [5])


if __name__ == "__main__":
    unittest.main()
