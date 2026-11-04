# Midterm examination – AI Agents (week 7)

**Covers:** L100 #1–6, L200 #7–11, L300 #12–14, L500 #23–24. **Time:** 2 hours. **Total:** 60 marks. Closed book; one A4 sheet of your own notes; a non-programmable calculator. Numerical answers to 4 decimals unless stated. All model-answer numbers were recomputed with the L500 lab modules (`research/l500_checks.py` verifies that they appear in this file).

---

### Q1 Derivation (10 marks)
Let p = softmax(z/T) for logits z ∈ ℝ^V. Show that the entropy H(p) satisfies dH/dT = Var_p(z)/T³ and state when the derivative is zero. Explain in two sentences what this means for an agent that uses T = 0 for JSON output and T = 0.8 for drafting replies.

**Model answer.** With β = 1/T and Z = Σ exp(βz_i): log p_i = βz_i − log Z, so H = log Z − β E_p[z] (2). d log Z/dβ = E_p[z] and dE_p[z]/dβ = E_p[z²] − E_p[z]² = Var_p(z) (2). Hence dH/dβ = E_p[z] − E_p[z] − β Var_p(z) = −β Var_p(z) (2), and dH/dT = dH/dβ · dβ/dT = −β Var · (−1/T²) = Var_p(z)/T³ (2). Zero only when all logits with positive probability are equal (1). Meaning: raising T never makes the distribution more certain; T = 0 is the argmax limit (deterministic, good for schema-validated JSON), T = 0.8 trades some score for variety in drafts, which must still be checked (1).

### Q2 Prediction (8 marks)
Logits for four candidate tools are (3, 1, 1, 0). (a) Give the softmax probabilities at T = 1 and T = 2. (b) Give the entropy of each in nats. (c) Which tokens does top-p with p = 0.9 keep at T = 1?

**Model answer.** (a) T = 1: (0.7573, 0.1025, 0.1025, 0.0377); T = 2: (0.5105, 0.1878, 0.1878, 0.1139) (4). (b) 0.8011 and 1.2188 nats – entropy rises with T, as Q1 predicts (2). (c) Sorted cumulative mass: 0.7573, 0.8598, 0.9623 → the first three are kept (the two tied tools both survive because the threshold is crossed only by the third) (2).

### Q3 Short explanation (6 marks)
A colleague's attention layer trains to near-zero loss in minutes, but generation is nonsense. Their code computes `softmax(Q @ K.T / sqrt(d)) @ V`. Explain the bug, why it produces exactly this symptom, and the one-line fix.

**Model answer.** No causal mask (2): position i can attend to token i+1, the very token it must predict, so it learns to copy – loss collapses (2). At generation time future tokens do not exist, the copying shortcut is useless and output degrades (1). Fix: set scores for j > i to −∞ before the softmax, e.g. `np.where(np.tril(np.ones((n, n), bool)), scores, -np.inf)` (1).

### Q4 Calculation (8 marks)
An agent passes 45 of 50 golden cases. (a) Compute the 95 % Wilson and Wald intervals. (b) Your product owner asks "is the true pass rate at least 95 %?" Answer with reference to (a).

**Model answer.** (a) Wilson [0.7864, 0.9565] (3); Wald [0.8168, 0.9832] (2). (b) 95 % lies inside the Wilson interval, so the data are compatible with ≥ 95 %, but also with rates as low as about 79 % – 50 cases cannot answer the question; Wilson is the right interval near the boundary (Wald's coverage there is poor) (3).

### Q5 Calculation and interpretation (10 marks)
Prompt v1 and v2 are run on the same 200 cases: 171 pass with both, 9 pass only with v1, 2 pass only with v2, 18 fail with both. (a) Exact McNemar p-value. (b) Continuity-corrected chi-square statistic and p-value. (c) The p-value of an unpaired two-proportion test on 180 vs 173 passes. (d) Recommendation.

**Model answer.** (a) b = 9, c = 2, m = 11: 2·P(Bin(11, ½) ≤ 2) = 0.0654 (3). (b) (|9 − 2| − 1)²/11 = 36/11 = 3.2727, p = 0.0704 (3). (c) 0.2771 (2) – far weaker, because pairing is ignored. (d) Not significant at 0.05, but 9 regressions versus 2 fixes is a signal: read the 9 discordant cases; if they share a cause, fix before release; enlarge the suite if the decision depends on the rate (2).

### Q6 Design critique (10 marks)
Lesson 12's gate: 20 golden cases, block if pass rate < 95 % or if any previously passing case fails. Critique it statistically and propose two concrete improvements, quantifying one of them.

**Model answer.** Strengths: the per-case regression rule detects *known* regressions deterministically; cases are labelled and versioned (2). Weaknesses: the 95 % bar on n = 20 means one failure decides; 20/20 has a Wilson lower bound of 0.8389; the exact one-sided test against a 95 % → 90 % drop has power 0.1330, so most moderate regressions pass (3); no per-category control, and adding many categories inflates false alarms (1). Improvements: (i) a larger regression suite sized with the sample-size formula – about 150 independent cases for a 95 % → 90 % drop at α = 0.05, power 0.8 (2); (ii) paired comparison with McNemar against the previous version, reporting Wilson intervals, and Bonferroni across pre-registered categories (2).

### Q7 Prediction (8 marks)
A model endpoint returns 503 independently with probability 0.2 per call. The agent retries up to 3 attempts in total. (a) Expected number of calls. (b) Probability the user gets the fallback answer. (c) Which part of lesson 14's design would you change if the 503s came from a server that stays down for minutes, and why?

**Model answer.** (a) 1 + 0.2 + 0.04 = 1.2400 (3). (b) 0.2³ = 0.0080 (2). (c) Failures are then correlated, so the conditional success probability of the next attempt is near 0 and retries only add cost and load: use a circuit breaker / fallback model immediately after the first failure and backoff with jitter; keep the budget (3).
