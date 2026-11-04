**Concept: Monte Carlo estimation**

## Why it matters
A release has three tasks with fuzzy estimates. Adding the "most likely" values gives 15 days, but the manager asks: "How likely are we to finish within 20?" One number cannot answer that; a distribution can.

## Mental model
Play the project thousands of times with dice loaded by your estimates, then count how often you finish in time.

```
sample inputs ──> model (sum) ──> outcome
   x N times                         │
                     histogram <─────┘ ──> mean ± CI, P(≤20), P90
```

## How it works
1. **Sample every uncertain input** from its distribution (triangular min/mode/max) and run the model once per sample. Here: exact mean 17.333 days, sampled mean 17.334 at N=100,000 → see lab step 2.
2. **Quantify precision:** a 95% confidence interval is mean ± 1.96·s/√N. Error falls like 1/√N: half-widths 0.436, 0.150, 0.047, 0.015 for N = 100 to 100,000 → see lab step 3.
3. **Answer with probabilities and percentiles,** not just the mean: P(≤20 days) = 0.857, P90 = 20.56 days → see lab step 4.

## Common mistakes
- Quoting a result from N=100 without its interval.
- Adding most-likely values: skewed tasks make the real mean (17.3) larger than 4+8+3 = 15.
- Trusting precise output from guessed input ranges; the interval covers sampling error, not wrong inputs.
