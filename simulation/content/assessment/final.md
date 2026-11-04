# Final examination - whole course (L100-L500)

**Time:** 3 hours. **Total:** 100 marks. **Allowed:** one A4 sheet of your own notes and a non-programmable calculator.

Answer **all** questions. Questions 1-5 are derivations and predictions, question 6 is a design critique, question 7 is ethics and question 8 is on the readings. Every numeric model answer was recomputed by `research/l500_checks.py`.

---

## Q1 - Proof: weak law of large numbers (10 marks)
State and prove the weak law of large numbers for pairwise uncorrelated X₁ … Xₙ with mean μ and variance σ² < ∞. Then compute Chebyshev's guarantee for n = 400 and ε = 0.2 with σ² = 1. Is the bound tight? Use the lesson's observed 0.0003 in your answer.

**Model answer.**
- **Markov's inequality.** For Y ≥ 0, Y ≥ a·1{Y ≥ a}, so P(Y ≥ a) ≤ E[Y]/a.
- **Chebyshev.** Apply Markov to Y = (X̄ − μ)² with a = ε²: P(|X̄ − μ| ≥ ε) ≤ Var(X̄)/ε².
- **Variance of the mean.** Because the covariances vanish, Var(X̄) = σ²/n. So P(|X̄ − μ| ≥ ε) ≤ σ²/(nε²) → 0.
- **The numbers.** With n = 400, ε = 0.2 and σ² = 1, the bound is 1/(400 × 0.04) = **0.0625**. The observed value for exponential data was 0.0003, so the bound is valid but about 200× loose, because it uses only the variance.

*(Markov 2, Chebyshev 2, variance 3, number 1, tightness 2)*

## Q2 - Derivation: Poisson process (12 marks)
(a) From the Poisson process axioms, derive P(N(t) = 0) = e^(−λt) and hence the distribution of the first inter-arrival time. **[7]**

(b) Ambulance calls arrive at 2 per hour. A dispatcher has had no call for 45 minutes. What is the probability of no call in the next 30 minutes? Name the property you used. **[5]**

**Model answer.**
(a) Independent and stationary increments give P₀(t + h) = P₀(t)(1 − λh + o(h)). Rearranging and letting h → 0 gives P₀′ = −λP₀ with P₀(0) = 1, so P₀(t) = e^(−λt). The first arrival comes after t exactly when there is no event in [0, t], so P(T₁ > t) = e^(−λt): T₁ is Exponential(λ). *(difference equation 3, ODE solution 2, link to T₁ 2)*

(b) By memorylessness the 45 minutes are irrelevant: P = e^(−2 × 0.5) = **0.3679**. *(3 + 2)*

## Q3 - Prediction: order and round-off (12 marks)
On a smooth test problem at h = 0.1, explicit Euler has global error 0.2420 and RK4 has 6.990e-06.

(a) Predict both errors at h = 0.025. **[4]**

(b) RK4 needs 4 evaluations of f per step and Euler needs 1. Using the predictions, which method reaches an error below 1e-4 more cheaply? **[4]**

(c) In float32, explicit Euler on y′ = −y stopped improving beyond about 10⁴ steps. Explain, and say how the picture changes in float64. **[4]**

**Model answer.**
(a) Euler is first order, so its error is about 0.2420/4 = **0.0605** (measured: 0.0655). RK4 is fourth order, so its error is about 6.990e-06/256 = **2.73e-08** (measured: 2.779e-08). *(2 + 2)*

(b) Euler needs error ∝ h. Going from 0.242 at h = 0.1 to below 1e-4 needs h ≈ 4e-5, about 50,000 steps or 50,000 evaluations. RK4 already meets 1e-4 at h = 0.1, which is 20 steps or 80 evaluations. RK4 is cheaper by a factor of several hundred. *(4)*

(c) Each step adds a rounding error of about u (u₃₂ ≈ 6e-8). Over N steps these accumulate to roughly N·u in the worst case, while truncation error falls like 1/N. Beyond about 10⁴ steps, round-off dominates. Float64 has u ≈ 1.1e-16, so its floor is about 10⁹ times lower and Euler keeps its O(h) behaviour to 10⁶ steps. *(4)*

## Q4 - Proof and test design: RANDU (12 marks)
(a) For RANDU (xₖ₊₁ = 65539·xₖ mod 2³¹), prove that 9uₖ − 6uₖ₊₁ + uₖ₊₂ is an integer, and deduce that triples lie on at most 15 planes. **[7]**

(b) Design a test that detects this defect but which a 1-D chi-square test misses. State the statistic and its degrees of freedom. **[5]**

**Model answer.**
(a) 65539² = (2¹⁶ + 3)² = 2³² + 6·2¹⁶ + 9, and 2³² ≡ 0 (mod 2³¹), so a² ≡ 6·2¹⁶ + 9 = 6a − 9. It follows that xₖ₊₂ ≡ 6xₖ₊₁ − 9xₖ. Dividing by 2³¹ gives 9uₖ − 6uₖ₊₁ + uₖ₊₂ = j with j an integer. The left side lies in (−6, 10), so j ∈ {−5, …, 9}: 15 planes. *(algebra 4, range 3)*

