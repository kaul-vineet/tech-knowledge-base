**Concept: the capstone - an exoplanet transit search from light curves to a vetted, explained report**

## Overview
This is a TESS-style search on one simulated sector: twelve stars, 27 days at a 10-minute cadence, a mid-sector gap, an instrumental drift and photon noise. Three stars host transiting planets. The rest are traps: two eclipsing binaries, a spotted star, a post-gap ramp and five quiet stars. The job is the real one: find the periodic dips, reject the impostors with reasons, measure the survivors with honest uncertainties, keep a provenance trail, and let a local model explain the results without letting it decide anything. `run_capstone.py` prints one scorecard line per milestone; the run here gives PASS 6/6.

## Architecture walkthrough
```
S01..S12.csv --> detrend (0.75 d running median) --> BLS-lite (6000 freqs x 4 durations; SNR, SDE)
   --> re-detrend with the candidate's transits masked --> vet (code decides) --> fit (trapezoid + MCMC)
   --> prov.jsonl (SHA-256 of inputs + parameters) --> agent explains behind a gate --> scorecard.jsonl
```
1. **Detrend.** A running median follows drift, spots and ramps; quiet-star rms lands within 3 % of the injected noise. A 0.25-day window would eat a 4.2-hour transit (S03 SNR 43.96 → 6.69), so the window is an ADR, not a default.
2. **Search.** Box least squares (Kovács et al. 2002) folds at each trial period, bins the phase and slides boxes. Periods of all three planets come back within 0.05 %.
3. **Vet.** The rules are SNR ≥ 10, SDE ≥ 7, at least two transits, odd and even depths equal within 3σ, no secondary eclipse at phase 0.5, and a duration plausible for a Sun-like star. S04 is rejected for a 5217 ppm secondary, and S05 because alternate eclipses are 5937 and 11603 ppm deep. With the odd/even rule switched off, S05 would be published as a planet.
4. **Fit.** The lesson 15 trapezoid and Metropolis sampler, imported rather than copied, run on the folded transit with a free noise scale. Depths are 8169 ± 76, 2940 ± 63 and 5096 ± 107 ppm against injected 8000, 3000 and 5000: within 3σ. Masking the transit before re-detrending removed a −2.8σ depth bias.
5. **Provenance.** Each input's SHA-256 and the search parameters are recorded (lesson 16), and a rerun reproduces the period exactly.
6. **Explain.** The fake model calls every candidate a planet and invents "1.8 Earth radii". All six explanations are blocked; no verdict changes.

## How it ties L100–L400
- Time and coordinates (lessons 2–3) underlie every timestamp and sky position.
- Magnitudes and flux (lesson 4) define depth in ppm.
- Kepler's laws (lesson 5) give the duration bound.
- Light curves and Lomb–Scargle (lesson 10) lead to BLS.
- Calibration (lesson 13) explains why the flux is trustworthy.
- Honest uncertainty (lesson 15) supplies the fitter.
- Provenance (lesson 16) supplies the trail.
- The survey architecture (lesson 17) sets the stage boundaries.
- The alert broker (lesson 18) supplies the agent gate pattern.
- Open-data practice (lesson 21) governs using real TESS data: `fetch_tess.py` runs the same search on π Mensae in CI and should recover the published 6.27-day period.
