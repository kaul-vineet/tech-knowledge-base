"""Build-task check: request coalescing turns a 50-request herd on a cold key into ONE database read.
Default target = solution_cache.py. Test YOUR cache.py:  BUILD_TARGET=mine python -m unittest test_build_task -v
(PowerShell: $env:BUILD_TARGET="mine"; python -m unittest test_build_task -v)"""
import importlib.util, os, unittest
from pathlib import Path

from helpers import SimClock

HERE = Path(__file__).resolve().parent
FILE = "cache.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution_cache.py"
spec = importlib.util.spec_from_file_location("target_cache", HERE / FILE)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class TestCoalescing(unittest.TestCase):
    def test_herd_of_50_makes_one_db_read(self):
        svc = c.PriceService(c.PriceDB(delay=0.2), c.TTLCache(30, SimClock()))
        reads, values = c.herd(svc, n=50)
        self.assertEqual((reads, values), (1, [5]))

    def test_different_keys_are_not_merged_and_later_reads_hit_the_cache(self):
        db = c.PriceDB(delay=0.05)
        db.prices["pear"] = 4
        svc = c.PriceService(db, c.TTLCache(30, SimClock()))
        self.assertEqual((c.herd(svc, "apple", 10)[0], c.herd(svc, "pear", 10)[0]), (1, 1))
        self.assertEqual(c.herd(svc, "apple", 10)[0], 0)  # cached now


if __name__ == "__main__":
    unittest.main()