(b) Use a 3-D serial test. Take non-overlapping triples, bin each coordinate into d = 20 intervals (d³ = 8,000 cells) and compute Pearson's X² with 7,999 df. The lesson's check gave X² = 151,465 for RANDU, while PCG64, Philox and MT19937 gave p > 0.1. Expected counts should be ≥ 5 per cell: 200,000 triples gives 25. *(design 3, df 1, expected-count rule 1)*

## Q5 - Derivation: importance sampling for a rare event (14 marks)
A service-level breach has probability p = P(Z > 4) with Z ~ N(0, 1), and p = 3.167e-05.

(a) Derive the importance-sampling identity and its variance. **[5]**

(b) For the proposal q = N(4, 1), derive the weight and the exact per-sample variance. **[5]**

(c) How many naive samples give a relative standard error of 10%? How many IS samples? **[4]**

**Model answer.**
(a) E_q[f·p/q] = ∫f(p/q)q = ∫fp = μ, provided q > 0 wherever fp ≠ 0. The per-sample variance is ∫f²p²/q − μ². *(5)*

(b) The weight is w = φ(x)/φ(x − 4) = e^(8 − 4x). Completing the square, φ(x)²/φ(x − 4) = e¹⁶φ(x + 4), so the second moment is e¹⁶P(Z > 8) and the variance is **4.525e-09**. *(5)*

(c) Naive: relative SE = √((1 − p)/(Np)) = 0.1 gives N = (1 − p)/(0.01p) ≈ **3,157,339**. IS: N = 4.525e-09/(0.01p²) ≈ **452** samples. *(2 + 2)*

## Q6 - Design critique: a model card (14 marks)
A digital-twin model card claims the following. Validated: yes. Accuracy: within 2% of the real system. Valid range: utilisation up to 0.95. Key input: arrival rate. Evidence: an M/M/c comparison at ρ = 0.5, 0.7 and 0.85 with 10 replications, a 10% accuracy requirement, a relative CI half-width of 11.9% at ρ = 0.90, and sensitivity elasticities of 6.01 to λ and −7.02 to μ. Identify every overclaim and rewrite the card's claims.

**Model answer.**
- "Within 2%" is not supported: the requirement was 10% and the evidence shows errors up to the 10% level.
- "Up to 0.95" is outside the tested envelope, and ρ = 0.90 already failed the CI requirement (11.9% > 10%). The envelope is utilisation ≤ 0.85.
- The key input is **μ**, not λ: |−7.02| > 6.01.
- "Validated" needs a qualifier: validated against M/M/c (verification-like operational validity) for this intended purpose, not against field data.

**Rewrite:** "Operationally validated against Erlang C within 10% for utilisation 0.50-0.85 (10 replications per point); not valid above 0.85. Most influential input: service rate (elasticity −7.02). Intended use: hourly staffing advice, reviewed by a manager."

*(each overclaim 3, rewrite 2; this mirrors L400 #21)*

## Q7 - Ethics: a staffing model that affects workers (14 marks)
Your capstone twin recommends hourly staffing. Management proposes to use it, without review, to set individual agents' shifts and to flag "under-performing" agents whose handling times exceed the model's lognormal mean. Using the ACM Code (2018) and the AQuA Book (2025), analyse the proposal and recommend safeguards. (About 400 words.)

**Model answer (points).**
- **Change of intended use.** The model was validated for aggregate hourly staffing, not for judging individuals. Sargent: validity is relative to purpose.
- **Statistical error.** A lognormal service-time distribution means about half of all agents exceed the mean by chance. Flagging on the mean misreads variability as performance, which is an aggregate-to-individual error like lesson 26's.
- **ACM 1.2 (avoid harm).** Unfair flags harm livelihoods.
- **ACM 2.5 (evaluate impacts and risks).** Evaluating the impacts and risks of this use is the modeller's duty.
- **ACM 1.3 (honesty).** State the model's limits plainly.
- **ACM 3.1 (public good).** Put the public good and affected people at the centre.
- **AQuA Book.** Name a commissioner for the new use, require independent assurance proportionate to the consequence (employment decisions are high stakes), and have an approver accept the residual risk explicitly.
- **Safeguards.** Keep the model to aggregate staffing; any individual review uses human judgement with context; publish the intended-use statement on the model card; consult the affected staff (OSR: test acceptability with affected groups); provide an appeal route.

*(use change 3, statistical argument 3, codes cited accurately 4, safeguards 4)*

## Q8 - Readings (12 marks)
(a) In under 80 words, state what Metropolis and Ulam (1949) left open about the method's error, and give the modern answer with its assumption. **[4]**

(b) Sargent (2010) distinguishes conceptual model validity, computerized model verification, operational validity and data validity. Classify each capstone check: (i) the DES matches Erlang C under exponential inputs; (ii) the lognormal service-time fit has KS D = 0.0059; (iii) the arrival log has duplicate rows removed; (iv) the patience calibration matches holdout days. **[8]**

**Model answer.**
(a) They noted that a precise estimate of the error for a finite sample was still open. The modern answer is that the error of the mean is σ/√N, with interval μ̂ ± 1.96·s/√N from the CLT. It assumes independent samples with finite variance. *(4)*

(b)
- (i) Computerized model verification: comparison with an analytic model in a degenerate, exponential case.
- (ii) Conceptual model validity of the input assumption, supported by data.
- (iii) Data validity.
- (iv) Operational validity, through historical-data validation on holdout days.

*(2 each)*
