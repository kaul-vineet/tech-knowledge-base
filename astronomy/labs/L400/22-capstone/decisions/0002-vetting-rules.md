# 2. Vet candidates with deterministic rules: SNR ≥ 10, SDE ≥ 7, ≥ 2 transits, odd/even and secondary at 3σ, duration

## Status
Accepted (2026-10-29)

## Context
BLS reports the strongest box-shaped dip in every light curve, including noise, starspots and eclipsing binaries. Kovács et al. (2002) suggest SDE > 6 for a significant detection, and the Kepler DR25 Robovetter (Thompson et al. 2018) groups false positives into categories, eclipsing binaries among them. On this sector:
- Quiet stars and the ramp star peak at SNR 4.5–5.6 and SDE 3.6–4.8. The spotted rotator S06 peaks at SNR 14.27 but SDE 5.07, with a single "transit" at 13.8 d.
- The planets reach SNR 44–126 and SDE 8.7–9.6.
- S04 (EB) shows a secondary eclipse at phase 0.5 of 5217 ppm. S05 (EB at twice the BLS period) has alternate depths of 5937 and 11603 ppm.

## Decision
A candidate is `planet_candidate` only if all of these hold:
- SNR ≥ 10 and SDE ≥ 7;
- at least 2 distinct transit epochs carry data;
- the odd and even depths agree within 3σ;
- there is no secondary eclipse deeper than 3σ at phase 0.5;
- T14 ≤ 1.5 × 13 h × (P / 1 yr)^(1/3) (a Sun-like star). The bound is **derived, not quoted**: a central transit on a circular orbit lasts T14 ≈ (P/π)(R★/a), the small-angle limit of Seager & Mallén-Ornelas (2003) with b = 0 and Rp ≪ R★. Kepler's third law for 1 M☉ gives a = 1 au × (P / 1 yr)^(2/3). With R☉/au = 0.00465, T14 ≈ (8766 h / π) × 0.00465 × (P / 1 yr)^(1/3) = 13.0 h × (P / 1 yr)^(1/3). A central transit is the longest possible, so this is an upper bound; the ×1.5 margin covers larger stars and eccentric orbits.

Every failed rule is recorded as a reason.

## Consequences
- On this sector: 3/3 planets kept, 0/9 false positives. Without the odd/even rule, S05 would be published as a planet (tryIt 2).
- The duration rule assumes a Sun-like host. Giants or M dwarfs need the stellar radius and density from a catalogue (for example the TESS Input Catalog).
- Single-transit planets (P > half the sector) are rejected by design and need another route.
- Thresholds are tuned on synthetic data. Real sectors have scattered light and momentum dumps, so re-measure the false-positive rate with injection tests before trusting it.
- Fitness: `test_fitness.py::test_no_false_positives` and `test_recovery`.
