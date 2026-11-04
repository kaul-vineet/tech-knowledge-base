# Final examination — week 14 (lessons 1–27, L100–L500)

**Time:** 3 hours. **Total:** 100 marks. **Allowed:** one A4 sheet of notes and a scientific calculator; no network.
**Constants:** GM☉ = 1.3271244 × 10²⁰ m³ s⁻²; R☉ = 6.957 × 10⁸ m; 1 au = 1.495978707 × 10¹¹ m; 1 Mpc = 3.0857 × 10¹⁹ km; G = 6.67408 × 10⁻¹¹ (SI); Julian year.
Model-answer numbers come from the course's verified code (lab outputs, `research/l500_checks.py`, `research/qbank_checks.py`).

---

### Q1 — Derivation (12 marks)
A planet with negligible mass transits a Sun-like star (radius R☉) on a circular, edge-on orbit of period P.
(a) Using Kepler's third law, show that the full transit duration is approximately T ≈ P R☉ / (π a), and hence T ≈ 13 h × (P/1 yr)^(1/3). (8)
(b) Evaluate it for P = 6.27 d. (4)

**Model answer.**
(a) The planet crosses a chord of length about 2R☉ (central transit, R_p ≪ R☉) at orbital speed v = 2πa/P. So T ≈ 2R☉/v = P R☉/(π a). Kepler III gives a ∝ P^(2/3), so T ∝ P^(1/3). Normalise at P = 1 yr, a = 1 au: T = 365.25 × 24 h × 0.0046505/π = **12.98 h**. Hence T ≈ 13 h (P/yr)^(1/3), the bound used in the capstone.
(b) 12.98 × (6.27/365.25)^(1/3) = **3.35 h**. (The capstone's search window uses 1.5 × this bound: 5.03 h.)
*Marks:* (a) 3 chord-and-speed, 3 Kepler III, 2 normalisation; (b) 4.

### Q2 — Short explanation (10 marks)
In lesson 15 the reduced χ² was 4.13 with the pipeline's quoted errors, and the 1σ coverage of t₀ was only 0.36. Explain what both numbers mean, what the minimum fix is, and what it does not fix.

**Model answer.**
- χ²_red ≈ 1 if the errors are right. A value of 4.13 means the real scatter is about √4.13 = **2.03 ×** the quoted σ.
- Coverage 0.36, against an expected 0.68, means the stated ±1σ contains the truth only 36 % of the time: the error bars are overconfident.
- Minimum fix: scale the covariance by max(χ²_red, 1), or fit a noise-scale parameter (MCMC gives s = 2.035).
- What it does not fix: nonlinear parameters (T14, T12) still under-cover with linearised errors, and correlated (red) noise is not captured. Use posterior percentiles or a noise model.
*Marks:* meaning of each number 3 + 3; fix 2; limits 2.

### Q3 — Proof (12 marks)
(a) Prove that the Metropolis–Hastings kernel satisfies detailed balance with respect to π and hence leaves π stationary. (8)
(b) Explain, with the course's numerical evidence, what goes wrong if the Hastings factor is omitted for an asymmetric proposal. (4)

**Model answer.**
(a) As in lesson 25, theorem 3. π(x)K(x, y) = min(π(x)q(y|x), π(y)q(x|y)) is symmetric in x and y. Summing over x and using the row sums gives πK = π.
(b) Detailed balance fails, so the chain converges to a different distribution. For the 5-state target with a 0.8/0.2 biased walk, the total-variation distance to π is **0.175** without the factor and about 3 × 10⁻¹⁴ with it.
*Marks:* (a) symmetric minimum 4, x = y and row sums 2, stationarity 2; (b) 4.

### Q4 — Calculation (12 marks)
For a flat universe with H₀ = 67.4 km/s/Mpc and Ω_m = 0.315 (Λ for the rest; radiation neglected) compute:
(a) the Hubble time; (b) the critical density in kg/m³; (c) the age, from t₀ = [2/(3H₀√Ω_Λ)] asinh√(Ω_Λ/Ω_m); (d) the Einstein–de Sitter age for the same H₀.

**Model answer.** (a) **14.51 Gyr**. (b) **8.53 × 10⁻²⁷ kg/m³**. (c) **13.80 Gyr**. (d) 2/(3H₀) = **9.67 Gyr**.
*Marks:* 3 each.

### Q5 — Prediction (12 marks)
Lesson 17's survey pipeline subtracts one median sky level per frame. On a night with a 300 → 900 e⁻ moonlight gradient across each frame, predict the effect on completeness and purity, explain the mechanism, and say what the fixed design measures.

**Model answer.**
- *Prediction:* purity stays at about 1 but completeness collapses. The shipped pipeline measured completeness 0.1745 with purity 1.0.
- *Mechanism:* one median leaves the whole gradient in the residual. The robust rms is inflated (about 226 e⁻ against photon noise of about 25 e⁻ for a pure gradient), so the 5σ threshold rises and only bright stars pass.
- *Fix:* a mesh background (SExtractor-style boxes with interpolation) restores completeness to **0.9729** with purity 0.984. The same catalogue hash across options A/B/C shows the change is algorithmic, not an artefact of parallelism.
*Marks:* prediction 4; mechanism 5; fix and evidence 3.

### Q6 — Design critique (16 marks)
An ADR for the alert broker proposes: "Drop all alerts within 30″ of satellite tracks predicted from public TLEs; no schema change; no documentation needed because this only removes noise." Critique it technically and ethically and write the decision you would record instead.

**Model answer.**
- *Technical:*
  - The COPUOS CRP (2026, para 24) reports that public TLEs are accurate only to a few arcminutes, so a 30″ mask misses most streaks and removes unrelated sky.
  - Glints and tumbling debris produce point-like false positives that are not on predicted tracks.
  - The proposal has no measurement of completeness or false-positive rate, and no fitness test.
- *Ethical:* silently discarding real transients harms downstream users (ACM 1.2). An undocumented filter misstates system limits (1.3). The ADR skips evaluation of impacts and risks (2.5). Twilight programmes such as NEO searches bear the loss.
- *Recorded decision:*
  - Add a `satellite_proximity` flag computed from the best available ephemerides, preferring operator data.
  - Keep all alerts.
  - Add a fitness test that injects transients near tracks and asserts completeness ≥ the agreed threshold.
  - Publish false-positive rates with and without the flag.
  - Revisit when astronomy-grade ephemerides are available.
  - Consequences: larger alerts, and consumers must filter.
*Marks:* technical 6; ethical with named principles 5; quality of the recorded decision (context, decision, consequences, test) 5.

### Q7 — Calculation (12 marks)
Three galaxies have d = 10, 20, 40 Mpc and v = 700, 1500, 2800 km/s, with σ_v = 300 km/s. Prior: H₀ ~ N(70, 5).
(a) Give the flat-prior posterior mean and s.d. (b) Give the posterior with the prior. (c) Which dominates, and how should you report it?

**Model answer.**
(a) Σvd = 149 000 and Σd² = 2100, so the mean is **70.95** and s = 300/√2100 = **6.55**.
(b) The precisions add: 2100/300² + 1/25 = 0.0633. This gives **70.35 ± 3.97**.
(c) The prior is somewhat more precise than the data (5 versus 6.55), so the two contribute comparably, the prior slightly more. Report the prior, the flat-prior result and the combined result.
*Marks:* 4 + 5 + 3.

### Q8 — Essay (14 marks)
In about 400 words, evaluate Hubble (1929) as evidence for a linear velocity–distance relation. Use at least two numerical checks of the paper's own figures. Separate what the evidence supported, what Hubble hedged, and what later work changed.

**Model answer outline.**
- *Evidence:* 24 nebulae with distances from Cepheids, novae, brightest stars and cluster luminosities; a joint least-squares solution with solar motion; two solutions (individual nebulae and nine groups) giving K of about 500. Independent support came from the 22 nebulae without individual distances (745/1.4 = 532, "K of 530") and from NGC 7619 (3910/500 = 7.82 Mpc, M = −17.66 against the printed −17.65).
- *Hedges:* "scanty material, so poorly distributed"; the Virgo nebulae unduly influence K; "a first approximation representing a restricted range".
- *Later work:* the distance scale was recalibrated, so K = 500 implies 1/K = 1.96 Gyr, whereas today's H₀ ≈ 67–73 km/s/Mpc gives about 13–14.5 Gyr. The linear law survived as the low-z limit of cz = H₀d.
*Marks:* evidence 4; checks 4; hedges 2; later work without anachronism 3; writing 1.
