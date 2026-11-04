## Why it matters
Labs 3, 15, 16 and 19 measured latency and throughput. Foundations III explains the shapes those measurements took:
- why the unbounded queue's p99 exploded at 150% load (lab 16);
- why a timeout set at a leaf percentile turns into a root failure rate;
- why adding replicas sometimes makes a system slower.

Each formula comes with its assumptions and a seeded simulation, because the assumptions are where capacity plans fail.

## Definitions
- **Arrival rate** λ, **service rate** μ, **utilisation** ρ = λ/μ.
- **L**: mean number in the system. **W**: mean time in the system (sojourn). **Wq**: mean wait before service.
- **M/M/1**: Poisson arrivals, exponential service, one FIFO server, unbounded buffer.
- **Fan-out**: one root request waits for n leaf requests.
- **Serial fraction** σ: the part of a job that cannot run in parallel (contention).
- **Coherency cost** κ: pairwise coordination that grows with p(p - 1).

## Key results
1. **M/M/1 (T25.1).**
   - Balancing probability flow across the cut between n and n+1 gives λp_n = μp_{n+1}.
   - So p_n = (1 - ρ)ρ^n, which needs ρ < 1.
   - The means follow: L = ρ/(1 - ρ), W = 1/(μ - λ), Wq = ρ/(μ - λ).
2. **Little's law (T25.2).** L = λW for *any* stable system: any distributions, any number of servers, any service order.
   - Proof: the area under n(t) counts each customer's stay once.
   - On a window that starts and ends empty, the identity is exact.
3. **Tail amplification (T25.3).**
   - With independent leaves, P(root waits for a slow leaf) = 1 - (1 - p)^n ≈ np.
   - To hold the root at q, each leaf needs p ≤ 1 - (1 - q)^(1/n) ≈ q/n.
   - For any dependence: max p_i ≤ P ≤ min(1, Σp_i).
4. **Amdahl and USL (T25.4).**
   - Amdahl: S(p) = p/(1 + σ(p - 1)), bounded by 1/σ.
   - USL: C(p) = p/(1 + σ(p - 1) + κp(p - 1)), peaking at p* = √((1 - σ)/κ).
   - Beyond the peak, throughput falls.

## Intuition
Write W = (1/μ)·1/(1 - ρ). The second factor is the **queueing multiplier**: 2 at ρ = 0.5, 5 at 0.8, 10 at 0.9, 20 at 0.95. Utilisation is not a free efficiency target. The last few percent are paid for in latency, and in variance even more. This is why lab 16 bounds its queue and sheds load instead of letting work pile up.

Little's law is a conservation law, not a queueing model. Measure two of the three quantities and the third follows. Use it to size thread pools, connection pools and in-flight limits. It is also the basis of concurrency-limit algorithms such as Netflix's, mentioned in L300 #16's equivalents.

Fan-out turns rare into common. Dean and Barroso give the example: a server that is slow 1% of the time makes 63% of 100-way requests slow. It makes 18% of 2,000-way requests slow even when each server is slow only once in 10,000 requests. Their remedies attack either p or n: hedged requests, tied requests, micro-partitions, selective replication and canary requests.

Amdahl says the serial part caps speedup. The USL adds the other cost of scale: keeping p copies coherent costs on the order of p² pairwise exchanges. That is why throughput can turn *retrograde*.

## Worked example
**Little's law (25-P2).** 2,000 req/s × 0.150 s = 300 requests in flight. With 64 threads per instance you need at least ⌈300/64⌉ = 5 instances. But 5 instances means 94% busy threads, and T25.1 warns what that does to latency.

**M/M/1 (25-P1).** λ = 80/s and μ = 100/s give ρ = 0.8, L = 4, W = 50 ms and Wq = 40 ms. Check with Little: 80 × 0.05 = 4.

**Simulation results** (`perf_proofs.py`):

| check | simulated | theory |
|---|---|---|
| M/M/1 W at ρ = 0.5 / 0.8 / 0.9 (400,000 customers each) | 2.001 / 4.992 / 9.838 | 2 / 5 / 10 |
| Little: area vs Σ sojourn, window ending empty | equal to 1.1e-15 relative | exact |
| Little: L vs λW, arbitrary window | 1.3113 vs 1.3113 | equal in the limit |
| fan-out 1 / 10 / 100 slow-root fraction | 0.0095 / 0.0954 / 0.6329 | 0.0100 / 0.0956 / 0.6340 |

The Little's law check used a G/G/1 queue: uniform-jitter arrivals and log-normal service, deliberately not Markov.

**USL.** The formula's p* matched the numerical argmax for three (σ, κ) pairs (44.27 → 44, 30 → 30, 98.49 → 98). Then a simulated closed system was run: workers sharing one lock whose hold time grows with p - 1. Its relative capacity rose to 10.17 at p = 13 and fell to 5.10 at p = 40. A USL fit (with σ ≥ 0) predicted the peak at 15.3: useful for planning, but not exact. The machine-repairman curve is not literally a USL.

## Common misconceptions
- **"Average latency tells me the user experience."** Fan-out makes users feel the leaf *tail*. Set leaf targets at p99.99 when the root fans out 100-way (25-P4).
- **"80% utilisation is 80% efficiency."** In M/M/1 it means a mean delay of 5 service times, and much worse in the tail. Plan for headroom.
- **"Little's law needs Poisson arrivals."** It needs stationarity (or a window that starts and ends empty), nothing else. The check used non-Markov arrivals and log-normal service.
- **"The tail formula assumes independence, so it is useless."** The union bound holds for any dependence. Correlation (a shared GC pause) moves the true value *towards* max p_i, and independence is the pessimistic case.
- **"More nodes always help a bit."** Not with coherency costs. Past p*, the USL says throughput falls. Reduce κ instead: shard, avoid broadcast invalidation, keep coordination off the hot path.
- **"ρ ≥ 1 just means a long queue."** It means *no* steady state. The queue grows without bound until something sheds load or times out.

## Further reading
Little & Graves 2008, chapter 5. Dean & Barroso, *The Tail at Scale* (CACM 2013). Gunther 2008 (arXiv:0808.1431) on USL and Amdahl as queueing bounds. Amdahl 1967.
