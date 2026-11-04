**Concept: resources and multi-server queues**

## Why it matters
A clinic reception has three desks and patients arrive at 2.4 per minute. Is a fourth desk worth paying for? "80% busy" doesn't say how long people wait. A model with c servers sharing one line does, and the Erlang C formula lets you check it.

## Mental model
A resource is a pool of identical tokens. A patient takes a desk token if one is free, otherwise joins one FIFO line, and hands the token straight to whoever is first in line when done.

```
arrivals ──> [ line: ● ● ● ] ──> desk 1 ─┐
                               ──> desk 2 ─┼──> leave   (busy <= c)
                               ──> desk 3 ─┘
```

## How it works
1. **Acquire or queue.** On arrival, if busy < c, take a desk and schedule a departure. Otherwise join the line → see lab step 2.
2. **Release hands over.** On departure the desk passes to the next in line, whose wait is now minus their arrival time → see lab step 2.
3. **Time-weighted averages.** Queue length and utilisation are areas under step curves: at each event add len(line) × (time since the last event), then divide by total time → see lab step 3.
4. **Check, then use.** With offered load a = λ/μ and ρ = a/c, Erlang C gives P(wait). Then Wq = P(wait)/(cμ − λ) and Lq = λWq (Little's law) → see lab steps 2 and 4.

**Worked example (lab run):** a = 2.4, c = 3 gives P(wait) = 0.647, Wq = 0.647/(3 − 2.4) = 1.079 min and Lq = 2.4 × 1.079 = 2.589. The simulation gives 1.110 min and 2.665, and 2.665 ≈ 2.4 × 1.110 passes Little's law too. With five desks, P(wait) drops to 0.114.

## Trade-offs
| Choice | Use when | Avoid when |
|---|---|---|
| Erlang C | Poisson arrivals, exponential service, one line, steady state | Peaks, breaks, abandonment |
| Heap simulation | Custom rules, no dependencies | Many interacting resources |
| SimPy `Resource` | Several resources, priorities, readable processes | You need instant closed-form sweeps |

## Common mistakes
- Separate lines per desk. Pooling them cut the mean wait from 3.87 to 1.11 min in the lab.
- Averaging queue length per event instead of per unit of time.
- Reading 80% utilisation as plenty of spare capacity. 10% more patients raised Wq from 1.08 to 2.17 min.
