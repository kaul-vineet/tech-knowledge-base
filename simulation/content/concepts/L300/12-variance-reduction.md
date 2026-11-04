**Concept: variance reduction (antithetic variates, control variates, common random numbers)**

## Why it matters
A warehouse wants the expected overtime of a picking shift. Plain Monte Carlo error shrinks only like 1/√n, so halving it costs four times the runs. Variance reduction changes the estimator instead of the run count: the same answer, unbiased, with a smaller variance per model evaluation. In models that take minutes per run, that is the difference between an overnight batch and a coffee break.

## Mental model
Same question, smarter sampling. Pair each random draw with its mirror image, or subtract a quantity whose error you already know.

```
plain:       f(u1)  f(u2)  f(u3) ...          error ~ σ/√n
antithetic: [f(u) + f(1-u)]/2 per pair        errors cancel if ρ < 0
control:     Y - β(C - E[C])                  C known exactly -> remove its noise
CRN:         f_A(u) - f_B(u), same u          shared noise cancels in the difference
```

## How it works
1. **Measure cost-fairly.** Compare variance per model evaluation, not per estimate; the ratio says how many plain runs one method run is worth → see lab step 1.
2. **Antithetic variates.** Evaluate f(u) and f(1−u) with the same u. Variance is σ²(1+ρ)/n with ρ = Corr(f(u), f(1−u)). Monotone models give ρ < 0; symmetric models can give ρ = +1 and double the variance → see lab step 2.
3. **Control variates.** Pick an output C with known mean (total task time, mean 7.2 h). Use β = Cov(Y,C)/Var(C). The gain is 1/(1−r²), where r = Corr(Y,C) → see lab step 3.
4. **Stream discipline.** Antithetic pairs need one stream per pair. Reseeding per evaluation silently turns the mirror into an independent draw → see lab step 4.
5. **Common random numbers.** For a difference between two designs, feed both the same u so the noise cancels (L200 #11) → see lab step 5.
6. **Choose by pilot.** A small pilot measures ρ and r before you commit, and logs the decision → see lab step 8.

**Worked example (lab run, 20,000 evaluations):** exact overtime is 0.9196 h. Antithetic pairs have ρ = −0.32, so theory predicts 1/(1−0.32) = 1.48× and the lab measures 1.46×. Total time correlates with overtime at r = 0.90, so the control variate gives 1/(1−0.90²) = 5.40×. Its 20,000 runs are worth about 108,000 plain runs. The 30-minute-longer shift saves 0.2120 ± 0.0259 h with independent streams and 0.2237 ± 0.0033 h with CRN.

## Failure modes
- **Broken pairing.** Nothing crashes and the estimate stays unbiased. Only the gain vanishes: ρ = −0.00 and 1.01×. You notice only if you log ρ and the variance ratio.
- **Antithetic on a symmetric model.** ρ = +1 and the ratio drops to 0.49×, so you pay twice for nothing (tryIt 1).
- **Bad β.** A guessed β = 1.5 gives 0.52×, which is worse than plain (tryIt 2).
- **Wrong standard error.** Treating the 2n antithetic values as independent misstates the CI. Analyse pair averages.

## Common mistakes
- Reporting "variance reduced" without a ratio at equal cost against plain Monte Carlo.
- Reusing per-replication seeding (right for independent replications) inside an antithetic pair.
- Picking a control variate whose mean is estimated, not known exactly. That adds the noise back.
