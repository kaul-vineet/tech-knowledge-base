## Why it matters
B fails 30% of the time for a few seconds after each deploy. Without retries, users see errors. With naive retries, a thousand clients hammer B in lock-step, and a blip becomes an outage.

## Mental model
Retrying is calling back a busy shop: wait longer each time (backoff), pick a random moment up to that wait (jitter) so callers don't all ring together, and stop when your phone credit (retry budget) runs low.

```
attempt    0      1      2      3
ceiling   20ms   40ms   80ms  160ms    min(cap 500 ms, 20 ms × 2^attempt)
sleep     uniform(0, ceiling)          ← full jitter
```

## How it works
1. **Retry only transient failures, a bounded number of times:** 429/502/503/504, connection errors and timeouts, at most 4 attempts. A 404 will fail again, so it is not retried. → see lab step 3
2. **Capped exponential backoff + full jitter:** sleep = `uniform(0, min(cap, base × 2^attempt))`. AWS's simulation found backoff without jitter "the clear loser". → see lab step 2
3. **A retry budget stops storms.** A per-client token bucket (failure −1, success +ratio, no retries below half) keeps load at ×1.0 when B is sick, instead of up to ×4.0. → see lab step 4

## Common mistakes
- Retrying forever, with fixed delays, or on 4xx errors.
- Retrying at every layer: 3 attempts at each of 5 layers = 243 calls at the bottom.
- Retrying a POST that charges money without an idempotency key (lesson 5).
