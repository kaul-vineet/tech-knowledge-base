## Why it matters
Checkout calls `get_price("pear")` and it "just works" — until the price service moves to another machine. Now the call is two network messages, takes milliseconds, and can fail in ways a local function never does.

## Mental model
A remote call is a phone call, not a thought: you dial (request), wait, and hear an answer (response) — or silence.

```
A ── GET /price?item=pear ─────────────▶ B
A ◀── 200 {"item": "pear", "price": 4} ── B
latency = t_response − t_request   (time.perf_counter)
```

## How it works
1. **Request and response are messages.** A sends method + target; B answers status + headers + JSON body (marshalling). 2xx = success, 4xx = the client asked wrongly, 5xx = the server failed. → see lab step 3
2. **Errors are results.** `urllib` raises `HTTPError` for the 404, which A handles as a normal outcome. The third outcome is no reply at all: then A cannot know whether B did the work. → see lab step 1
3. **Latency needs a monotonic clock and the median.** `perf_counter()` cannot jump backwards like `time.time()`. README run: median 4.7 ms, so three sequential calls cost ≈14.1 ms. → see lab step 2

## Common mistakes
- Treating a remote call like a local one: no timeout, no error handling.
- Timing with `time.time()` — a clock adjustment gives negative or huge latencies.
- Averaging latency instead of looking at the median and the tail (p99).
