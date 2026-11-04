# L300 research evidence — Simulation (applied), lessons 12-16

Method: SPEC.md research method. All sources were retrieved on 2026-10-28 with web_fetch, or read from a web_search result where marked. Scores are implementable / current / authoritative / open / transferable / depth, 0-2 each; kept at ≥ 8/12. Every number in the L300 concept notes comes from `research/concept_examples_L300.py` (observed output in `concept_examples_L300_observed.txt`), apart from the two lesson 16 timing runs, which were read from `perf.py` output. `research/failure_proofs_L300.py` applies each fix's acceptance check to the faulty and the fixed variant. Observed: all five faults FAIL and all five fixes PASS.

---

## Lesson 12 — Variance reduction
**Questions**
1. What is the variance of the antithetic estimator, when does it help, and how should its CI be computed?
2. What is the optimal control-variate coefficient, and what gain should we expect?
3. How should random streams be organised so that pairs (and CRN) stay synchronised?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Owen, MC book ch. 8 (Variance reduction) | kept | 10 | Var(μ̂_anti) = σ²(1+ρ)/n, monotone f ⇒ ρ < 0, "in the worst case it doubles the variance", analyse pair averages Yᵢ = (f(Xᵢ)+f(X̃ᵢ))/2, efficiency E = c₀σ₀²/(c₁σ₁²), CRN synchronisation |
| NumPy v2.5: Parallel random number generation | kept (reused) | 11 | SeedSequence spawning and `default_rng([worker_id, root_seed])` |
| NumPy v2.5: Random Generator | kept (reused) | 11 | `random`, `exponential` |

**Key facts**
- Antithetic variance σ²(1+ρ)/n with ρ = Corr(f(X), f(X̃)). Monotone f is a "safe harbor", and the worst case doubles the variance. — https://artowen.su.domains/mc/Ch-var-basic.pdf. The lab measures ρ = −0.32 against theory 1/(1+ρ) = 1.48× and an observed 1.46×. tryIt 1 shows a symmetric model at ρ = +1.00 and 0.49×.
- Efficiency compares variance × cost. — same source. The lab therefore reports variance per evaluation.
- Control-variate gain 1/(1 − r²): r = 0.90 gives 5.40×, and the lab measures 5.40×. This is the standard regression result, checked numerically here.
- The Erlang formula for E[(T − s)⁺] is a standard result. It is checked by a 400,000-run test locally and by SciPy `gamma` + `quad` in CI.

## Lesson 13 — Calibration
**Questions**
1. How is a nonlinear least-squares fit computed, and what can go wrong (starting values, local minima)?
2. What is the SciPy equivalent, and what does it return?
3. How do you show that parameters are or are not identifiable from the data?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| NIST e-Handbook 4.1.4.2 Nonlinear LS | kept | 10 | Iterative estimation, starting values "must be reasonably close", local minima, intervals "only approximately correct", outlier sensitivity |
| SciPy 1.18 `least_squares` | kept | 11 | Residual function, `method='lm'`/`'trf'`, result `.x`, `.jac` ("J^T J is a Gauss-Newton approximation of the Hessian") |
| NumPy `linalg.lstsq` | kept | 10 | Linear LS for the polynomial; `rcond` default changed in 2.0 |
| sustainablecatalyst.com calibration article | dropped | 6 | Blog/overview, no runnable code |
| matforge.org calibration techniques | dropped | 5 | Blog, materials-science specific |
| ACM TOMACS "eligibility set" paper | dropped | 7 | Research-level depth, beyond the lesson |
| HAL "identifiability classes" | dropped | 6 | Conference abstract, FE-specific |

**Key facts**
- Nonlinear LS needs starting values, and bad ones converge to a local minimum. — https://www.itl.nist.gov/div898/handbook/pmd/section1/pmd142.htm. The lab starts from physical values.
- `least_squares(fun, x0, method='lm')` takes a residual vector. Its `jac` gives JᵀJ as the Gauss–Newton Hessian approximation. — https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html. That is the basis of `param_report()`'s covariance s²(JᵀJ)⁻¹.
- Observed: same-data selection picks poly-6 (0.148 °C), with holdout 12.517 °C. The time holdout picks two-exp (0.161 °C). A random holdout still picks poly-6. The two-exp model has corr(T_inf, tau_wall) = −0.994, and a 0-5 h fit gives T_inf = −71,014 °C.

