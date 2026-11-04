# Midterm examination — week 7 (lessons 1–11 and 23–24)

**Time:** 2 hours. **Total:** 100 marks. **Allowed:** one A4 sheet of notes and a scientific calculator; no network.
**Constants:** GM☉ = 1.3271244 × 10²⁰ m³ s⁻²; 1 au = 1.495978707 × 10¹¹ m; T☉ = 5772 K; Wien b = 2.897771955 × 10⁻³ m K.
All model-answer numbers were computed by code (`research/l500_checks.py`, the lab scripts, or the course's verified lab outputs).

---

### Q1 — Derivation (15 marks)
(a) From conservation of energy and angular momentum, derive the vis-viva equation v² = GM(2/r − 1/a). (8)
(b) A comet has a = 1 au and e = 0.9. Find its speed at r = 1 au and at perihelion r = 0.1 au. (5)
(c) Explain in one sentence why the first answer does not depend on e. (2)

**Model answer.**
(a) As in lesson 23, theorem 2. Use h = r_p v_p = r_a v_a and energy conservation at the two apsides. These give v_p² = 2GM r_a/(r_p(r_a + r_p)), so E = −GM/(2a). Since E is constant, v²/2 − GM/r = −GM/(2a) everywhere.
(b) At r = a = 1 au: v² = GM/a, so v = **29.78 km/s**. At perihelion: v = √(GM(2/0.1 au − 1/1 au)) = √19 × 29.78 = **129.8 km/s**.
(c) At r = a the term 2/r − 1/a equals 1/a for every e; eccentricity changes the direction of the velocity, not its magnitude, at that radius.
*Marks:* (a) 2 for the conserved quantities, 4 for the algebra, 2 for generalising from the apsides to all r. (b) 2 + 3. (c) 2.

### Q2 — Short explanation (10 marks)
Lesson 11 measured |ΔE/E| = 1.24 × 10⁻² for Euler and 1.22 × 10⁻¹² for leapfrog over the same run. Explain why leapfrog conserves energy so much better, and whether that makes its orbits "exact".

**Model answer.** Leapfrog (kick–drift–kick) is symplectic and time-reversible. It exactly conserves a nearby "shadow" Hamiltonian, so its energy error oscillates and stays bounded instead of drifting. Euler is neither, and its energy error grows secularly (outward spiral). The orbit is still not exact: phase (timing) errors accumulate, the error depends on dt, and the measured Kepler-III period in lesson 23's check differs from the formula by 1.3 × 10⁻⁷ at dt = 10⁻⁴ yr.
*Marks:* symplectic/reversible 4; bounded vs secular error 4; limits 2.

### Q3 — Derivation + calculation (15 marks)
(a) Derive the spherical cosine rule from a dot product, and apply it to the pole–zenith–star triangle to obtain sin h = sin δ sin φ + cos δ cos φ cos H. (9)
(b) At Gurgaon (φ = 28.46°), find Polaris's (δ = 89.2641°) altitude at upper and lower culmination. (6)

**Model answer.**
(a) As in lesson 23, theorem 4. Place A at the pole; then cos a = B̂·Ĉ = cos b cos c + sin b sin c cos A. The triangle sides are 90 − φ, 90 − δ and 90 − h, and the angle at the pole is H.
(b) Upper culmination: h = 90 − (δ − φ) = **29.20°**. Lower culmination: h = φ − (90 − δ) = **27.72°**.
*Marks:* (a) 4 for the vector set-up, 2 for the rule, 3 for the triangle mapping; (b) 3 + 3.

### Q4 — Prediction (12 marks)
A colleague replaces lesson 7's atan2 (Vincenty) separation with arccos of the spherical cosine rule "because it is simpler". Predict what happens when cross-matching two catalogues whose true counterparts are 0.01″ apart at δ = 60°, and justify numerically.

**Model answer.** cos θ = 1 − θ²/2 with θ ≈ 5 × 10⁻⁸ rad, so θ²/2 ≈ 10⁻¹⁵, near double-precision resolution (2.2 × 10⁻¹⁶). Arccos amplifies the rounding. The computed separation is **0.00972″ instead of 0.01″** (about 3 % low), and at 1″ the relative error is still 2.6 × 10⁻⁶. Matches within a tight radius become noisy and a few can flip. Predict also that identical positions can return a tiny nonzero separation. Keep atan2 or haversine.
*Marks:* the cancellation mechanism 5; numbers 4; consequence for matching 3.

### Q5 — Calculation (13 marks)
A star has R = 1.711 R☉ and T_eff = 9940 K. (a) Find L/L☉. (b) Find its blackbody peak wavelength. (c) Where does it lie on the HR diagram relative to the Sun, and along which line would it move if it expanded at constant T?

**Model answer.** (a) L/L☉ = 1.711² × (9940/5772)⁴ = **25.7**. (b) λ_peak = b/T = **291.5 nm** (ultraviolet). (c) It lies above and to the left of the Sun: hotter and more luminous. Expanding at constant T moves it straight up, since L ∝ R² at fixed T. Lines of constant R have slope 4 in log L against log T.
*Marks:* 5 + 4 + 4.

### Q6 — Design critique (20 marks)
A team's photometry pipeline computes distances as d = 1/p from Gaia parallaxes for every star and writes them to a catalogue without uncertainties. About 30 % of the stars have σ_p/p > 0.3, and some have negative parallaxes. Critique the design and propose a better one.

**Model answer.**
- *Problems:*
  - 1/p is undefined for p ≤ 0 and strongly biased for large fractional errors; the inverse of a noisy quantity is not an unbiased distance.
  - Selecting stars by p imports Lutz–Kelker-type biases (lesson 24, l Car: a −0.08 mag correction even at 10 %).
  - Dropping uncertainties hides the problem from users (ACM 1.3 honesty, 2.5 evaluation).
- *Better design:*
  - Store p and σ_p as primary data.
  - Derive distances as posteriors with a stated prior (a space-density model; lesson 25 theorem 4) and report the median with an interval.
  - Flag σ_p/p > 0.2; never invert negative parallaxes.
  - Test with injected stars of known distance and report coverage (lesson 15).
  - Document the choice in an ADR.
*Marks:* identifies ≥ 3 problems with mechanisms 8; credible design 8; verification plan 4.

### Q7 — Calculation and explanation (15 marks)
A Cepheid with log P = 1.5 has ⟨V⟩ = 25.0 (no extinction). Using the illustrative P–L relation M_V = −2.43(log P − 1) − 4.05:
(a) find its distance; (b) find the distance error caused by a 0.10 mag error in the P–L zero point; (c) explain why observing 100 more Cepheids in the same galaxy does not fix (b).

**Model answer.**
(a) M_V = **−5.265**, μ = **30.265**, d = **11.30 Mpc**.
(b) σ_d/d = (ln 10/5) × 0.10 = **4.6 %**, about 0.52 Mpc.
(c) The zero-point error is shared by every Cepheid. Averaging reduces the random scatter but not a common calibration offset; only a better rung-1 calibration (parallaxes) does.
*Marks:* (a) 6, (b) 5, (c) 4.
