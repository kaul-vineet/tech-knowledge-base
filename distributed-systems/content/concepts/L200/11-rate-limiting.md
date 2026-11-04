## Why it matters
One customer's script loops on your API and takes all its capacity. A rate limiter gives each client a fair share and tells the greedy one, in a standard way, when to come back.

## Mental model
Each client owns a bucket that refills with tokens at a steady rate up to a maximum. A request takes one token; an empty bucket answers "429, try again in N seconds".

```
refill 2/s --> [ bucket, max 5 ] --> request takes 1 token
                   empty? --> 429 Too Many Requests
                              Retry-After: ceil(time to next token)
```

## How it works
1. **Token bucket.** Tokens refill continuously (`rate × elapsed`) up to `burst`; over time at most `rate` requests/s pass, in bursts of at most `burst`. → see lab step 1
2. **429 + Retry-After.** RFC 6585 defines 429 and says it MAY include Retry-After; RFC 9110 allows delay-seconds (a whole number) or an HTTP date. → see lab step 1
3. **Clients must honour it.** Retrying at once gets nothing sooner and multiplies server work. → see lab step 2
4. **Per-client keys.** One bucket per client, so a flood never empties another client's bucket. → see lab step 3
5. **Sliding window alternative.** Count requests in the last W seconds; no double burst at window edges. → see lab step 5

Worked example (demo output): rate 2/s, burst 5. Alice's first 5 requests at t=0 pass; the 6th finds 0 tokens, the next is (1 − 0) / 2 = 0.5 s away, sent as `Retry-After: 1`. She finished 12 requests at t=4 with 4 rejections; bob, retrying every 0.1 s, got 35.

## Trade-offs
| Use it when | Avoid it when |
|---|---|
| Shared capacity must be split fairly | Each of N instances enforces "the" limit (N × the limit) |
| Bursts are fine but the average must be capped | You need exact per-period counts for billing |

A fixed window ("5 per second, reset each second") let 10 requests through in 10 ms across a boundary; the token bucket let 5 (tryIt 1).

## Common mistakes
- Keying limits on a header the client chooses, not an authenticated identity.
- Fractional or missing Retry-After values.
- Clients that ignore Retry-After and retry in a tight loop.