## Lesson 14 — Global sensitivity analysis
**Questions**
1. Which estimators does SALib use for S1 and ST, what sample size does Saltelli's design need, and what is the current SALib API and version?
2. How does the Morris method work, and what do μ* and σ mean?
3. Why does OAT miss interactions?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| PyPI SALib | kept | 11 | 1.6.0 (2026-09-19), MIT, py3-none-any, Python ≥ 3.10; quick start |
| SALib Concise API Reference | kept | 11 | `sample.sobol.sample(problem, N, calc_second_order, scramble, seed)` → N(D+2) rows; `analyze.sobol.analyze` "follows [Saltelli 2010] for first and total order"; `sample.saltelli.sample` deprecated since 1.4.6; Morris: `sample(problem, N, num_levels=4, seed)`, `analyze(...)` → mu, mu_star, sigma ("sigma is used as an indicator of interactions") |
| Wikipedia, Variance-based sensitivity analysis | replaced 2026-10-28 (R3-13) | 8 | A, B, AB_i construction, N(d+2) runs, ΣST ≥ 1, ST definition. The estimator formulas were missing from the fetched text |
| Saltelli et al. 2010, Comput. Phys. Commun. 181(2) 259-270 (JRC record JRC52955; author's copy) | kept (primary, 2026-10-28) | 12 | Table 2: (b) S_i = (1/N) Σ f(B)_j (f(A_B^(i))_j − f(A)_j) [this paper]; (f) S_Ti = (1/2N) Σ (f(A)_j − f(A_B^(i))_j)² ('Jansen 1999', best practice); cost N(k+2) for A, B and k matrices A_B^(i) |
| SALib `sobol.py` source on GitHub (raw) | not retrieved | — | web_fetch returned nothing; see KNOWN-GAPS |

**Key facts**
- Saltelli's scheme gives N(D+2) rows without second order, and SALib's Sobol' analysis follows Saltelli et al. 2010 for S1 and ST. — https://salib.readthedocs.io/en/latest/api.html. Confirmed in the primary paper: N(k+2) model runs and the S1/ST estimators (Saltelli et al. 2010, Table 2, https://publications.jrc.ec.europa.eu/repository/handle/JRC52955).
- Morris: μ* is the mean of the absolute elementary effects, and σ indicates interactions. — SALib API page. The lab finds window_open with μ* 100.8 and σ 107.4.
- Analytic check: Var = 3,793.3, ST_window = 0.152, S1_window = 0. The lab estimates 0.155 and 0.005 at N = 8,192, and `test_sensitivity.py` asserts agreement within 0.02.

## Lesson 15 — Co-simulation with FMI
**Questions**
1. What is the current FMI version, what is in an FMU, and how do Co-Simulation and Model Exchange differ?
2. What does a master algorithm call (lifecycle, doStep), and how does FMPy expose it?
3. How does OpenModelica export a Co-Simulation FMU, and which FMI versions does it support?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| FMI Specification 3.0.2 | kept | 11 | FMU = ZIP with modelDescription.xml + binaries/sources; ME, CS, SE; communication points tᵢ, hᵢ = tᵢ₊₁ − tᵢ; CS "contains its own solver"; 3.0 adds early return, Event Mode, Intermediate Update |
| fmi-standard.org | kept (supporting) | 9 | Current release 3.0.2; 290+ tools |
| OpenModelica User's Guide: FMI | kept | 11 | FMI 1.0 deprecated, 2.0.5 supported, 3.0.2 experimental; `buildModelFMU(BouncingBall, version="2.0", fmuType="cs")`; OMEdit File > Export > FMU; default CS integrator forward Euler "an Euler step of communicationStepSize in fmi2DoStep"; 2.0 CS exports "variable communication step size: yes" |
| PyPI FMPy | kept | 10 | 0.3.32 (2026-09-09), FMI 1.0/2.0/3.0, CS and ME, Windows/Linux/macOS |
| FMPy `custom_input.py` | kept | 10 | `FMU2Slave(guid, unzipDirectory, modelIdentifier, instanceName)`, `instantiate`, `setupExperiment`, `enter/exitInitializationMode`, `setReal/getReal`, `doStep(currentCommunicationPoint, communicationStepSize)`, `terminate`, `freeInstance` |
| Gomes et al. 2017, arXiv 1702.00686 | kept (supporting) | 8 | Stable, accurate coupling of simulation units is the main open problem; abstract only |
| iotdigitaltwinplm.com FMPy tutorials | dropped | 5 | Vendor blog with ads; duplicate pages |
| FMI++ Python interface docs | dropped | 7 | A different library; FMPy is the catalog-adjacent choice |

**Key facts**
- FMI 3.0.2 (2024-11-27) is current. An FMU is a ZIP holding modelDescription.xml plus binaries and/or C sources. — https://fmi-standard.org/docs/3.0.2/ ; https://fmi-standard.org/
- OpenModelica supports FMI 2.0.5 and has experimental 3.0.2. The lab therefore exports FMI 2.0 CS. — https://openmodelica.org/doc/OpenModelicaUsersGuide/latest/fmitlm.html
- The FMPy lifecycle used by `fmpy_cosim.FMURoom` matches the FMPy example exactly. — https://github.com/CATIA-Systems/FMPy/blob/main/src/fmpy/examples/custom_input.py
- Stability (our derivation, checked by tests): with K = 12 and τ = 1 h, h_max = τ·ln(12/11) = 313 s. The lab settles at 240 s and oscillates at 300 s and 900 s (6.78 °C). Gauss–Seidel gives h_max = 601 s and is stable at 450 s.

## Lesson 16 — Performance and scale
**Questions**
1. Which start method is the default on Windows and macOS, and what must code do to be spawn-safe?
2. How should independent, reproducible streams be created for parallel workers?
3. Can Lindley's recursion be vectorised?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Python 3.15 docs: multiprocessing | kept | 11 | spawn is the default on Windows and macOS; POSIX default forkserver since 3.14; `if __name__ == '__main__'` guard; targets must be importable/picklable |
| NumPy parallel RNG | kept (reused) | 11 | `SeedSequence(...).spawn(n)`; collision bound n²·2⁻¹²⁸; "UNSAFE! Do not do this!" for root + worker_id |

**Key facts**
- "spawn … The default on Windows and macOS." The functionality "requires that the `__main__` module be importable by the children". — https://docs.python.org/3/library/multiprocessing.html
- Seeding with root + worker_id: "multiple invocations of the program with different seeds will get overlapping sets of worker seeds". — https://numpy.org/doc/stable/reference/random/parallel.html. tryIt 2 observes 7 of 8 streams reused when the root is incremented by one.
- Lindley's waits in closed form, W_n = S_n − min(0, min_k S_k), is a standard identity. Here it is checked against the loop to 9.1e-14 and against a hand-worked case.
