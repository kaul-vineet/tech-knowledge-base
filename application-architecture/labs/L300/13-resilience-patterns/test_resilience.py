import threading
import time
import unittest

import loans_service as base
from deps import Catalogue, Members
from failure_lab import run_waves, summary
from resilience import Bulkhead, BulkheadFull, CircuitBreaker, CircuitOpen, Pool, with_fallback


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def boom():
    raise ConnectionError("down")


class CircuitBreakerTest(unittest.TestCase):
    def setUp(self):
        self.clock, self.log = FakeClock(), []
        self.breaker = CircuitBreaker("cat", window=10, min_calls=5, failure_rate=0.5, open_s=1.0,
                                      clock=self.clock, log=self.log.append)

    def fail(self, n):
        for _ in range(n):
            with self.assertRaises(ConnectionError):
                self.breaker.call(boom)

    def test_opens_at_the_failure_rate_after_min_calls(self):
        self.fail(4)
        self.assertEqual(self.breaker.state, "closed")  # 4 calls < min_calls
        self.fail(1)
        self.assertEqual(self.breaker.state, "open")
        with self.assertRaises(CircuitOpen):
            self.breaker.call(lambda: "never called")

    def test_half_open_trial_closes_or_reopens(self):
        self.fail(5)
        self.clock.now = 1.0
        self.fail(1)  # trial fails -> open again
        self.assertEqual(self.breaker.state, "open")
        self.clock.now = 2.0
        self.assertEqual(self.breaker.call(lambda: "ok"), "ok")
        self.assertEqual([r["to"] for r in self.log], ["open", "half_open", "open", "half_open", "closed"])

    def test_successes_keep_it_closed(self):
        for _ in range(5):
            self.breaker.call(lambda: 1)
        self.fail(4)  # 4 of 9 = 44% < 50%
        self.assertEqual(self.breaker.state, "closed")


class PoolAndBulkheadTest(unittest.TestCase):
    def test_timeout_frees_the_caller_not_the_thread(self):
        pool, gate = Pool("p", 1), threading.Event()
        with self.assertRaises(TimeoutError):
            pool.call(gate.wait, 5, timeout=0.05)
        self.assertEqual(pool.busy, 1)  # the worker is still stuck in gate.wait
        gate.set()
        pool.shutdown()

    def test_bulkhead_rejects_the_call_over_its_limit(self):
        bulkhead, gate = Bulkhead("cat", 2), threading.Event()
        for _ in range(2):
            with self.assertRaises(TimeoutError):
                bulkhead.call(gate.wait, 5, timeout=0.02)
        with self.assertRaises(BulkheadFull):
            bulkhead.call(lambda: "x", timeout=0.02)
        gate.set()
        for _ in range(100):  # wait until both stuck workers have returned
            if bulkhead.busy == 0:
                break
            time.sleep(0.01)
        self.assertEqual(bulkhead.call(lambda: "x", timeout=1), "x")  # slots come back when workers finish
        bulkhead.shutdown()

    def test_fallback_only_for_expected_errors(self):
        self.assertEqual(with_fallback(boom, lambda exc: "fallback"), ("fallback", True))
        with self.assertRaises(ZeroDivisionError):
            with_fallback(lambda: 1 / 0, lambda exc: "fallback")  # a bug is not a dependency failure


class ServiceTest(unittest.TestCase):
    def test_healthy_dependencies(self):
        service = base.build_service(Members(), Catalogue(), log=lambda record: None)
        self.assertEqual(service.borrow("m1", "b1"),
                         {"member": "m1", "book": "b1", "title": "Title of b1", "degraded": False})
        with self.assertRaises(PermissionError):
            service.borrow("blocked-1", "b1")
        service.close()

    def test_symptom_slow_catalogue_starves_the_shared_pool(self):
        records = run_waves(base, Catalogue(mode="slow"))
        self.assertEqual(summary(records), {1: {"ok": 8}, 2: {"TimeoutError": 8}, 3: {"TimeoutError": 8}})
        self.assertTrue(all(r["pools"] == {"shared": "8/8"} for r in records if not r["ok"]))


if __name__ == "__main__":
    unittest.main()
