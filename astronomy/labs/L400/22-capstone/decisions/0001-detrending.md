# 1. Detrend with a 0.75-day running median, then re-detrend with the candidate's transits masked

## Status
Accepted (2026-10-29)

## Context
The light curves carry a slow instrumental drift (0.15 %, 11 d), a starspot modulation on S06 (0.8 %, 4.5 d) and a post-gap ramp on S07 (0.2 %, 0.5 d decay). Transits last 2.6–4.2 h. Detrending must flatten the slow signals and keep the transit depth, because the depth sets the planet's radius. Measured on this seeded sector:
- A running median over 0.25 d eats the transits. S03's BLS depth falls from 4834 to 726 ppm and its SNR from 43.96 to 6.69 (tryIt 1), which is below the 10 detection threshold.
- A running median over 0.75 d, unmasked: periods within 0.05 %, and the quiet stars' rms within 3 % of the injected noise. The MCMC depth of S02 is 2798 ± 72 ppm against an injected 3000 (−2.8σ): the median still includes in-transit points.
- 0.75 d with the in-transit points (1.5 × T14) masked on a second pass: S01 8169 ± 76, S02 2940 ± 63, S03 5096 ± 107 ppm (+2.2σ, −0.95σ, +0.9σ).

## Decision
Search on the 0.75 d running-median light curve. For each candidate, re-detrend the raw flux with its in-transit points excluded from the median, then vet and fit on that curve.

## Consequences
- The window must stay several times longer than the longest transit sought (4.5 h boxes). Longer transits, such as long-period planets around large stars, need a longer window or a spline with masking.
- A 0.75 d window passes rotation periods shorter than a day. Fast rotators would need a different detrender (a Gaussian process, or lightkurve's `flatten` Savitzky–Golay in CI).
- Masking needs a first detection, so a transit too shallow to be found unmasked stays unfound. Iterative search is a follow-up.
- Fitness: `test_fitness.py` (recovery, depths within 3σ) and M1 (quiet-star rms / noise within 15 %).
