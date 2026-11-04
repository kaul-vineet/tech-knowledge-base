## Why it matters
Every server has a capacity. Above it, requests have to wait somewhere. If the waiting line is unbounded, a short burst becomes minutes of slow responses, clients time out and retry, and the server spends its capacity on answers nobody is waiting for. Backpressure and load shedding turn "everything is slow" into "a few requests are told to come back later".

## Mental model
Throughput is capped at capacity; waiting time is not. Little's law ties them together: requests in the system = arrival rate × time in the system. If you bound the queue, you bound the time.

```
arrivals 600/s --> [ queue ......... ] --> 4 workers --> 400/s out
                   unbounded: +200/s, wait grows by 0.5 s every second
                   bounded at 40: wait <= 40/400 s = 100 ms, the rest gets 503 + Retry-After
```

## How it works
1. **Open-model load.** Clients keep arriving at their own rate however slow the server is. This is how real users behave, and how k6's constant-arrival-rate executor tests. → see lab step 1
2. **Queueing delay grows faster than load.** Between 80% and 95% of capacity, throughput rises about 20% but the mean wait grows about five times. → see lab step 2
3. **Overload with an unbounded queue.** Above capacity the backlog grows linearly. It keeps growing after the burst until spare capacity drains it, and p99 peaks after the burst has ended. → see lab step 3
4. **Bounded queue and shedding.** Admission control refuses work when the line is full: a fast 503 with Retry-After (whole seconds, at least 1) instead of a slow 200 that arrives too late. → see lab step 5
5. **Adaptive concurrency.** Callers can cap their in-flight requests with AIMD: add a little on each success, multiply down on each 503. They then stop sending work that would only be shed. → see lab step 5 (tryIt 2)

Worked example (lab output): capacity is 400 requests/s. At 80% load the mean wait is 5.9 ms; at 95% it is 30.4 ms and p99 is 204.6 ms. During a 10 s burst at 150%, the unbounded queue's p99 reaches 4,689 ms at t=15, and only 3,781 of 10,686 answers arrive within the 1 s client timeout. With a bound of 40, p99 is 154.5 ms, 1,907 requests are shed, and goodput is 8,779.

## Failure modes
- **Latency explosion with 100% "success":** every request is eventually served, too late to matter. Watch p99 and goodput, not error rate.
- **Retry amplification:** timeouts trigger retries, which add load. Honour Retry-After and use retry budgets (lesson 4).
- **Shedding the wrong work:** health checks or paying users get dropped first. Use priorities.
- **Hidden queues:** thread pools, connection pools and socket backlogs queue work too. Bound them all.

## Common mistakes
- Sizing a queue for "no errors" instead of for a latency budget.
- Measuring with a closed model (fixed users that wait), which hides overload.
- Rejecting too late, after doing expensive work such as parsing and authentication.
