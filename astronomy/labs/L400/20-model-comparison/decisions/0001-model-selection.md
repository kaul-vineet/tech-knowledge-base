# 1. Select the published mass model by BIC, then require structure-free residuals

## Status
Accepted (2026-10-29)

## Context
We publish one mass model for a disk galaxy's rotation curve: 40 radii from 1 to 30 kpc, with errors of 2–6 km/s. The data are synthetic, shaped like NGC 3198 (Begeman 1989); the truth is a disk plus a cored halo. There are four candidates:
- disk only (k = 1);
- disk + cored halo (k = 3);
- disk + NFW halo (k = 3);
- disk + cored halo + a cubic "wiggle" term (k = 6).

Constraints: the rule must pick a physical, minimal model, must not reward flexibility, must be reproducible from the data alone, and must flag fits whose residuals show structure.

`compare.py` measured three selection rules on 50 seeded galaxies:
- A, lowest χ²: wiggles 50/50. On the published curve, χ² is 3267.95 / 43.24 / 67.83 / 40.63, so the wiggles win by 2.6.
- B, BIC = χ² + k ln n: disk + cored halo 50/50. On the published curve, BIC is 3271.64 / 54.30 / 78.90 / 62.76.
- C, hold-out of the outer radii (fit R ≤ 20 kpc, score R > 20): cored halo 43, NFW 5, wiggles 2.

## Decision
Use B, BIC (Schwarz 1978), and publish AIC beside it. Then require the chosen model's residuals to pass the Wald–Wolfowitz runs test (|Z| < 1.96, NIST e-Handbook). Disk only fails it (Z = −6.05); the cored halo passes (Z = −1.27).

## Consequences
- Each extra parameter must reduce χ² by ln 40 ≈ 3.7. The wiggle term buys only 2.6, so it is rejected. If the true halo is NFW, BIC switches to NFW (tryIt 1: BIC 47.84 against 74.95).
- BIC assumes the errors are right. Underestimated errors inflate χ² differences and favour complex models (see lesson 15: check χ²_red).
- C uses less data and depends on where the cut falls; it is kept as a robustness check, not the rule.
- Disk–halo degeneracy: with only R ≤ 8 kpc (an optical curve), a halo still wins, but the disk mass-to-light ratio moves from 1.087 to 1.19. Publish M/L only with its uncertainty, or fix it from stellar-population models.
- The data are synthetic. The real SPARC NGC 3198 file has no stated licence, so it is not vendored (KNOWN-GAPS).
- Fitness function: `test_fitness.py` requires a halo model in at least 95 % of 50 galaxies, never the wiggles, published residuals with |Z| < 1.96, and disk only rejected.
