# 3. Two-state Markov cloud model and the all-or-nothing completion rule

## Status
Accepted (2026-10-30)

## Context
Promises to observers ("your target will be observed") are only honest if they include weather. Independent
per-slot clouds understate spells; real cloud cover persists. A two-state Markov chain (clear/cloudy) is the
simplest model with persistence (Gabriel & Neumann 1962 used it for daily rain occurrence).

## Decision
- 10-min steps; P(clear -> cloudy) = 0.04, P(cloudy -> clear) = 0.20 (assumed, not fitted: stationary clear
  fraction 0.833, mean clear spell 250 min, mean cloud spell 50 min); the night starts in the stationary state.
- A block counts only if every one of its slots is clear (time-series blocks cannot be stitched).
- Promise = analytic p_complete(n) = pi_clear (1 - a)^(n-1); the Monte Carlo (1000 runs, SeedSequence child per run,
  common random numbers for both plans) must reproduce it within 3 binomial standard errors per block.

## Consequences
- Expected value, not nominal value, is what the scheduler reports; long blocks show low completion odds.
- The parameters must be fitted to site records before use (scaling limit); the code takes a and b as arguments.
- Stitchable exposures (partial credit) would change the objective; not modelled here.
