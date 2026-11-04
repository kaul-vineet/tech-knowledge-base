# L600 #03 An AI agent that runs simulation experiments — and can't fool you — evidence

Checked 2026-10-30. Primary sources only: papers, official docs, specs, and maintained OSS docs. `integrated/research/checks_03.py` recomputes every number in the lesson, the concept note and the question bank (prints OK, exit 0). It does so by re-running the lab code in `integrated/labs/L600/03-agent-driven-simulation` (seed 13, CPython 3.12.15, numpy 2.5.3, Linux x86_64), not by copying numbers.

## Research questions
1. How should the number of replications be chosen for a target precision, and what is a defensible pilot size?
2. Which confidence interval fits the difference of two independently simulated arms with unequal variances?
3. What do JSON Schema range keywords guarantee for tool arguments, and what can they not express (cross-field rules)?
4. How can a seed be derived so that replication i is the same run however many follow, and what does Python promise about reproducing random streams?
5. Does a local OpenAI-compatible server (Ollama) accept `tools` in chat completions, so that the same loop runs against a real model?
6. Which established ideas does the project rest on: V&V before use, Morris screening, and agents that interleave reasoning and tool calls?

## Sources kept (score /12: implementable, current, authoritative, open, transferable, right depth)
| # | Source | URL | Score | Used for | Verified how |
|---|---|---|---|---|---|
| 1 | Hoad, Robinson & Davies (2010), Automated selection of the number of replications for a discrete-event simulation, JORS 61:1632-1644 | https://link.springer.com/article/10.1057/jors.2009.121 | 10 | The problem statement in ADR 0003. Too few replications lose accuracy and precision; too many waste time. An automatable algorithm selects n for a desired precision of the mean. | Abstract and introduction fetched 2026-10-30 (JSTOR/ResearchGate copies of the same paper). The lab's rule (pilot, then n·(h/target)²) is the classic sequential half-width procedure the paper automates. The paper's own algorithm (with a look-ahead) is not implemented. |
| 2 | NIST/SEMATECH e-Handbook 1.3.5.3 Two-Sample t-Test | https://www.itl.nist.gov/div898/handbook/eda/section3/eda353.htm | 12 | `stats.welch_ci`: T with s1²/N1 + s2²/N2. The Welch-Satterthwaite ν formula is "robust for unequal sample sizes and/or unequal variances". | Fetched 2026-10-30. The formula in `stats.welch_ci` matches it term by term. |
| 3 | Sargent (2020), Verification and validation of simulation models: an advanced tutorial, Proc. WSC | https://www.informs-sim.org/wsc20papers/002.pdf | 11 | M1 and the "verified envelope". Validity is "within its domain of applicability", and passing tests at some conditions "does not guarantee that a model is valid everywhere". | Search result text fetched 2026-10-30. The same definitions appear in the 2008/2014 WSC versions. |
| 4 | JSON Schema 2020-12 Validation vocabulary | https://json-schema.org/draft/2020-12/json-schema-validation | 12 | `maximum`/`minimum` are inclusive. `enum`, `required`. "integer" matches any number with a zero fractional part. Each keyword is evaluated independently, so there is no cross-field arithmetic, hence the envelope rule in code. | Fetched 2026-10-30. The ai-agents L200 #8 `schema_check` already implements these keywords (its own test compares with python-jsonschema). |
| 5 | NumPy `SeedSequence` | https://numpy.org/doc/stable/reference/random/bit_generators/generated/numpy.random.SeedSequence.html | 12 | `spawn_key`: "an additional source of entropy based on the position of this SeedSequence in the tree". Logging the entropy gives reproducible bit streams. | Fetched 2026-10-30 (NumPy 2.5 docs). Checked locally: the seeds for reps 0-2 are identical whether 3 or 10 are requested (qbank int03-L600-021, executed). |
| 6 | Python `random`: Notes on reproducibility | https://docs.python.org/3/library/random.html | 12 | Only `random()`'s sequence and a compatible seeder are guaranteed across versions, and `seed(None)` uses OS randomness. These are the scalingLimit on cross-version bit-equality and the `unseeded` fault. | Fetched 2026-10-30. |
| 7 | Python `math` (fsum; module wraps the platform C library) | https://docs.python.org/3/library/math.html | 12 | `math.fsum` "avoids loss of precision by tracking multiple intermediate partial sums", so the mean does not depend on summation order. The math module is mostly "thin wrappers around the platform C math library", which is why bit-equality holds only per environment fingerprint. | Fetched 2026-10-30. The docs also note a possible double-rounding on some non-Windows builds, another reason the fingerprint is stored. |
| 8 | Ollama OpenAI compatibility | https://docs.ollama.com/api/openai-compatibility | 11 | `/v1/chat/completions` lists "Tools" among supported features and `tools` among request fields. The local server ignores the API key. | Fetched 2026-10-30. The `--real-model` path itself is pendingCi. |
| 9 | SALib `analyze.morris` docs | https://salib.readthedocs.io/en/latest/api/SALib.analyze.html | 11 | mu* = mean of the absolute elementary effects. sigma indicates interactions. References Morris (1991) and Campolongo et al. (2007), the same definitions as simulation L300 #14's `morris()`. | Fetched 2026-10-30. The SALib exercise is pendingCi (not installed here). |
| 10 | Yao et al. (2023), ReAct, ICLR | https://arxiv.org/abs/2210.03629 | 10 | Interleaving reasoning and actions (tool calls) reduces hallucination by grounding in an external source. Here the external source is the registry, and the claim checker does the grounding check that ReAct leaves to the model. | Abstract fetched 2026-10-30. |

