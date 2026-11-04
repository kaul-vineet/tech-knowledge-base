**Concept: deterministic numbers that behave randomly, and estimators that use them well**

## Why it matters
Every stochastic result in this course started as `default_rng(seed)`. L300 #12 found that reseeding inside a loop destroyed antithetic variance reduction (ρ −0.00, gain 1.01×). L300 #16 found that giving every worker the same seed produced one distinct result out of 40. Those faults were caught by tests. This lesson gives the theory behind them: what a generator must satisfy, how to test one, why Monte Carlo error is σ/√N in any dimension, and how importance sampling and antithetics change σ.

## Definitions
- **Pseudo-random number generator.** A state s, a transition s → T(s) and an output map g(s). It is completely deterministic, and it is good if its outputs are hard to tell apart from iid U(0, 1) values *in every way your simulation uses them*.
- **LCG.** x₍ₖ₊₁₎ = (a·xₖ + c) mod m, with output xₖ/m. Its **period** is the length of the cycle, at most m.
- **PCG64 (NumPy's default).** A 128-bit LCG state with a *permutation* (xorshift plus a data-dependent rotation) applied to the output. This hides the LCG's weak low bits. Its period is 2¹²⁸, and `advance(n)` jumps ahead in O(log n) work.
- **Philox (counter-based).** The output is a keyed bijection of a counter (Salmon et al. 2011). Value n of stream k can be computed directly, with no sequential state, so parallel streams need only distinct keys. NumPy's Philox4x64 has period 2²⁵⁶ − 1.
- **Goodness-of-fit statistics.** Pearson's X² = Σ(O − E)²/E over cells. Kolmogorov-Smirnov's Dₙ = sup|Fₙ − F|.
- **Monte Carlo estimator.** μ̂_N = (1/N) Σ f(Xᵢ). The **importance sampling** estimator is (1/N) Σ f(Yᵢ)p(Yᵢ)/q(Yᵢ) with Yᵢ ~ q. **Antithetic pairs** average f(U) and f(1 − U).

## Key results
1. **Full period (Theorem 25.1, Hull & Dobell 1962).** An LCG has period m iff gcd(c, m) = 1, every prime factor of m divides a − 1, and 4 | (a − 1) whenever 4 | m. We checked this by brute force for every (a, c) with m = 64, 60 and 81. The RANDU corollary takes three lines: a² ≡ 6a − 9 (mod 2³¹), so 9uₖ − 6uₖ₊₁ + uₖ₊₂ is an integer between −5 and 9. Every triple therefore lies on one of 15 planes.
2. **Tests (Theorem 25.2).** Under H₀, E[X²] = k − 1 exactly (a binomial variance calculation), and X² → χ²(k − 1). √n·Dₙ has a limit that does not depend on F. A test can only reject; passing proves nothing.
3. **Monte Carlo variance (Theorem 25.3a).** E[μ̂_N] = μ and Var = σ²/N, whatever the dimension. Halving the error costs 4× the samples.
4. **Importance sampling (Theorem 25.3b).** E_p[f] = E_q[f·p/q] whenever q > 0 where fp ≠ 0. The variance is (∫f²p²/q − μ²)/N, and q* = fp/μ gives zero variance.
5. **Antithetics (Theorem 25.4).** Var of the pair mean is (σ²/2)(1 + ρ), so the gain at equal cost is 1/(1 + ρ). For monotone f, ρ ≤ 0 by the association inequality: (f(U) − f(V))(g(U) − g(V)) ≤ 0 when g is decreasing.

## Intuition
A generator is a long, carefully shuffled list of numbers that you read in order. Period is the list's length; quality is how well it is shuffled *in the dimensions you look at*. RANDU's list looks perfect one number at a time but has visible structure three at a time.

Monte Carlo error depends only on σ and N. That is its strength in high dimensions and its weakness for small probabilities. Importance sampling moves the samples to where the integrand matters and pays them back with weights. Antithetics make two errors cancel, which works only if they really do point in opposite directions.

## Worked example (numbers from the check scripts)
- **Tests.** The mean X² over 400 PCG64 runs (k = 100) is 99.06 (theory 99). PCG64, Philox and MT19937 pass a 1-D chi-square, KS and a 3-D chi-square (20³ cells). RANDU passes 1-D (p = 0.958) and KS (p = 0.814), then fails 3-D with X² = 151,465 on 7,999 df. An m = 2³² LCG's low bit alternates 1010…, so a serial pair test gives X² = 30,000 on 3 df.
- **Plain MC of ∫₀¹eˣdx.** σ² = 0.24204. The SD of 2,000 estimates is 0.0505, 0.0241, 0.0125 and 0.0063 at N = 100, 400, 1600 and 6400, with a log-log slope of −0.500.
- **Rare event P(Z > 4) = 3.167e-5.** Naive sampling with N = 100,000 has a relative SE of 0.56. Importance sampling with q = N(4, 1) and weight e^(8 − 4x) has a relative SE of 0.021 with N = 10,000. Its per-sample variance is 4.525e-9 against 3.167e-5, about 7,000× fewer samples.
- **Antithetics on eˣ.** ρ = −0.968 predicts a 30.9× gain; we observed 30.1×. For the symmetric (u − 0.5)², ρ = +1 and the gain is 0.53×: it makes things worse.

## Where the course uses it
- **L100 #2 and L200 #10.** Interval widths follow σ/√N.
- **L300 #12.** Antithetic 1.46× and control variate 5.40× are the gains predicted by ρ. The reseeding fault set ρ to 0.
- **L300 #16 and L400 #20.** `SeedSequence.spawn` and spawn keys give independent, position-free streams. Counter-based generators make that property structural.
- **L400 #22.** Thinning for non-stationary arrivals is acceptance sampling, a cousin of importance sampling.

## Common misconceptions
- **"Long period means good quality."** RANDU's period from an odd seed is 2²⁹ and it fails in 3-D. Period is necessary, not sufficient.
- **"It passed the chi-square test, so it is random."** A test can only reject. RANDU passes 1-D tests, which is why test batteries (TestU01) run hundreds of tests.
- **"Seeding with time or with consecutive integers gives independent streams."** Use the generator's stream mechanism (spawn, jumped, or a Philox key). Ad-hoc seeding can overlap or correlate streams.
- **"Importance sampling always helps."** A q with lighter tails than fp can give infinite variance, and the estimate looks stable until one huge weight arrives.
- **"Antithetics halve the variance for free."** The gain is 1/(1 + ρ). For symmetric integrands ρ = +1 and antithetics double the variance.

## Check yourself
1. Does a = 1664525, c = 1013904223, m = 2³² have full period? (Yes: c is odd and 4 | a − 1.)
2. How many samples does plain MC of ∫eˣ need for a half-width of 0.001? (929,804)
3. Write the IS weight for target N(0, 1) and proposal N(4, 1). (e^(8 − 4x))

Sources: Hull & Dobell (1962); O'Neill (2014) PCG; Salmon et al. (2011) Random123; the NumPy PCG64 and Philox docs; NIST/SEMATECH e-Handbook 1.3.5.15-16; Owen's *Monte Carlo theory, methods and examples* ch. 8-9 (linked, not copied). Next: ethics of models that decide about people.
