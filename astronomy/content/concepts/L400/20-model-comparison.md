**Concept: model comparison - choosing between physical models without rewarding flexibility**

## Why it matters
Galaxy rotation curves are where the evidence for dark matter became hard to ignore. Stars and gas alone predict velocities that fall with radius; observed curves stay flat. NGC 3198 stays flat within 5 km/s out to 11 disk scale lengths (Begeman 1989). Whether you need a halo, and which shape, is a model-selection question, and the same question appears whenever you choose between explanations of data. If the rule is "smallest χ²", the most flexible model always wins, and you publish wiggles as physics.

## Mental model
Every model gets a fit, and every parameter must pay rent. The data decide how much improvement a parameter has to buy.

```
V_obs(R) +/- err ---> disk only        (k=1)  chi2 3267.95  BIC 3271.64   residual runs Z -6.05
                 ---> disk + cored halo(k=3)  chi2   43.24  BIC   54.30   Z -1.27   <- published
                 ---> disk + NFW halo  (k=3)  chi2   67.83  BIC   78.90
                 ---> halo + wiggles   (k=6)  chi2   40.63  BIC   62.76   (lowest chi2!)
```

## Design space
- **Mass models.** An exponential disk (Freeman 1970: V² = 2GM_d/R_d · y²[I0K0 − I1K1], y = R/2R_d) with a free mass-to-light ratio. A cored halo ρ0/(1 + (r/rc)²), whose closed-form velocity follows by integrating the density. NFW (1996, eq. 5) with V200 = 10 H r200. Every curve here comes from code that the tests check against a numerical mass integral and tabulated Bessel values.
- **Selection rules.** Lowest χ² ignores complexity. AIC = χ² + 2k and BIC = χ² + k ln n (Schwarz 1978) penalise parameters; with n = 40, BIC charges ln 40 ≈ 3.7 per parameter. Holding out the outer radii tests extrapolation directly but uses less data and depends on the cut.
- **Residual diagnostics.** A good χ² can hide structure. The Wald–Wolfowitz runs test (NIST e-Handbook) counts sign runs in the residuals: |Z| > 1.96 means systematic misfit.

## How to decide
State what a published model must satisfy: it must be physical, minimal, chosen reproducibly from the data, and leave residuals without structure. Then test the rules on many synthetic galaxies whose truth you know, not on the one galaxy you care about.

**Worked example (lab run, 50 seeded galaxies, truth = disk + cored halo):**
- Lowest χ² picked the wiggles model 50/50. On the published curve it wins by 2.6 in χ², with an absurd halo (ρ0 16.35 × 10⁷ M☉/kpc³, rc 1.7 kpc).
- BIC picked the cored halo 50/50.
- The hold-out of R > 20 kpc picked the cored halo 43 times, NFW 5 and wiggles 2.
- The chosen fit has runs Z = −1.27; disk only has Z = −6.05 and is rejected.
- When the data are generated from NFW instead, BIC switches to NFW (47.84 against 74.95).

ADR 0001 records BIC plus the runs test; `test_fitness.py` keeps it true.

## Failure modes at scale
- **Wrong error bars:** BIC differences scale with 1/σ². Underestimated errors (lesson 15) make every extra parameter look worth it. Check χ²_red first.
- **Degeneracies:** with only R ≤ 8 kpc, a halo still wins, but the disk mass-to-light ratio moves from 1.087 to 1.19 (tryIt 2). The "maximum disk" ambiguity is real, so report M/L with its uncertainty.
- **Many galaxies, many models:** with hundreds of galaxies, selecting per galaxy multiplies false choices. Use hierarchical models or a fixed physical prior.
- **Non-Gaussian systematics:** non-circular motions, warps and distance errors produce residual patterns no halo model fixes. The runs test flags them; a model will not.

## Common mistakes
- Reporting R² or χ² alone as the reason to prefer a model.
- Treating AIC and BIC as interchangeable: AIC penalises 2 per parameter, BIC ln n. With large n, BIC is much stricter.
- Using real survey data whose licence you have not checked. SPARC's page states none, so this lab is synthetic, and the real path is manual.
