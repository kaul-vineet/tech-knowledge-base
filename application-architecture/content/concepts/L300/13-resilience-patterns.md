**Concept: Resilience patterns – timeouts, circuit breaker, bulkhead, fallback**

## Why it matters
Borrowing a book calls two dependencies: members (must answer) and the catalogue (only for the title).
Outright failures are easy to see. Slowness is worse: every
waiting call holds a thread, and once the threads run out, borrowing fails even for members whose data
is fine. One sick dependency takes down every feature that shares its resources.

## Mental model
A ship has watertight compartments (bulkheads), so one leak floods one compartment. Inside each
compartment there is a fuse box (circuit breaker) that cuts power when a device keeps shorting, and the
crew has a spare (fallback) for anything that is nice to have.

```
borrow ─► members pool (4)  ─► Members           required: no fallback
       └► catalogue bulkhead (4, reject #5) ─► breaker ─► timeout 0.1 s ─► Catalogue
                                                   └─ fallback "(title unavailable)"
```

## How it works
1. **Circuit breaker states.** Closed counts results in a sliding window of 10 calls. At ≥ 50 % failures,
   after at least 5 calls, it opens and fails fast without calling. After `open_s` it goes half-open:
   one trial call closes it again or reopens it → see lab step 1
2. **Every transition is logged** as a JSON line (`from`, `to`, `failure_rate`), which is what you graph
   and alert on in production → see lab step 1
3. **A timeout frees the caller, not the thread.** `future.result(timeout=0.1)` stops waiting, but a call
   that has already started keeps its worker until it returns → see lab step 2
4. **Bulkhead = own pool + semaphore.** The catalogue gets 4 workers and a semaphore. Call 5 gets
   `BulkheadFull` at once instead of queueing behind stuck calls. The slot is freed when the worker
   finishes → see lab step 5
5. **Fallback only for expected errors.** `with_fallback` turns `TimeoutError`, `CircuitOpen`,
   `BulkheadFull` and `ConnectionError` into a degraded answer; a bug (`ZeroDivisionError`) still
   raises → see lab step 4

**Worked example** (`research/L300_concept_examples.py`): the catalogue hangs for 1 s and three waves of
8 borrows arrive 0.25 s apart. With one shared pool of 8, wave 1 gets fallback titles, but its 8 stuck
calls hold all 8 threads. The members checks in waves 2 and 3 then time out: 8/24 ok, and the log shows
`"pools": {"shared": "8/8"}`. The breaker opened after wave 1 and did not help. With 4 members workers
plus a catalogue bulkhead of 4, all 24 succeed with a fallback title.

## Failure modes
- **Thread starvation:** the pool gauge shows busy = max; calls to a healthy service time out.
- **Timeouts too long:** no errors, but latency climbs. With a 2 s timeout, every borrow took 1.0–2.4 s.
- **Breaker never opens:** the window is too large or `min_calls` too high for the traffic. Check the
  transition log.
- **Retry storm:** retries behind an open breaker or a full bulkhead multiply the load. Retry only
  idempotent calls, with a budget.

## Common mistakes
- One global pool or HTTP connection pool for every downstream call.
- Treating a timeout as a cancellation. In Python, Java and .NET the work may still be running.
- Falling back on a required dependency. A member check must fail closed, not with a made-up "yes".
