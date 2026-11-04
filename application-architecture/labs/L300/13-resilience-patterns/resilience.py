"""Resilience patterns around a flaky dependency: timeout, circuit breaker, bulkhead, fallback (lesson 13 lab code).

Stdlib only. Same ideas as resilience4j (Java) and Polly (.NET). Run the demo: python app.py
"""
import json
import sys
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout


def json_log(record, stream=sys.stdout):
    print(json.dumps(record, sort_keys=True), file=stream)  # structured log: one JSON object per line


class CircuitOpen(Exception):
    pass


class BulkheadFull(Exception):
    pass


class Pool:
    """Worker threads with a busy gauge. A timeout frees the CALLER, not the worker thread."""

    def __init__(self, name, workers):
        self.name, self.workers, self.busy, self._lock = name, workers, 0, threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=workers, thread_name_prefix=name)

    def _run(self, fn, args):
        with self._lock:
            self.busy += 1
        try:
            return fn(*args)
        finally:
            with self._lock:
                self.busy -= 1

    def call(self, fn, *args, timeout):
        future = self.executor.submit(self._run, fn, args)
        try:
            return future.result(timeout=timeout)  # timeout: stop WAITING after `timeout` s ...
        except FutureTimeout:
            future.cancel()  # ... but a call that already started keeps its thread until it returns
            raise TimeoutError(f"{self.name}: no answer within {timeout} s") from None

    def shutdown(self):
        self.executor.shutdown(wait=False, cancel_futures=True)


class Bulkhead(Pool):
    """Pool + semaphore for ONE dependency: at most `workers` calls in flight, the next is rejected at once."""

    def __init__(self, name, workers):
        super().__init__(name, workers)
        self._slots = threading.BoundedSemaphore(workers)

    def _run(self, fn, args):
        try:
            return super()._run(fn, args)
        finally:
            self._slots.release()  # the slot frees when the WORKER finishes, not when the caller gives up

    def call(self, fn, *args, timeout):
        if not self._slots.acquire(blocking=False):  # bulkhead: fail fast instead of queueing behind stuck calls
            raise BulkheadFull(f"{self.name}: {self.workers} calls already in flight")
        return super().call(fn, *args, timeout=timeout)


class CircuitBreaker:
    """closed -> open when >= failure_rate of the last `window` calls failed; open -> half_open after open_s;
    one trial call in half_open: success -> closed, failure -> open again."""

    def __init__(self, name, window=10, min_calls=5, failure_rate=0.5, open_s=1.0, clock=time.monotonic, log=json_log):
        self.name, self.min_calls, self.failure_rate, self.open_s = name, min_calls, failure_rate, open_s
        self.clock, self.log, self.state, self.opened_at, self.trial = clock, log, "closed", 0.0, False
        self.results, self._lock = deque(maxlen=window), threading.Lock()  # count-based sliding window

    def _move(self, to, **why):
        self.log({"evt": "breaker", "name": self.name, "from": self.state, "to": to, **why})
        self.state = to
        if to == "open":
            self.opened_at = self.clock()

    def call(self, fn, *args, **kwargs):
        with self._lock:
            if self.state == "open":
                if self.clock() - self.opened_at < self.open_s:
                    raise CircuitOpen(f"{self.name}: circuit open, failing fast")  # no call, no waiting
                self._move("half_open")
            if self.state == "half_open":
                if self.trial:
                    raise CircuitOpen(f"{self.name}: half-open, trial call in progress")
                self.trial = True
        try:
            result = fn(*args, **kwargs)
        except Exception:
            self._record(False)
            raise
        self._record(True)
        return result

    def _record(self, ok):
        with self._lock:
            if self.state == "half_open":
                self.trial = False
                self.results.clear()
                self._move("closed" if ok else "open", trial="ok" if ok else "failed")
                return
            self.results.append(ok)
            rate = self.results.count(False) / len(self.results)
            if self.state == "closed" and len(self.results) >= self.min_calls and rate >= self.failure_rate:
                self._move("open", failure_rate=round(rate, 2), calls=len(self.results))


def with_fallback(call, fallback):
    """Fallback: a degraded answer for the errors we expect from a sick dependency. Returns (value, degraded)."""
    try:
        return call(), False
    except (TimeoutError, CircuitOpen, BulkheadFull, ConnectionError) as exc:
        return fallback(exc), True
