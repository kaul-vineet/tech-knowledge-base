**Concept: statistics for evaluating agents – how much a pass rate really tells you**

## Why it matters
Lesson 12's gate blocked a prompt because 18 of 20 golden cases passed instead of 20. Was that a real regression or noise? Lesson 21 compared a new model against a baseline; lesson 16 reported a red-team block rate. Every one of those is a proportion estimated from a small sample, and every decision taken on it has an error rate you can compute. Without that computation, teams ship regressions that "passed the eval" and block improvements that "failed" by one case.

## Definitions
- **Pass rate as a binomial proportion.** If each of n independent cases passes with probability p, the number of passes X follows Binomial(n, p) and the observed rate is p̂ = X/n. "Independent" matters: twenty paraphrases of one ticket are closer to one case than twenty.
- **Confidence interval (CI).** A procedure that, applied to many repeated samples, contains the true p in at least the stated share of them (the *coverage*). It is a statement about the procedure, not a 95 % probability for one particular interval.
- **Wald interval.** p̂ ± z·√(p̂(1−p̂)/n). Easy, and wrong near 0 or 1: at 20/20 it is [1, 1].
- **Wilson score interval.** The set of p that a z-test would *not* reject: |p̂ − p| ≤ z·√(p(1−p)/n). Recommended for virtually all n and p (NIST/SEMATECH e-Handbook §7.2.4.1, citing Wilson 1927, Brown–Cai–DasGupta 2001, Agresti–Coull 1998).
- **Power.** The probability that a test detects a real change of a given size. Power 0.8 means one real regression in five slips through.
- **Paired design.** Old and new agent run on the *same* cases. Only the discordant cases – passed by one, failed by the other – carry information about the difference (McNemar 1947).
- **Family-wise error rate (FWER).** The probability of at least one false alarm when you run m tests.

## Key results (proved in the lesson, checked in `eval_stats.py`)
1. **Wilson interval (T1).** Squaring the score inequality gives a quadratic in p whose roots are centre ± half with centre = (p̂ + z²/2n)/(1 + z²/n). The interval always lies in [0, 1] and is never empty at 0/n or n/n. Exact coverage at n = 20, p = 0.95: Wald 0.6389, Wilson 0.9245.
2. **Sample size (T2).** To detect a drop from p0 to p1 with a one-sided level-α test and power 1 − β you need about n = ((z_{1−α}√(p0q0) + z_{1−β}√(p1q1)) / (p0 − p1))² cases. Halving the effect size quadruples n. A 90 % → 85 % drop needs 253 cases; lesson 12's 20 cases detect a 95 % → 90 % drop with power 0.1330.
3. **McNemar (T3).** Under "no difference", each discordant case is equally likely to favour either version, so b given b + c is Binomial(b + c, ½). The exact p-value is a binomial tail. Concordant cases (both pass, both fail) cancel out.
4. **Multiple comparisons (T4).** P(any false alarm) ≤ Σ α_i (Boole's inequality), so testing each of m categories at α/m keeps the FWER ≤ α whatever the dependence. Without correction and with independent tests, FWER = 1 − (1 − α)^m: 0.6415 for 20 categories at 0.05.

## Intuition
The standard error of a pass rate is √(p(1−p)/n). Near p = 0.9 and n = 20 that is about 0.067: a single case moves the rate by 0.05, less than one standard error. Small golden sets are *regression alarms for big breaks*, not instruments for measuring small improvements. Pairing is the cheapest power you can buy: if both versions fail the same hard cases, those cases cancel, and the test looks only at where they disagree.

## Worked example (lesson 12's numbers)
- 20/20 passes: Wilson 95 % CI [0.839, 1.000]. "100 %" is compatible with a true rate of 84 %.
- 18/20: [0.699, 0.972]. The intervals overlap heavily; the gate blocked v2 because of a *rule* (no previously passing case may fail), not because the pass rates differ significantly.
- Paired view of v1 → v2: 2 cases broke, 0 were fixed, so b = 2, c = 0 and the exact McNemar p-value is 0.500. Statistically this is weak evidence; operationally, two *named* regressions on cases you understand are a good reason to block. The statistics tell you how much the *rate* tells you; they do not replace looking at the failures.
- A bigger paired suite: 200 cases, b = 15, c = 5: exact p = 0.0414. Analysed as if unpaired (170 vs 160 passes out of 200), the two-proportion test gives p = 0.1882 – the same data, a much weaker conclusion, because the pairing information was thrown away.

## How to use this in practice
1. Report every pass rate with n and a Wilson interval.
2. Decide the smallest regression you must catch and compute n *before* building the golden set; if n is unaffordable, say which size of drop the gate can and cannot see.
3. Compare versions on the same cases with McNemar, and read the discordant cases by hand.
4. Fix the list of slices (categories, languages) in advance and correct for the number you test; for exploratory slicing, treat any hit as a hypothesis to confirm on fresh cases.
5. Keep the rule-based gate (no previously passing case may fail) – it catches *known* regressions with certainty, which no test of proportions can.

## Common misconceptions
- **"95 % CI means a 95 % chance the true value is inside this interval."** Coverage is a property of the procedure over repeated samples.
- **"Non-overlapping intervals are needed for a significant difference."** Overlapping intervals can still differ significantly, especially in a paired design.
- **"More model runs on the same 20 cases give more cases."** Repeating a case measures sampling noise of the model on that case, not coverage of the task. Use them to estimate per-case pass probability, not to multiply n.
- **"p = 0.05 means a 5 % chance the regression is not real."** It is the probability of data at least this extreme *if there were no regression*.
- **"Check every slice and fix the ones that fail."** With 20 slices at 0.05, about two will "fail" by chance in an unchanged system.
- **"The normal formula gives the exact n."** It is an approximation; the exact binomial power at n = 253 is 0.7810, slightly below the 0.8 target – verify with the exact test and round up.

## Sources
NIST/SEMATECH e-Handbook of Statistical Methods §7.2.4.1 · Wilson (1927), JASA 22:209 · McNemar (1947), Psychometrika 12:153 (doi:10.1007/BF02295996) · Jurafsky & Martin ch. 3 (test sets with enough statistical power).
