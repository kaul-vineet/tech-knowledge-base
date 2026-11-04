# L200 research evidence — Simulation (applied), lessons 7-11

Method: SPEC.md research method. All sources were retrieved on 2026-10-28 with web_fetch, or read from a web_search result where marked. Scores are implementable / current / authoritative / open / transferable / depth, 0-2 each; a source is kept at ≥ 8/12. Every number in the L200 concept notes comes from `research/concept_examples_L200.py` (observed output in `concept_examples_L200_observed.txt`), not from mental arithmetic.

---

## Lesson 7 — Input modelling
**Questions**
1. What are the closed-form estimators (MLE / method of moments) for the exponential, normal and lognormal, so the fits run in numpy alone?
2. How is the KS statistic defined exactly, and is its critical value valid once parameters are estimated?
3. How do I make Q-Q data, and how do the SciPy equivalents (`lognorm.fit`, `kstest`) parameterise the lognormal?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| NIST e-Handbook 1.3.5.16 KS test | kept | 11 | Exact D formula (both sides of each step), limitation: estimated parameters invalidate the critical region, example critical value 0.04301 for N = 1000 |
| NIST e-Handbook 1.3.6.6.9 Lognormal | kept | 10 | MLE: μ̂ = mean of ln X; σ is the sd of the log; CDF Φ(ln x / σ) |
| NIST e-Handbook 1.3.3.24 Q-Q plot | kept | 10 | Definition and use of quantile-quantile comparison |
| SciPy 1.18 `stats.kstest` | kept | 11 | Equivalent API; one-sample statistic, D+ / D− |
| SciPy 1.18 `stats.lognorm` | kept | 11 | `s` = σ, `scale` = exp(μ): the parameter mapping used in `fit_scipy.py` |
| Python docs `statistics.NormalDist` | kept | 11 | `cdf`, `inv_cdf` (stdlib, so no SciPy needed locally) |
| MIT 6.263 lecture 8 (M/G/1, P-K formula) | kept | 9 | W = λE[X²]/(2(1−ρ)), used as the queue test oracle |
| Generic "fit distribution in Python" blogs | dropped | — | Not needed; official docs cover it |

**Key facts**
- KS D = max over i of (F(Yᵢ) − (i−1)/N, i/N − F(Yᵢ)). If the parameters are estimated from the data, "the critical region of the K-S test is no longer valid" and must be found by simulation. — https://www.itl.nist.gov/div898/handbook/eda/section3/eda35g.htm (cross-checked: SciPy kstest docs describe the same one-sample statistic.) Our 1.36/√N reproduces NIST's example critical value 0.04301 for N = 1000.
- Lognormal MLE: μ̂ = Σ ln Xᵢ / N, m̂ = exp(μ̂). — https://www.itl.nist.gov/div898/handbook/eda/section3/eda3669.htm ; SciPy: "Y = exp(X) is lognormally distributed with s = sigma and scale = exp(mu)". — https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.lognorm.html
- P-K: W = λE[X²]/(2(1−ρ)); M/M/1 is the case E[X²] = 2/μ². — https://web.mit.edu/modiano/www/6.263/lec8.pdf (Wikipedia's P-K page, seen in search results, gives the same mean-value form). The lab's lognormal-fed queue is within 5% of it (`test_queue_matches_pollaczek_khinchine`).
- Exponential MLE rate = 1/mean, and the normal's MLE is the mean and the ddof=0 sd. These are standard results; the lab's tests check them against the closed forms, and CI checks them against SciPy's `fit`.

