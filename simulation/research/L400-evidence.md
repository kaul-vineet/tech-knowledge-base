# L400 research evidence — Simulation (applied), lessons 17-21 + capstone 22

Method: SPEC.md research method. Sources were retrieved on 2026-10-28 with web_fetch, either directly or by a research sub-agent; any source read only from a search result is marked. Each source is scored 0-2 on six criteria (implementable / current / authoritative / open / transferable / depth) and kept at ≥ 8/12. Civilian sources only: the DoD VV&A material was considered and not used. Every number in the L400 concept notes comes from code that ran:
- `research/concept_examples_L400.py` (observed output in `concept_examples_L400_observed.txt`);
- the lab READMEs, for the storage timings (`storage_options.py`) and the capstone scorecard (`run_capstone.py`).

`research/failure_proofs_L400.py` applies each fix's acceptance check to the shipped and the fixed file (observed output in `failure_proofs_L400_observed.txt`).

---

## Lesson 17 — Digital twins with live data
**Questions**
1. What are the predict and update equations, and what is the innovation?
2. How should a drift detector on residuals be tuned (k, h), and what false-alarm and delay trade-off should we expect?
3. Is there a neutral, current definition of a digital twin that covers two-way data flow?

| Source | Decision | Score | Reason |
|---|---|---|---|
| Welch & Bishop, UNC TR 95-041 (2004) | kept | 11 | Eq. 1.9-1.13; innovation = "measurement innovation, or the residual" |
| NIST/SEMATECH e-Handbook 6.3.2.3 CUSUM | kept | 11 | Tabular S_hi/S_lo; "choose k to be half the δ shift ... h around 4 or 5"; design equations |
| NIST IR 8356 (final, Feb 2025) | kept | 9 | Quotes the description "synchronized at a specified frequency and fidelity"; monitoring and bidirectional links; it is a security report and does not define "digital twin" itself |
| JSON Lines (jsonlines.org) | kept | 9 | UTF-8, one JSON value per line, `\n` terminator (`\r\n` tolerated) |
| Page (1954), Biometrika 41 (archive.org copy) | background | 7 | Original CUSUM; bibliographic check only |

**Key facts:** the lab uses h = 8, deliberately above NIST's rule of thumb of 4-5. tryIt 1 shows h = 4 giving 2 false alarms on this feed, which has noise and a glitch.

## Lesson 18 — Simulation-based optimisation
| Source | Decision | Score | Reason |
|---|---|---|---|
| Fu, Chen & Shi, WSC 2008, "Some topics for simulation optimization" | kept | 12 | OCBA procedure (Figure 3): N_i/N_j = (s_i²/(J_b−J_i)²)/(s_j²/(J_b−J_j)²), N_b = s_b√Σ(N_i/s_i)², n0 ≥ 5, Δ steps; (s, S) with q = S − s as its running example; search vs replication trade-off |
| Chen, Lin, Yücesan & Chick (2000), DEDS 10 (UMich Deep Blue PDF) | kept (bibliography) | 8 | Original OCBA; the fetched text stopped before §3. The rule above is taken from Fu, Chen & Shi |
| Kim & Nelson (2001), ACM TOMACS 11(3) (author PDF) | kept | 10 | Indifference zone: "the smallest actual difference that it is important to detect"; P(CS) guarantee |
| Jones, Schonlau & Welch (1998), J. Global Optimization 13 | kept | 9 | Expected improvement; cross-validated residuals in about [−3, 3]; about 10k initial points |
| Hansen, CMA-ES tutorial, arXiv:1604.00772 | kept (equivalent) | 9 | Evolution-strategy reference for the ES option |