Reused from earlier KB evidence (not re-fetched): Currie & Cheng (WSC 2016), the Welch warm-up plot in simulation L200 #10, which gives the warm-up of 169 → 200; the Nygard ADR format used across the KB; consumer-driven contracts (application-architecture L300 #14); fitness functions (application-architecture L300 #16).

## Considered and dropped
- Law, *Simulation Modeling and Analysis* (textbook, sequential procedure §9.4): not openly accessible. Hoad et al. cite and automate the same procedure.
- Vendor "AI experiment tracking" product pages: marketing, not primary.
- Blog posts on LLM hallucinated statistics: no runnable method; the lab's checker is the method.

## What was verified locally, and how
| Claim | How |
|---|---|
| Exact t quantiles 4.303 (df 2), 2.262 (df 9); `warmup.t975(2)` = 3.85 | `stats.t_quantile` (regularised incomplete beta + bisection) vs table values; `tests/test_seam_replications.py`; `checks_03.py` |
| M1: 0.992 ± 0.038 vs 1.0; 3.894 ± 0.229 vs 4.0; 8.491 ± 0.817 vs 9.0 | `run_project.verify_model()` (10 runs × 20,000 customers, warm-up 2,000) |
| Sobol' N 64 = 384,000 customers refused; Morris r 10 = 50,000 run; μ* mu 1.72, lam 1.53, warmup 0.74, backlog 0.54 | `pipeline.Pipeline.submit` with seed 13 |
| 3 → 10 → 47 → 55 replications; 4.04 vs 3.14; -0.895 ± 0.293; -22%; arm half-widths 0.23 / 0.19 | Same; the budget ledger |
| 3 replications: 4.28 vs 2.58 (-40%); CI -3.436 to 0.019; half-width 1.728; arm half-widths 2.07 / 1.05 | `Pipeline(policy=naive_policy)` |
| Steady-state difference -0.952 (-23.8%) lies inside the 55-replication CI | M/M/1 formula; `checks_03.py` |
| CRN: n 10, -1.022 ± 0.266, correlation 0.963; ±0.2 target: n 10, required 105, half-width 0.645, budget_limited | `try_it/crn.py`, `try_it/tighter_target.py` |
| Session: 4 sentences, 1 rejected (32.3), 7/7 traced, 160/160 reproduced, 270,000 customers, 5 calls | `run_project.session(None, ...)` with the fake model |
| Faults: few-reps 10/12, no-contract 9/12, no-budget-gate 10/12, unseeded 8/12, all exit 1 | `run_project.py --inject …` (unseeded numbers vary run to run by design) |
| 38 tests OK; build task FAILED (failures=3) on the shipped file | `python -m unittest discover -s tests -v`; `BUILD_TARGET=mine python -m unittest tests.test_build_task` |
| Code-reading answers | `checks_03.py` executes each snippet and compares stdout with the keyed option |

## Gaps
- No real model here. `--real-model` against Ollama (qwen2.5:1.5b) is pendingCi; a real model's plan may differ from the fake's, which can change the "M2 at least one contract rejection" line.
- Bit-for-bit reproducibility has been shown on one Linux environment only. macOS arm64 and Windows runs are pendingCi, and so is whether a registry made on one OS reproduces on another (not expected: libm `log`).
- SALib, SimPy and promptfoo exercises are not run here (packages not installed).
- The claim checker matches numbers by value, not by meaning. A correct value quoted for the wrong quantity passes (documented as a scaling limit).
