# Midterm examination - weeks 1-7 (L100, L200, L500 #23-24)

**Time:** 2 hours. **Total:** 100 marks. **Allowed:** one A4 sheet of your own notes and a non-programmable calculator.

Show your working. A correct number without reasoning earns at most half marks. Every numeric model answer was recomputed by `research/l500_checks.py`.

---

## Q1 - Derivation: the M/M/1 queue (15 marks)
(a) For an M/M/1 queue with arrival rate λ and service rate μ (ρ = λ/μ < 1), use cut balance to derive πₙ = (1 − ρ)ρⁿ. **[6]**

(b) Derive L = ρ/(1 − ρ), and use Little's law to obtain W. **[4]**

(c) A help desk has μ = 1 per minute. Predict W at λ = 0.9 and at λ = 0.95. Explain to a manager, in two sentences, why a 5.6% increase in demand doubles the wait. **[5]**

**Model answer.**
(a) In steady state the flow across the cut between {0..n} and {n+1, …} balances: λπₙ = μπₙ₊₁. So πₙ₊₁ = ρπₙ and πₙ = ρⁿπ₀. Normalising, Σρⁿπ₀ = π₀/(1 − ρ) = 1, which requires ρ < 1 and gives π₀ = 1 − ρ. *(cut argument 3, recursion 1, normalisation with the ρ < 1 condition 2)*

(b) L = Σ n(1 − ρ)ρⁿ = (1 − ρ)·ρ/(1 − ρ)² = ρ/(1 − ρ). Then W = L/λ = 1/(μ − λ). *(2 + 2)*

(c) W(0.9) = 1/(1 − 0.9) = **10 min** and W(0.95) = 1/(1 − 0.95) = **20 min**. The wait depends on the *spare* capacity μ − λ, and that spare capacity halves from 0.10 to 0.05. Near full utilisation, small increases in demand therefore cause large increases in waiting. *(2 numbers, 3 explanation)*

## Q2 - Short explanation: where do confidence intervals come from? (10 marks)
A student runs one long simulation of 50,000 customers and reports mean wait 3.21 ± 0.02 minutes, computing the ± as 1.96 × (SD of the 50,000 waits)/√50,000. Explain which theorem the formula relies on, which of its assumptions fails here, and what the student should do instead.

