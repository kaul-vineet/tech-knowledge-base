# ADR 0005: Run 3 instances (N+1) and send confirmation emails asynchronously; no cache yet

## Status

Accepted (2026-10-28).

## Context

Library Loans grows from one library to 400 (stated in the brief). The lesson 15 log gives one library's
demand: 0.1 requests/s, route mix 44.9 % GET /books, 35.1 % GET /loans, 20 % POST /loans, mean service
time 45.2 ms. Stated assumptions: daily peak = 3 x average; 4 workers per instance; 150 ms per confirmation
email; hypothetical price 0.10 USD per instance-hour. SLO (lesson 15): p99 <= 300 ms, which must hold with
one instance down (deploys, crashes).

Measured by `app.py` (seeded queue simulation fed with the logged service times):

| Option | Mean service | Capacity per instance (p99 <= 300 ms) | Instances (N+1) | p99 at peak / one down | USD per 1M requests |
|---|---|---|---|---|---|
| email inside POST /loans | 75.1 ms | 35 req/s | 6 | 230.8 / 239.1 ms | 4.17 |
| email via the outbox (async) | 45.2 ms | 75 req/s | 3 | 102.4 / 130.4 ms | 2.08 |
| async + LRU cache for GET /books (hit ratio 0.65) | 32.6 ms | 105 req/s | 3 | 94.7 / 100.5 ms | 2.08 |

Little's law: 120 req/s x 45.2 ms = 5.4 requests in flight at peak; 24 emails/s x 150 ms = 3.6 emails in flight.

## Decision

1. Send confirmation emails through the outbox (lesson 9) with 5 concurrent sender slots (3.6 / 0.8).
2. Run 3 instances: ceil(peak / (benchmarked capacity x 0.8 headroom)) + 1 spare.
3. Do not add the cache now: it does not change the instance count at 400 libraries and adds invalidation
   risk. Revisit at about 600 libraries (peak 180 req/s); at 800 libraries the cache saves one instance (4 vs 5).
4. Fitness function `fitness_capacity.py` re-checks the plan (p99 with one instance down, peak share of
   capacity) whenever the log or the code's service time changes.

## Consequences

- Cost is driven by the spare instance at this size (3 instances for a load 2 can carry).
- The plan is only as good as the service-time sample: re-measure after big code changes (lesson 16's gates).
- Queue simulation, not a real load test: the k6 run against the real service is pending in CI.
