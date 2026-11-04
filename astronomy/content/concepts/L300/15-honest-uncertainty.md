**Concept: honest uncertainty - when the error bar matters more than the best fit**

## Why it matters
A planet's radius comes from the transit depth, and its error bar decides whether it is "Earth-like" or "mini-Neptune". Fitting software always returns a number and a ±. If the pipeline's per-point errors are too small (a common, realistic case: scintillation and systematics are left out), the ± shrinks while the fit stays the same. Then every downstream claim is overconfident, and nothing crashes to warn you.

## Mental model
An error bar is a promise: "the truth lies inside ±1σ about 68 % of the time". You can check a promise by simulating many datasets with known truth and counting.

```
truth --(noise, seed k)--> data_k --fit--> p_k +/- s_k        k = 1..200
coverage = fraction of k with |p_k - truth| <= s_k     honest ~ 0.68
```

## How it works
1. **Least squares.** Levenberg–Marquardt minimises χ² = Σ((y − model)/σ)² with damped Gauss–Newton steps. The model is a trapezoid (flat bottom between 2nd and 3rd contact, Seager & Mallén-Ornelas 2003) → see lab step 2.
2. **Formal errors.** cov = (JᵀWJ)⁻¹ with W = 1/σ². This is correct **only if** σ is right and the model is nearly linear near the minimum → see lab step 2.
3. **The residuals know σ.** χ²_red = χ²/(n − p) should be about 1. If it is 4.13, the true σ is about 2.03 × the reported one; scale the covariance by χ²_red → see lab step 5.
4. **Bootstrap.** Refit the best model plus resampled residuals 300 times. The spread of the refits is an error bar that needs no σ → see lab step 3.
5. **MCMC with a noise parameter.** Sample the posterior including a noise scale s (σ = s × flux_err) with Metropolis. Check the acceptance (0.2–0.5) and the autocorrelation time τ; the emcee docs suggest chains longer than about 50τ → see lab step 6.

**Worked example (lab run):** with flux_err = 0.0010 (true scatter 0.0020) the formal σ(t0) is 0.0060 h, the bootstrap gives 0.0128 h, and the coverage is t0 0.36, depth 0.335, T14 0.275, T12 0.22. After χ²_red scaling, σ(t0) is 0.0122 h and the coverage is 0.73 / 0.615 / 0.555 / 0.56. MCMC finds s = 2.035 ± 0.09 and T14 −0.089/+0.071 h, wider and asymmetric where the linear error was ±0.052 h.

## Failure modes
- **Trusting reported errors.** The coverage collapses while the fits look perfect. The tell is χ²_red far from 1.
- **Nonlinear parameters.** Even with the right σ, linearised errors under-cover T14 and T12 (0.555 / 0.56) because the trapezoid has kinks. Use MCMC or a bootstrap, and quote percentiles.
- **Short chains.** 1000 steps give chain/τ = 32. The numbers look plausible, but they are not converged.
- **Correlated (red) noise.** Neither χ² scaling nor a residual bootstrap captures it; time-correlated noise needs its own model.

## Common mistakes
- Quoting ± from (JᵀWJ)⁻¹ without looking at χ²_red.
- Shrinking errors when χ²_red < 1 (the lab uses max(χ²_red, 1)).
- Writing "median ± σ" for an asymmetric posterior (the stretch flags T14 and T12).
