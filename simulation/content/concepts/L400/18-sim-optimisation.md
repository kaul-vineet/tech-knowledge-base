**Concept: simulation-based optimisation under a fixed budget (search, ranking & selection, common random numbers)**

## Why it matters
You can simulate a policy. The question is which policy to run. A bike shop's (s, Q) reorder policy has 81 sensible settings, and each simulated half-year costs one run. The answer is noisy and the budget is fixed. Search hard and the winner looks cheaper than it is, because you picked the luckiest noise (the "winner's curse"). Compare optimisers on unequal budgets and you learn nothing about the optimisers.

## Mental model
Two jobs share one budget: **search** (where to look) and **selection** (which candidate is really best).

```
budget B = 324 runs, same streams for every design (CRN)
 +---------------- search: B - reserve ----------------+-- selection: reserve --+
 grid / GP-lite + EI / (mu+lambda)-ES  -> top 5 designs  -> OCBA on FRESH streams -> pick + honest estimate
```
Fu, Chen & Shi (WSC 2008) describe this trade-off as allocating effort between "searching the solution space versus conducting additional simulation replications". The OCBA rule they give gives a non-best design i runs in proportion to s_i²/(J_b − J_i)². The best design gets N_b = s_b·√Σ(N_i/s_i)².

## Design space
- **Grid search.** Equal replications for all 81 designs. Simple, embarrassingly parallel, and exhaustive. Its cost is (levels)^dimensions.
- **Surrogate-guided (GP-lite + expected improvement).** Fit a Gaussian process to the noisy means and simulate where expected improvement (Jones, Schonlau & Welch 1998) is highest. Revisits add replications. It pays off when runs are expensive and the response is smooth.
- **Evolution strategy, (μ + λ).** Parents mutate on the grid and the best μ of parents plus children survive. It is robust to ugly landscapes and needs no model, but it has no guarantees.
- **Selection stage (for all three).** Re-run the top 5 on *fresh* common random numbers with OCBA, from a reserve of 60 runs inside the same budget. Report that estimate, not the search estimate.

## How to decide
Criteria: the optimality gap against a referee (`truth.json`: 100 replications per design on streams no optimiser sees), the worst gap across 5 macro-replications, the bias of the reported cost, and **identical budgets**.

**Worked example (lab run, budget 324).** Without the selection stage, the mean/worst gaps were grid 0.049/0.117, surrogate 0.277/1.085 and evolution 0.052/0.145 per day. The reported cost was 0.30-0.47/day too optimistic. With the OCBA stage (reserve 60), they were grid 0.042/0.088, surrogate 0.090/0.186 and evolution 0.088/0.241. Over 12 macro-replications, the grid's reported-minus-true bias moved from -0.394 to -0.143. The referee has its own standard error (0.085, shared by all designs because truth.json uses CRN), so -0.143 is within 2 referee SEs and -0.394 is not. Turning common random numbers off raised the grid's mean gap from 0.042 to 0.200. Giving evolution twice the budget "improved" it to 0.008: that is an unfair comparison, not a better method. Decision (ADR 0001): grid + OCBA for this 2-D, 81-design problem. `test_fitness.py` enforces budget fairness, a worst gap at most the indifference zone δ = 0.10/day, and an absolute bias of at most 0.15 over 12 macro-replications.

The indifference zone (Kim & Nelson 2001) is the smallest difference that matters to the business. Cost gaps below 0.10/day are not worth a decision, so the selection only has to be right to within δ.

## Failure modes at scale
- **Dimensions grow:** a grid over 5 parameters at 9 levels is 59,049 designs. Grid search is out, and a surrogate or evolution strategy is needed. The signal is a budget smaller than the design count.
- **Noisy expected improvement:** EI treats the luckiest noisy mean as the incumbent and keeps exploiting it. The surrogate's worst case here was a 1.085/day gap. Use replications or a noise-aware incumbent.
- **Correlated selection:** OCBA assumes independent normal outputs, and CRN breaks the independence. It still works here, but the claimed P(correct selection) is approximate.
- **Simulation time varies by design:** "equal runs" is then not "equal budget". Count seconds instead.

## Common mistakes
- Reporting the winner's search-phase mean as its expected cost.
- Comparing optimisers that consumed different budgets or different random numbers.
- Choosing δ after looking at the results.