## Lesson 8 — Resources and multi-server queues
**Questions**
1. What are the Erlang C P(wait), Wq and Lq for M/M/c, and is there a worked example to test against?
2. How does SimPy model a pool of c servers (`Resource(capacity=c)`), and what attributes does it expose?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| NPTEL lecture 15 (IIT Guwahati), M/M/c, Erlang delay formula | kept | 9 | p0, Lq, Wq, Erlang C; worked example λ=30, μ=12, c=3 → C = 0.702 (our test reproduces it) |
| SimPy docs: Shared Resources | kept | 11 | `Resource(env, capacity=1)`, `request()` as context manager, `count`, `queue`; also Container `put`/`get`/`level` (lesson 11) |
| Python docs: heapq | kept | 11 | Heap event list (already used in L100) |
| Mitan technical report (Erlang-C theory) | dropped | 7 | Company report; the NPTEL lecture covers the same with a worked example |
| SLM MBA page on M/M/C | dropped | 6 | Course-marketing site |
| Technion QED lecture (Erlang B formula) | supporting (search result only) | 8 | Erlang B = (R^n/n!)/Σ R^j/j! (buildTask solution); not fetched in full |

**Key facts**
- ρ = λ/(cμ) < 1 for stability; Lq = r^c ρ p0 / (c!(1−ρ)²); Wq = Lq/λ; Erlang C C(c, r) = P(wait); example C = 0.702 for λ=30, μ=12, c=3. — lecture 15 transcript, originally read from an unofficial mirror (kcl.digimat.in); official course page listing Lec 15: https://nptel.ac.in/courses/111103159 (review F10, 2026-10-28)
- The lab computes C = (a^c/c!/(1−ρ)) / (Σ_{k<c} a^k/k! + a^c/c!/(1−ρ)), which is the same formula, and `test_textbook_call_centre_example` checks 0.702.
- SimPy Resource: "conceptually a semaphore", `capacity` must be positive, requests usable as context managers. — https://simpy.readthedocs.io/en/latest/topical_guides/resources.html

## Lesson 9 — ODE solvers in practice
**Questions**
1. What are the exact Dormand–Prince coefficients and the error-control constants SciPy uses?
2. What do rtol and atol mean in `solve_ivp`, and what does SciPy advise for stiff problems?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| SciPy source `_ivp/rk.py` (GitHub) | kept | 11 | Tableau C, A, B, E; SAFETY 0.9, MIN_FACTOR 0.2, MAX_FACTOR 10; error exponent −1/(order+1); scale = atol + max(|y|,|y_new|)·rtol |
| SciPy 1.18 `solve_ivp` docs | kept | 11 | Methods; "explicit RK for non-stiff, implicit (Radau, BDF) for stiff"; rtol/atol meaning; events; Lotka–Volterra example (a=1.5, b=1, c=3, d=1, z0 = [10, 5]) |
| Wikipedia: Dormand–Prince method | kept | 8 | FSAL property, 4th/5th order pair, local extrapolation; cross-check of SciPy docs (tableau image not readable as text) |
| Python Numerical Methods 22.4 (Berkeley) | kept (from L100) | 9 | Accuracy vs stability |
| raw.githubusercontent rk.py | dropped | — | web_fetch returned nothing; GitHub HTML view used instead |

**Key facts**
- RK45 "uses the Dormand-Prince pair … error is controlled assuming accuracy of the fourth-order method, but steps are taken using the fifth-order accurate formula." — https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html ; the same text is in the rk.py docstring.
- Tableau and E vector exactly as in rk.py; the lab's tests check row sums = c, Σb = 1, ΣE = 0, and a 5th-order error ratio (> 40 for halving h). — https://github.com/scipy/scipy/blob/main/scipy/integrate/_ivp/rk.py
- "If it makes unusually many iterations, diverges, or fails, your problem is likely to be stiff and you should use 'Radau' or 'BDF'." — solve_ivp docs. Observed: 3,027 explicit steps at rtol 1e-3 and 30,226 at τ = 0.1 ms.
- Lotka–Volterra conserved quantity V = d·x − c·ln x + b·y − a·ln y is a standard result used as an accuracy oracle. No retrieved source states it, so it is listed in KNOWN-GAPS; the drift falls with rtol as expected (1.4e-1 → 3.1e-8).

