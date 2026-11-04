**Concept: warm-up, replications and confidence intervals**

## Why it matters
An IT help desk opens on Monday with 30 weekend tickets waiting. You want the long-run mean wait at 80% load. Keep the backlog in the averages and 40 runs of 1,000 customers give 5.59 ± 0.61 min. The truth is 4.0. The interval is tight, and it is wrong.

## Mental model
A simulation starts in a state you chose, not the one you want to study, like a cold kettle. Discard the heating-up part, then repeat with fresh random numbers to measure how sure you are.

```
wait │█▇▅▃▂_ ~ ~ ~ ~  steady state
     │     ↑ warm-up d
rep 1..n: mean after d ─> Ȳ ± t·s/√n
```

## How it works
1. **Initial bias.** An empty or backlogged start is unusual, so early outputs aren't typical → see lab step 3.
2. **Welch's method.** Run R ≥ 5 replications. Average them point by point, smooth with a moving average (window ≤ T/4), and find where the curve flattens. The lab's code proposes a point; you confirm it on the curve → see lab step 2.
3. **Delete, then replicate.** Drop the first d observations of every run. Each run's mean is one independent observation → see lab step 3.
4. **Confidence interval.** Ȳ ± t(0.975, n−1)·s/√n. Width falls like 1/√n, so halving it costs 4× the runs → see lab step 4.

**Worked example (lab run):** the Welch curve reads 29.19 at customer 0, 8.69 at 100 and 3.39 at 200, and the code proposes d = 169. With replications of 5,000 customers, the half-width shrinks from 0.50 (n = 10) to 0.16 (n = 80). That ratio of 3.13 compares with √8 = 2.83.

## Trade-offs
| Method | Use when | Avoid when |
|---|---|---|
| Replication/deletion | Cheap runs, parallel cores, clear warm-up | Warm-up is most of each run |
| One long run + batch means | Warm-up is expensive | Batches too short to be near-independent |
| Terminating analysis | The transient is the question ("Monday 9am") | You want steady state |

## Common mistakes
- Treating thousands of autocorrelated waits from one run as independent data. The CI comes out far too narrow.
- Choosing the warm-up from one noisy run. Over-deleting is cheap: d = 961 instead of 169 moved the mean by only 0.03.
- Fixing n without checking the half-width against the precision you need.
