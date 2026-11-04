## Why it matters
A team asks for "strong consistency" everywhere, and every read now crosses regions. Another team turns it off everywhere, and a lock key hands out two owners. Consistency is not one switch: it is a menu of guarantees with prices in latency and availability. A designer picks per use case, from measurements, and writes the choice down.

## Mental model
A consistency model is the set of histories clients may observe. Stronger models allow fewer histories:

```
linearizable   one copy, real-time order: once any read sees v, every later read sees >= v
  sequential   one total order that respects each client's own order, not real time
  causal       effects never appear before their causes; concurrent writes may differ by replica
  eventual     replicas agree once updates stop; meanwhile reads may go back in time
   + session guarantees: read-your-writes, monotonic reads (per client)
```

With N replicas, a write waits for W acknowledgements and a read for R replies. If R + W > N, every read quorum overlaps every write quorum.

## Design space
Abadi's PACELC names the two forces. If there is a **P**artition, the system trades **A**vailability against **C**onsistency; **E**lse, in normal operation, it trades **L**atency against **C**onsistency. The second trade is paid on every request, not only during rare partitions, which is why it shaped Dynamo, Cassandra and Riak more than CAP did.

The options in the lab (N = 3, replicas in zones A and B of one region and in zone C of another):
- **R = 1, W = 1** (eventual): the fastest replica answers; stale reads and read-your-writes violations.
- **R + W > N** (R = 2, W = 2): no stale read of a finished write; still available with one region down.
- **R = N or W = N**: one slow or missing replica stalls every read or write.
- **Overlap + read write-back** (Attiya, Bar-Noy and Dolev's two-phase read): a read that saw a newer value than some replicas writes it back to W replicas before returning, so no later read can see older. Abadi notes that a plain quorum is not enough for linearizability; this is the addition.

## How to decide
1. Write each use case's constraint as numbers: maximum stale share, read-your-writes yes/no, linearizable yes/no, p99 budget, availability when a region is lost.
2. Measure every candidate on the same seeded workload, including a slow-message tail, because the anomalies live in the tail.
3. Pick the cheapest setting that meets all constraints, record it as an ADR, and add a fitness test.

Worked example (lab output, seed 17, 10 s simulated, about 2,100 reads per setting): R = 1 W = 1 reads p99 60.5 ms, 16.74% stale (up to 86.9 ms old), 15 read-your-writes violations. R = 2 W = 2 reads p99 65.9 ms, 0% stale, but **2 new-then-old inversions**: a read returned version 28 after another read had already returned 29, while the write of 29 was still in flight. R = 3 W = 1 is linearizable but answers 0% of reads when region C is down. With write-back, R = 2 W = 2 has 0 inversions, stays 100% available with C down, and pays for it in the tail: read p99 65.9 -> 124.5 ms, p50 unchanged at 12.5-12.7 ms, because the extra round trip only happens when replicas disagree. Decisions: cart badge R = 1 W = 1; feature flags R = 2 W = 2; lock owner/config R = 2 W = 2 with write-back. `test_fitness.py` keeps that last choice true on ten seeds.

## Failure modes at scale
- **Sloppy quorums and hinted handoff** (Dynamo) keep writes available during failures by writing to substitute nodes; R + W > N then no longer guarantees overlap with the replicas that hold the latest value.
- **Clock-based last-writer-wins** across regions silently drops one of two concurrent writes; noticed only in business data.
- **Tail amplification**: R or W waits for the slowest of its quorum, so p99 grows with N and with cross-region placement.
- **Rare anomalies**: 2 inversions in about 2,100 reads will not appear in example tests. A history checker (lesson 21) finds them; so does an angry customer.

## Common mistakes
- Treating R + W > N as "linearizable" (the lab shows it is not without write-back).
- Choosing one global consistency level instead of one per use case.
- Measuring averages; the trade-offs show at p99 and in the slow-message tail.
