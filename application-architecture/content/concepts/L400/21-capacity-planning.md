**Concept: Cost and capacity planning: load model, Little's law, benchmarks, headroom, cost per request**

## Why it matters
Library Loans will host 400 libraries. How many instances do we run, do we need a cache, and should the new
confirmation email be sent inside the request or later? In the lab the naive sum, average rate divided by what the workers can do
at 100 % busy, said one instance. At the daily peak that instance ran at 135 % utilization and its p99 was
58 seconds against a 300 ms SLO.

## Mental model
Capacity planning is a chain of measured numbers, each checked by code.

```
demand      L300 log: 0.1 req/s per library, mix 45/35/20 %, mean service 45.2 ms
            x 400 libraries x peak factor 3 (stated)  ─►  avg 40 req/s, peak 120 req/s
Little      L = λ W:  120 req/s x 45.2 ms = 5.4 requests in flight
benchmark   one instance (4 workers), queue simulation with the logged service times:
            highest rate with p99 <= 300 ms = capacity (75 req/s)
sizing      ceil(peak / (capacity x 0.8 headroom)) + 1 spare  =  3 instances
cost        instances x price / requests  ─►  USD per million requests
gate        p99 with one instance down <= SLO  (fitness_capacity.py)
```

## Design space
- **Scale out** (more instances): linear cost, no code change, until a shared resource (the database, one
  SQLite writer) becomes the bottleneck.
- **Scale up**: fewer, larger failure units; the spare costs more.
- **Cache** hot reads: cuts service time for hits, adds staleness and invalidation work (distributed-systems
  lesson 10). Measure the hit ratio, do not assume it.
- **Async work** (outbox plus workers, lesson 9): takes slow side effects out of the request path. Size the
  workers with Little's law too.
- **Headroom and N+1.** Plan to use part of the capacity at peak (spikes, garbage collection, deploys) and keep
  one instance spare so the SLO survives a crash or a rolling deploy.

## How to decide
Criteria: the SLO (lesson 15) with one instance down, cost per request, operational risk of each mechanism,
and when the next limit arrives.

Worked example (lab; stated assumptions: peak = 3 x average, 4 workers per instance, 150 ms per email,
hypothetical 0.10 USD per instance-hour):

| Option | Mean service | Capacity per instance | Instances | p99 peak / one down | USD per 1M requests |
|---|---|---|---|---|---|
| email inside POST /loans | 75.1 ms | 35 req/s | 6 | 230.8 / 239.1 ms | 4.17 |
| email via the outbox | 45.2 ms | 75 req/s | 3 | 102.4 / 130.4 ms | 2.08 |
| outbox + LRU cache for GET /books (hit ratio 0.65, measured) | 32.6 ms | 105 req/s | 3 | 94.7 / 100.5 ms | 2.08 |

Async email halves the cost. The cache changes no instance count at 400 libraries, so the decision (ADR 0005)
is "not yet": at 800 libraries it saves one instance (4 instead of 5). Little's law also sizes the email
workers: 24 emails/s x 0.15 s = 3.6 in flight, so 5 sender slots at 80 % headroom. A local model may draft the
capacity memo; code rejects any number that is not in the plan, such as the first draft's "peak of 40.0".

## Failure modes at scale
- **Planning on averages.** Queues grow without bound as utilization nears 100 %. Signal: p99 climbs before CPU looks full.
- **QPS as the unit.** Requests differ in cost; the Google SRE book recommends modelling capacity in
  resources (CPU) rather than queries per second. Re-measure the mix when features change.
- **Hidden shared limits.** Database connections, one writer per SQLite file, rate limits of an email relay.
  Signal: more instances, same latency.
- **No spare.** With exactly enough instances, a deploy or crash pushes the rest past capacity (try-it 2:
  p99 58 s on the survivor).
- **Stale model.** A new N+1 query (lesson 16) changes service time silently. Re-run the capacity gate whenever
  the service-time sample changes.

## Common mistakes
- Using c / S (88.5 req/s per instance here) as the capacity: that is 100 % busy, where the p99 is already
  seconds. Use the highest rate that still meets the SLO.
- Treating a simulation or micro-benchmark as a load test. Confirm with a real load test (k6 against the
  service) before committing the budget.
- Quoting cost per instance instead of per request, which is what compares options.