## Lesson 10 — Warm-up, replications and confidence
**Questions**
1. What exactly is Welch's procedure (replications, window, moving-average formula)?
2. How do I size the number of replications for a target relative precision?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Currie & Cheng, WSC 2016 tutorial | kept | 11 | Welch procedure (n ≥ 5, w ≤ T/4, moving-average formula), MSER-5, batch means, CI, relative-error replication rule, CRN (used in lesson 11 too) |
| Law, WSC 2015 tutorial | kept (search result + abstract) | 9 | Replication/deletion approach; rows are not IID, columns are; independence across runs is the key |
| NIST e-Handbook: confidence limits | kept (from L100) | 10 | t-interval |
| Law WSC 2023 / 2010 / 2004 versions | dropped | — | Same content as the 2015 version |

**Key facts**
- Welch: run n ≥ 5 replications, average point by point, moving average with w ≤ ⌊T/4⌋, and the warm-up is where the curve flattens; with variable data "the decision … can be less clear cut". — https://www.informs-sim.org/wsc16papers/013.pdf (Law 2015 describes the same replication/deletion setup.)
- CI Ȳ ± t(1−α/2, n−1)·S/√n; the CI narrows at rate 1/√n; for relative error ε, stop when t·S/(|Ȳ|√p) ≤ ε/(1+ε). — Currie & Cheng §5.1-5.2 (buildTask rule).
- t quantiles: the lab uses a 2-term Cornish–Fisher expansion and tests it against table values 2.262 / 2.093 / 2.023 / 1.990 (within 0.005); CI also compares it with `scipy.stats.t.ppf`. No retrieved source states the expansion; see KNOWN-GAPS.

## Lesson 11 — (s, S) inventory and common random numbers
**Questions**
1. What is the standard (s, S) model: inventory position, lead times, lost sales vs backlog, cost terms?
2. How should random-number streams be set up so that CRN stays synchronised?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Sigman, Columbia IEOR 4404 inventory notes | kept | 9 | Classic (s, S): order S − I when I < s, random lead time, lost sales, holding cost h per unit time; backlog as an extension |
| QuantEcon Inventory Dynamics (CC BY-SA 4.0) | kept | 10 | (s, S) dynamics "common in practice and also optimal in certain circumstances"; NumPy/JAX code |
| Currie & Cheng WSC 2016 §5.3, §6.1 | kept | 11 | CRN: "the same random numbers … being used to generate the same variables"; paired-difference CI |
| NumPy v2.5 parallel RNG docs | kept | 11 | `default_rng([worker_id, root_seed])` seed lists; SeedSequence spawn |
| SimPy docs: Container | kept (same page as lesson 8) | 11 | `Container(env, init=, capacity=)`, `put`, `get`, `level` |
| U Iowa DTMC (s,S) slides | dropped | 7 | Markov-chain analysis, not simulation |

**Key facts**
- (s, S): when inventory falls below s, order Y = S − I, delivered L (random) time later; demand when I = 0 is lost. — https://www.columbia.edu/~ks20/4404-Sigman/4404-Notes-inventory.pdf. The lab orders on inventory position, so several orders may be outstanding, which Sigman lists as a generalisation.
- CRN reduces the variance of differences; you must make sure "the same random numbers in the stream are being used to generate the same variables". — Currie & Cheng 2016. Observed: correlation 0.90, half-width 0.44 → 0.12.
- Seed lists `[worker_id, root_seed]` give independent, reproducible streams. — https://numpy.org/doc/stable/reference/random/parallel.html. The lab uses `[rep, purpose]`, with the varying ID first as the docs recommend.

## Agent assist (lesson 7)
Same boundary as L100 lesson 6 and PLATFORM-AGENT-SPEC: the agent proposes a candidate name and explains; code decides by KS D and checks numbers. The fake-server rule `[[SIM-FIT]]` is documented in the vendored server's header. Ollama OpenAI-compatibility source is reused from L100.
