**Concept: input modelling**

## Why it matters
You timed 200 bike-shop repairs and need service times for a queue model. Pick "exponential" because the textbook did, and the model overstates waits by about a quarter at every load. Choose the input distribution with evidence.

## Mental model
Tailoring: measure, cut a few standard patterns to size, then check each one against the body.

```
data ──fit──> exponential / normal / lognormal (parameters)
  └──── compare: KS distance D, Q-Q points ──> pick ──> simulation
```

## How it works
1. **Fit parameters** with closed-form estimators. For the exponential, rate = 1/mean (MLE = method of moments). For the lognormal, MLE gives μ and σ as the mean and standard deviation of log(data) → see lab step 2.
2. **Measure the gap.** The Kolmogorov–Smirnov D is the largest vertical distance between the data's step-shaped empirical CDF and the fitted CDF, checked on both sides of each step → see lab step 3.
3. **Look at the shape.** A Q-Q check puts fitted and data quantiles side by side. A good fit lines up; tails show problems first → see lab step 4.
4. **Check the consequence.** Feed each candidate into the same queue; compare with resampling the data → see lab step 5.

**Worked example (lab run):** n = 200, so 1.36/√200 = 0.096. D is 0.217 for the exponential, 0.132 for the normal and 0.031 for the lognormal. The data's cv is 0.73. The Pollaczek–Khinchine mean wait grows with 1 + cv², so the exponential (cv = 1) predicts (1+1)/(1+0.73²) = 1.31× the wait. Simulated: 1.25× at 50%, 70% and 85% load.

## Trade-offs
| Approach | Use when | Avoid when |
|---|---|---|
| Fitted distribution | Enough data, a family that matches the physics (positive, skewed) | Few points, several families fit equally |
| Resample the data | Plenty of data, only seen values needed | Rare long tails matter |
| Exponential by default | Truly independent arrivals (calls, requests) | Service times with a minimum or a hump |

## Common mistakes
- Using 1.36/√n as a real test after fitting the parameters from the same data. NIST: that critical region is then invalid, so rank by D.
- Fitting a normal to positive times and clipping the negatives. Clipping shifts the mean, and so the load.
- Checking only the mean: waits depend on variance, tail risk on shape.
