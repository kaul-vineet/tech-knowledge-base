**Concept: (s, S) inventory policies and common random numbers**

## Why it matters
A bike shop must decide when, and how many, inner tubes to reorder. Too rarely and customers walk out; too often and fees and shelf space eat the margin. Two candidate policies differ by cents a day, and independent runs are noisier than that.

## Mental model
For a fair comparison, give both policies the same year: the same sunny weeks, customers and supplier delays. Any remaining difference comes from the policy.

```
streams(rep): weather+demand ─┬─> policy A (30, 80) ─┐
              lead times ─────┘─> policy B (30, 90) ─┴─> per-rep difference -> CI
```

## How it works
1. **(s, S) rule.** Each evening, compute the inventory position (on hand plus on order). If it is ≤ s, order up to S. The order arrives after a random lead time → see lab step 1.
2. **Cost trade-off.** Cost is holding + ordering + lost sales. Raising s or S cuts lost sales but adds holding cost → see lab step 2.
3. **Common random numbers (CRN).** Run both policies on identical inputs; analyse per-replication differences. Var(A−B) = Var A + Var B − 2·Cov, so positive covariance shrinks it → see lab step 3.
4. **Synchronise by purpose.** Use one stream per random input (`default_rng([rep, purpose])`), drawn up front. An extra order in one policy then can't shift the other's demand → see lab step 4.

**Worked example (lab run):** under CRN the two policies' costs correlate at 0.90 across 30 replications. S=90 minus S=80 is −0.25 ± 0.12 per day with CRN, so S=90 is cheaper. With independent runs it is +0.03 ± 0.44, and you can't tell. Matching CRN's width without it would take about (0.44/0.12)² ≈ 14× the replications.

## Trade-offs
| Choice | Use when | Avoid when |
|---|---|---|
| CRN paired comparison | Similar designs, same model | The designs consume random numbers incompatibly |
| Independent runs | One system's absolute performance | Detecting small differences |
| Lost sales vs backorders | Lost: retail walk-outs. Backorders: customers who wait | Mixing both in one cost model |

## Common mistakes
- Drawing everything from one generator during the run. In the lab's tryIt this widened the interval from ±0.12 to ±0.31.
- Triggering orders on on-hand stock and ignoring stock already on order, which causes double orders.
- Comparing two overlapping CIs instead of one paired-difference CI.