**Model answer.** The formula is the CLT interval (Theorem 23.2) for the mean of **independent** identically distributed observations. Successive waits in a queue are strongly positively autocorrelated: a customer who arrives behind a long queue waits long, and so does the next one. The true variance of the mean is therefore far larger than s²/n, and the interval is much too narrow. The run also starts empty, which adds initialisation bias. Instead: delete a warm-up period (Welch), then use independent replications (L200 #10) or batch means, and build a t interval from the replication means. *(names CLT/independence 3, autocorrelation explained 3, warm-up 2, correct remedy 2)*

## Q3 - Prediction and derivation: Euler on a falling parcel (15 marks)
L100 #4 printed the explicit-Euler height error at t = 3 s with no drag (g = 9.8): +1.470000 at dt = 0.1, +0.147000 at dt = 0.01 and +0.014700 at dt = 0.001.

(a) Predict the error at dt = 0.05. **[3]**

(b) For y'' = −g, show that Euler's height error after n steps is exactly g·T·dt/2, where T = n·dt. **[7]**

(c) RK4's error was −1.4e-14, +7.8e-14 and +9.1e-13 at the same three steps. It *grows* as dt shrinks. Explain. **[5]**

**Model answer.**
(a) The error is first order (Theorem 24.1), so 1.47 × 0.05/0.1 = **0.735 m**. *(3)*

(b) Euler gives vₖ = −g·k·dt and yₙ = y₀ + dt·Σₖ₌₀ⁿ⁻¹ vₖ = y₀ − g·dt²·n(n − 1)/2. The exact height is y₀ − g(n·dt)²/2. Subtracting, the error is g·dt²·n/2 = g·T·dt/2. At T = 3 and dt = 0.1 this is 9.8 × 3 × 0.1/2 = 1.47, which matches the lab exactly. *(setting up the sum 3, closed form 2, difference 2)*

(c) With constant acceleration the exact solution is a quadratic in t, and RK4 integrates it exactly, so its truncation error is zero. What remains is round-off, about u per operation, and smaller dt means more steps (30 → 3,000), so the accumulated round-off grows. This is the floor of Theorem 24.4. *(exactness 2, round-off accumulation 3)*

## Q4 - Stability (15 marks)
A thermal model contains the mode y′ = −1000(y − T_env(t)). You need the solution on [0, 2] h with accuracy 1e-3.

(a) What is the largest explicit Euler step that stays stable? How many steps is that? **[5]**

(b) Implicit Euler with h = 0.01 h costs one linear solve per step, about 5× the cost of an explicit step. Which method is cheaper here? **[5]**

(c) Define stiffness, and say why this problem is stiff even though T_env(t) varies slowly. **[5]**

**Model answer.**
(a) |1 + hλ| ≤ 1 requires h ≤ 2/1000 = **0.002**, so at least **1,000 steps**. *(3 + 2)*

(b) Implicit Euler takes 200 steps at 5× cost, an equivalent of 1,000 explicit steps. That matches explicit Euler at its stability limit, but explicit Euler *at* the limit only oscillates without decaying, so a safe explicit run needs more steps still. Implicit Euler also lets the step follow accuracy (on the lesson's test problem, 20 steps gave 1.9e-5), so it wins. *(comparison 3, accuracy remark 2)*

(c) A problem is stiff when the step size is limited by stability rather than accuracy. The fast mode (λ = −1000) decays almost instantly, yet it still restricts every explicit step, while the solution of interest varies slowly. *(definition 3, explanation 2)*

## Q5 - Design critique: comparing two staffing policies (20 marks)
A team compares policies A (3 desks) and B (3 desks plus a triage desk) with a DES. For each policy they ran one run of 10,000 customers starting empty, with seed 42 for A and seed 43 for B. A gave a mean wait of 2.91 min and B 2.74 min, and they conclude "B reduces waits by 6%". They verified the DES "by inspection of the animation". Identify at least five problems and propose a corrected study design.

**Model answer (any five, 3 marks each, plus 5 for a coherent design).**
1. **One run per policy.** There is no estimate of between-run variability, so the difference may be noise.
2. **Starting empty.** Initialisation bias, with no warm-up deletion.
3. **Different seeds.** Independent streams inflate the variance of the difference. Common random numbers would sharpen it (L200 #11: ± 0.44 → ± 0.12).
4. **A 6% claim with no confidence interval.** Report the difference ± a t half-width over paired replications.
5. **Verification by animation only.** Animation is face validity. Verify against Erlang C (L200 #8) and check degenerate cases (no arrivals → no waits).
6. **No input modelling.** Were service times fitted and checked (L200 #7)? An exponential assumption can bias waits by about 25%.
7. **No accuracy requirement.** What difference matters to the decision?

**Corrected design:** warm-up chosen by Welch's method; R paired replications using CRN; a paired-t interval on (A − B); R increased until the half-width is below the decision threshold; verification against Erlang C at the same utilisation; an ADR recording the decision.

## Q6 - Prediction: variance reduction (10 marks)
(a) Antithetic pairs give Corr(f(U), f(1 − U)) = −0.5. Predict the variance reduction factor at equal cost. **[4]**

(b) A control variate correlates 0.9 with the output. Predict the factor using 1/(1 − r²). **[3]**

(c) Name one integrand for which antithetics make things worse, and say why. **[3]**

**Model answer.**
(a) 1/(1 + ρ) = 1/0.5 = **2.00x**. *(4)*

(b) 1/(1 − 0.81) = **5.26x**. *(3)*

(c) Any function symmetric about 0.5, such as (u − 0.5)². Then f(U) = f(1 − U), so ρ = +1, and the variance doubles: the lesson's check observed 0.53x. *(3)*

## Q7 - Short explanation: input modelling (15 marks)
For 200 service times the lab found Kolmogorov-Smirnov distances of D = 0.217 (exponential), 0.132 (normal) and 0.031 (lognormal).

(a) Compute the approximate 5% critical value 1.36/√n and state which candidates are rejected. **[5]**

(b) Why is this critical value only approximate when the parameters were estimated from the same data? **[5]**

(c) Why does choosing exponential service *overstate* queue waits when the true coefficient of variation is below 1? **[5]**

**Model answer.**
(a) 1.36/√200 = **0.096**. Exponential (0.217) and normal (0.132) are rejected; lognormal (0.031) is not. *(2 + 3)*

(b) Fitting the parameters to the same data pulls the fitted CDF towards the empirical one, so D is stochastically smaller than under a fully specified H₀. The tabulated critical value is therefore conservative: the true size of the test is below 5%, and the test rejects too rarely. Lilliefors-type corrections or a parametric bootstrap fix this. *(5)*

(c) Mean queueing delay grows with service variability (Pollaczek-Khinchine: Wq ∝ (1 + CV²)/2 for M/G/1). The exponential has CV = 1, so if the real CV is smaller, the model has too much variance and the waits come out too long. L200 #7 measured about 25%. *(5)*