## Lesson 19 — Surrogates
| Source | Decision | Score | Reason |
|---|---|---|---|
| Rasmussen & Williams, GPML ch. 2 | kept | 11 | Algorithm 2.1 (Cholesky, α, predictive variance, log marginal likelihood); © MIT Press, free online, no open licence |
| Rahimi & Recht (2007), NIPS 20 | kept | 10 | z(x) = √(2/D)[cos(ω′x + b)], b ~ U[0, 2π]. ω ~ N(0, I/ℓ²) is our derivation from σ_p² = 2dγ (the table is an image) |
| McKay, Beckman & Conover (1979), Technometrics (JSTOR) | kept | 9 | "N strata of equal marginal probability ... sample once from each" |
| SciPy 1.18 `qmc.LatinHypercube` | kept (equivalent) | 10 | Stratification; `rng` (not `seed`) since 1.15 |
| Kleijnen (2009), EJOR 192 (CentER DP version) | dropped | 7 | Only the bibliography came from a search snippet; the DP text has no explicit metamodel-validation statement |

## Lesson 20 — Large-scale and parallel
| Source | Decision | Score | Reason |
|---|---|---|---|
| SQLite Atomic Commit | kept | 12 | "either all ... or none"; atomic even after a crash or power failure |
| SQLite WAL | kept | 12 | A commit is an appended record; `synchronous=NORMAL` is not durable across power loss; "does not work over a network filesystem"; WAL-reset bug fixed in 3.51.3 |
| SQLite ON CONFLICT / UPSERT | kept (supporting) | 10 | IGNORE skips the conflicting row |
| NumPy v2.5 SeedSequence / parallel RNG | kept | 11 | spawn_key = position in the spawn tree; root + worker_id is "UNSAFE" |
| L'Ecuyer et al. (2017) (author preprint) | kept | 10 | Streams per source, substreams per run; results must not depend on how tasks are assigned to threads |
| PyPI pyarrow 26.0.0; Apache Parquet overview | kept | 10 | Apache-2.0, Python ≥ 3.11, macOS arm64 and win_amd64 wheels; columnar format |
| Amdahl (1967) reprint; Gustafson (1988) | kept / background | 8 / 7 | Amdahl's paper "has no equations": the formula in the lab is the standard reading. Gustafson is listed as background only |
| Python sqlite3 and multiprocessing docs | supporting | 9 | The fetch was cut before the context-manager and `imap_unordered` sections. Behaviour verified by the lab's tests instead (see KNOWN-GAPS) |

## Lesson 21 — Governance and V&V
| Source | Decision | Score | Reason |
|---|---|---|---|
| Sargent, WSC 2010 | kept | 12 | Verification and validation definitions, operational validity, domain of applicability, technique list, step 2 (accuracy before development), step 7 (documentation) |
| NASA-STD-7009B (catalogue page, 2024-03-05) | kept (catalogue only) | 8 | Credibility products in development and use. The PDF was not opened |
| FDA 2023 CM&S credibility guidance | kept | 10 | Model risk = model influence × decision consequence (ASME V&V 40); context of use; not for standalone ML models |
| Mitchell et al. (2019), arXiv:1810.03993 | kept | 9 | Model cards disclose intended use and evaluation procedures. Only the abstract was read; section names not verified |
| SemVer 2.0.0 | kept | 10 | MAJOR.MINOR.PATCH; released contents MUST NOT be modified; CC BY 3.0 |
| DoD VV&A recommended practices | dropped | n/a | Military; the topic is civilian only |

## Capstone 22
| Source | Decision | Score | Reason |
|---|---|---|---|
| Gans, Koole & Mandelbaum (2003), M&SOM (Wharton PDF) | kept | 10 | Service level = fraction answered within a target ("typically 20 or 30 seconds"); Erlang A and abandonment are section headings only (not read in full) |
| Halfin & Whitt (1981), Oper. Res. (Columbia PDF) | kept | 9 | Delay probability → α iff (1 − ρ)√n → β; square-root staffing background |
| Lewis & Shedler (1979), NRLQ (NPS Calhoun; U.S. Government work) | kept | 10 | Thinning: "controlled deletion of points in a Poisson process whose rate function dominates" |
| Fu, Chen & Shi (2008) | reused | 12 | "optimize staffing levels [with queueing models], and then use simulation to test ... and tune" (the capstone's ADR 0001) |
