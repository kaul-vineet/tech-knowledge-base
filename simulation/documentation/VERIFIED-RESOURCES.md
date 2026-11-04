# Verified resources — Simulation L100

All URLs were retrieved on 2026-10-28 with web_fetch (or, where marked, read from a web_search result because web_fetch returned no text). Score = implementable + current + authoritative + open + transferable + right depth (0-2 each); kept if ≥ 8/12. **Role**: *primary* = in the lesson's `sources`; *supporting* = used for a version pin, an equivalents line or a cross-check. "Not shown on page" = licence not visible in the retrieved text, so none is claimed.

| Title | URL | Type | Licence | Version / date checked | Score /12 | Used in lesson(s) |
|---|---|---|---|---|---|---|
| PyPI: simpy | https://pypi.org/project/simpy/ | docs (package page) | MIT (stated) | 4.1.2, released 2026-05-23; Python ≥ 3.8 | 11 | 1, 3 (primary); 6 (supporting: tox test suite) |
| PyPI: scipy | https://pypi.org/project/scipy/ | docs (package page) | BSD (stated) | 1.18.1, released 2026-08-21; Python ≥ 3.12 | 10 | 1 (primary) |
| PyPI: Mesa | https://pypi.org/project/Mesa/ | docs (package page) | Apache-2.0 (stated) | 3.5.1 stable, 2026-03-15 (4.0.0a0 pre-release ignored); Python ≥ 3.12; wheel `mesa-3.5.1-py3-none-any.whl` (SimPy 4.1.2 likewise `py3-none-any`) | 10 | 1, 5 (primary) |
| PyPI: numpy | https://pypi.org/project/numpy/ | docs (package page) | BSD-3-Clause AND others (stated) | latest 2.5.4 (2026-10-10); labs pinned to locally validated 2.5.3 | 10 | 1 (supporting) |
| NumPy v2.5 manual: Random Generator | https://numpy.org/doc/stable/reference/random/generator.html | docs | not shown on page | v2.5 | 11 | 1, 2 (primary) |
| Python docs: random | https://docs.python.org/3/library/random.html | docs | not shown on page | 3.15.2 docs | 11 | 6 (primary); 2, 3 (supporting: triangular arg order, expovariate, heapq queue recipe) |
| Python docs: heapq | https://docs.python.org/3/library/heapq.html | docs | not shown on page | 3.15.2 docs | 11 | 3 (primary) |
| Owen, *Monte Carlo theory, methods and examples*, ch. 1-2 | https://artowen.su.domains/mc/Ch-intro.pdf | course/book chapter | © Art Owen; "do not distribute" (read, not copied) | 2009-2013, 2018 | 9 | 2 (primary) |
| NIST/SEMATECH e-Handbook: Confidence limits for the mean | https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm | spec/handbook | US Government work (not shown on page) | checked 2026-10-28 | 10 | 2, 6 (primary) |
| MIT OCW 2.854 (Fall 2016): M/M/1 queue | https://ocw.mit.edu/courses/2-854-introduction-to-manufacturing-systems-fall-2016/927056a1af54772a587fd84ad4951e71_MIT2_854F16_Mm1Queue.pdf | course | MIT OCW terms (page points to ocw.mit.edu/terms; not restated here) | Fall 2016 | 10 | 3, 6 (primary) |
| NUS CS3260 teaching note: M/M/1 model | https://www.comp.nus.edu.sg/~cs3260/MM1.pdf | course | © 2003 I.P.L. Png | 2003 (formula unchanged) | 8 | 3 (supporting: second source for Wq; read via web_search result) |
| SimPy docs: Shared Resources | https://simpy.readthedocs.io/en/latest/topical_guides/resources.html | docs | not shown on page (SimPy is MIT) | 4.1.2.dev docs | 11 | 3 (primary) |
| Python Numerical Methods (UC Berkeley) 22.3 Euler Method | https://pythonnumericalmethods.berkeley.edu/notebooks/chapter22.03-The-Euler-Method.html | course/book | code MIT; text © Elsevier | online edition | 10 | 4 (primary) |
| Python Numerical Methods 22.4 Numerical Error and Instability | https://pythonnumericalmethods.berkeley.edu/notebooks/chapter22.04-Numerical-Error-and-Instability.html | course/book | code MIT; text © Elsevier | online edition | 9 | 4 (supporting: accuracy vs stability) |
| Python Numerical Methods 22.5 Predictor-Corrector and Runge-Kutta | https://pythonnumericalmethods.berkeley.edu/notebooks/chapter22.05-Predictor-Corrector-Methods.html | course/book | code MIT; text © Elsevier | online edition (read via web_search result; the duplicate `.studentorg.berkeley.edu` host dropped 2026-10-28) | 9 | 4 (primary) |
| NASA Glenn: Falling object with air resistance | https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/falling-object-with-air-resistance/ | docs (education) | US Government work (not shown on page) | checked 2026-10-28 | 10 | 4 (primary) |
| NASA Glenn: Flight equations with drag | https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/flight-equations-with-drag/ | docs (education) | US Government work (not shown on page) | checked 2026-10-28 | 10 | 4 (primary) |
| SciPy v1.18 manual: solve_ivp | https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html | docs | not shown on page (SciPy is BSD) | v1.18.0 manual | 11 | 4 (supporting: falling_scipy.py, equivalents) |
| Mesa docs: Schelling Segregation Model | https://mesa.readthedocs.io/stable/examples/basic/schelling.html | docs + repo example | not shown on page (Mesa is Apache-2.0) | stable docs (3.5.x) | 10 | 5 (primary) |
| Mesa docs: Creating Your First Model | https://mesa.readthedocs.io/stable/tutorials/0_first_model.html | docs/tutorial | not shown on page | stable docs; `seed=` kwarg (latest 4.0a0 docs use `rng=`) | 10 | 5 (primary) |
| NetLogo Models Library: Segregation | https://ccl.northwestern.edu/netlogo/models/Segregation | repo/model docs | CC BY-NC-SA 3.0 (stated) | checked 2026-10-28 | 9 | 5 (primary) |
| NetLogo home | https://www.netlogo.org/index | docs | free (stated); licence text not shown | 7.0.4 mentioned in news feed | 8 | 1 (supporting: equivalents) |
| Sargent, V&V of Simulation Models: An Advanced Tutorial (WSC 2020) | https://www.informs-sim.org/wsc20papers/002.pdf | paper/tutorial | © IEEE (read, not copied) | 2020 | 10 | 6 (primary) |
| FMI standard home | https://fmi-standard.org/ | spec | free standard (stated) | FMI 3.0.2 | 9 | 1, 4, 6 (supporting: equivalents) |
| PyPI: FMPy | https://pypi.org/project/FMPy/ | docs (package page) | not shown on page ("free Python library") | 0.3.32, 2026-09-09 | 9 | 1, 4 (supporting: equivalents) |
| OpenModelica home | https://openmodelica.org/ | docs | open source (stated); licence text not shown | v1.27.1, 2026-09-08 | 9 | 1, 4 (supporting: equivalents) |
| DifferentialEquations.jl docs | https://docs.sciml.ai/DiffEqDocs/stable/ | docs | not shown on page | v8.0.1 (docs build) | 9 | 1, 2, 4, 6 (supporting: equivalents) |
| Homebrew formula: python@3.12 | https://formulae.brew.sh/formula/python@3.12 | docs (package index) | Python-2.0 (stated for Python) | 3.12.16; Apple Silicon bottles | 10 | 1 (primary: mac install) |
| microsoft/winget-pkgs: Python.Python.3.12 manifests | https://github.com/microsoft/winget-pkgs/tree/master/manifests/p/Python/Python/3/12 | repo | not shown on page | folders 3.12.0-3.12.10 | 9 | 1 (primary: winget id) |
| Ollama download page | https://ollama.com/download | docs (download) | not shown on page | checked 2026-10-28 (shared catalogue); Windows installer `OllamaSetup.exe` | 9 | 1 (primary: Windows install, per shared WORKSTATION-SETUP) |
| microsoft/winget-pkgs: Ollama.Ollama manifests | https://github.com/microsoft/winget-pkgs/tree/master/manifests/o/Ollama/Ollama | repo | not shown on page | latest folder 0.34.2 (lags the 0.40.12 release) | 9 | background: why winget is not used |
| Homebrew cask: ollama-app | https://formulae.brew.sh/cask/ollama-app | docs (package index) | not shown on page | 0.40.12; macOS ≥ 14 | 9 | 1 (supporting: Mac alternative; default is `brew install ollama` per shared WORKSTATION-SETUP) |
| Ollama docs: macOS | https://docs.ollama.com/macos | docs | not shown on page | checked 2026-10-28; Sonoma 14+, Apple M CPU+GPU | 9 | HARDWARE (supporting) |
| Ollama docs: OpenAI compatibility | https://docs.ollama.com/api/openai-compatibility | docs | not shown on page | checked 2026-10-28; OpenAI-compatible `/v1/chat/completions` | 10 | 6, 7 (primary: agent assist) |
| Ollama library: qwen2.5 | https://ollama.com/library/qwen2.5 | docs (model page) | Apache 2.0 for 1.5b (stated) | `qwen2.5:1.5b` 986 MB | 8 | 1 (supporting: model size) |
| Python docs: venv | https://docs.python.org/3/library/venv.html | docs | not shown on page | 3.15.2 docs; `Activate.ps1`, `Set-ExecutionPolicy ... RemoteSigned -Scope CurrentUser` | 11 | 1 (primary) |
| Python docs: math (CPython implementation detail) | https://docs.python.org/3/library/math.html | docs | not shown on page | 3.15.2 docs; "thin wrappers around the platform C math library" | 10 | HARDWARE (supporting: floating point) |
| Python docs: multiprocessing | https://docs.python.org/3/library/multiprocessing.html | docs | not shown on page | 3.15.2 docs; spawn default on Windows and macOS | 10 | HARDWARE (supporting: cores) |
| NumPy v2.5 manual: random compatibility policy | https://numpy.org/doc/stable/reference/random/compatibility.html | docs | not shown on page | v2.5; "different CPUs implement floating point arithmetic differently" | 11 | HARDWARE (supporting) |
| SciPy v1.18 manual: Toolchain roadmap | https://docs.scipy.org/doc/scipy/dev/toolchain.html | docs | not shown on page | v1.18.0; official builds OSX arm64 (macos-14), Windows (windows-2025) | 10 | 1, HARDWARE (supporting: wheels) |
| GitHub Docs: GitHub-hosted runners reference | https://docs.github.com/en/actions/reference/runners/github-hosted-runners | docs | not shown on page | checked 2026-10-28; macos-latest arm64 M1 3 CPU 7 GB; windows-latest x64 | 10 | CI (supporting) |

**Count:** 41 sources kept: 18 primary + 9 supporting (L100 build) and 14 added for the Mac/Windows + local-agent addendum (4 primary: Homebrew python@3.12, winget Python manifests, Python venv, Ollama OpenAI compatibility). Lessons list 3-7 primary sources (lesson 1: 7, lesson 6: 5 after the addendum).

## L200 additions (lessons 7-11)

Retrieved on 2026-10-28 with web_fetch unless marked. Same scoring and role rules as above. Sources reused from L100 (NIST confidence limits, Python heapq, SimPy Shared Resources, SciPy solve_ivp, Berkeley 22.4, Ollama OpenAI compatibility) are not repeated; their "Used in" now also covers L200 lessons 8-10 and 7 (Ollama).

| Title | URL | Type | Licence | Version / date checked | Score /12 | Used in lesson(s) |
|---|---|---|---|---|---|---|
| NIST/SEMATECH e-Handbook 1.3.5.16: Kolmogorov-Smirnov goodness-of-fit test | https://www.itl.nist.gov/div898/handbook/eda/section3/eda35g.htm | spec/handbook | US Government work (not shown on page) | checked 2026-10-28 | 11 | 7 (primary) |
| NIST/SEMATECH e-Handbook 1.3.6.6.9: Lognormal distribution | https://www.itl.nist.gov/div898/handbook/eda/section3/eda3669.htm | spec/handbook | US Government work (not shown on page) | checked 2026-10-28 | 10 | 7 (primary) |
| NIST/SEMATECH e-Handbook 1.3.3.24: Quantile-quantile plot | https://www.itl.nist.gov/div898/handbook/eda/section3/qqplot.htm | spec/handbook | US Government work (not shown on page) | checked 2026-10-28 | 10 | 7 (primary) |
| SciPy v1.18 manual: scipy.stats.kstest | https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kstest.html | docs | not shown on page (SciPy is BSD) | v1.18.0 manual | 11 | 7 (primary) |
| SciPy v1.18 manual: scipy.stats.lognorm | https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.lognorm.html | docs | not shown on page | v1.18.0 manual; s = sigma, scale = exp(mu) | 11 | 7 (primary) |
| Python docs: statistics (NormalDist) | https://docs.python.org/3/library/statistics.html | docs | not shown on page | 3.15.2 docs | 11 | 7 (primary) |
| MIT 6.263 (Modiano), Lecture 8: M/G/1 queues | https://web.mit.edu/modiano/www/6.263/lec8.pdf | course | MIT (not shown on page) | checked 2026-10-28 | 9 | 7 (primary: P-K formula test oracle) |
| NPTEL Introduction to Queueing Theory (IIT Guwahati, Prof. N. Selvaraju), Lec 15: M/M/c Queues, Erlang Delay Formula | https://nptel.ac.in/courses/111103159 | course (official course page) | not shown on page | checked 2026-10-28; lists Lec 15 (M/M/c, Erlang delay formula); worked example C = 0.702 is in the lecture transcript | 9 | 8 (primary) |
| Technion Service Engineering, QED lecture (Erlang B/C) | https://serveng.technion.ac.il/files/Lectures/QED_lecture_Erlang_B_C.pdf | course | not shown | read via web_search result only | 8 | 8 (supporting: Erlang B for the buildTask) |
| SciPy source: scipy/integrate/_ivp/rk.py | https://github.com/scipy/scipy/blob/main/scipy/integrate/_ivp/rk.py | repo | BSD-3-Clause (SciPy) | main branch, checked 2026-10-28 | 11 | 9 (primary: tableau, step-control constants) |
| Wikipedia: Dormand-Prince method | https://en.wikipedia.org/wiki/Dormand%E2%80%93Prince_method | docs (encyclopedia) | CC BY-SA 4.0 (Wikipedia) | checked 2026-10-28 | 8 | 9 (primary: FSAL, local extrapolation, cross-check) |
| Currie & Cheng, A Practical Introduction to Analysis of Simulation Output Data (WSC 2016) | https://www.informs-sim.org/wsc16papers/013.pdf | paper/tutorial | © IEEE (read, not copied) | 2016 | 11 | 10, 11 (primary: Welch, replications, relative-error rule, CRN) |
| Law, Statistical Analysis of Simulation Output Data: The Practical State of the Art (WSC 2015) | https://www.informs-sim.org/wsc15papers/188.pdf | paper/tutorial | © IEEE (read, not copied) | fetched in full 2026-10-28 (Welch graphical procedure, replication/deletion) | 10 | 10 (primary) |
| Sigman, Columbia IEOR 4404 notes: Inventory models | https://www.columbia.edu/~ks20/4404-Sigman/4404-Notes-inventory.pdf | course | © 2013 Karl Sigman (read, not copied) | 2013 | 9 | 11 (primary) |
| QuantEcon: Inventory Dynamics (Sargent & Stachurski) | https://python.quantecon.org/inventory_dynamics.html | course/book | CC BY-SA 4.0 (stated) | last changed 2026-07-26 | 10 | 11 (primary) |
| NumPy v2.5 manual: Parallel random number generation | https://numpy.org/doc/stable/reference/random/parallel.html | docs | not shown on page (NumPy is BSD) | v2.5 | 11 | 11 (primary: seed lists, SeedSequence) |

**L200 count:** 16 new sources kept (15 primary, 1 supporting), plus 6 reused from L100. Each L200 lesson lists 3-8 sources.

## Clean-up 2026-10-28 (review F10, F14, F16)
- F10: the NPTEL lecture mirror (`kcl.digimat.in`) was replaced by the official course page `nptel.ac.in/courses/111103159`.
- F14: the local model endpoint is configuration, not a source; it no longer appears in this table.
- F16: one host per document. `pythonnumericalmethods.berkeley.edu` is used for all Berkeley chapters, and `www.informs-sim.org` for all WSC papers. The separate "PyPI release files" row was merged into the PyPI Mesa row. The winget Ollama manifest is kept as background only.
- Blogs: none used. Vendor pages: AnyLogic appears only as one `equivalents` line.

## Learning tools
Tool facts (licence, version, Mac/Windows install, URLs) are taken from the shared catalogue `../../shared/LEARNING-TOOLS-CATALOG.md` (checked 2026-10-28 against official sites). They are not re-scored here. The per-lesson list is in `LEARNING-TOOLS.md`, and each lesson's `learningTools[].url` holds the tool's official page.

## L300 (lessons 12-16), retrieved 2026-10-28
Same columns and scoring as above. Reused without re-scoring: NumPy parallel RNG (12, 16), NumPy Random Generator (12), PyPI scipy (12, 13 pins).

| Title | URL | Type | Licence | Version / date checked | Score /12 | Used in lesson(s) |
|---|---|---|---|---|---|---|
| Owen, *Monte Carlo theory, methods and examples*, ch. 8 Variance reduction | https://artowen.su.domains/mc/Ch-var-basic.pdf | course/book chapter | © Art Owen, "do not distribute" (read, not copied) | 2009-2013, 2018 | 10 | 12 (primary: antithetic Var = σ²(1+ρ)/n, monotone ⇒ ρ<0, worst case doubles variance, pair-average CI, CRN, efficiency) |
| NIST/SEMATECH e-Handbook 4.1.4.2 Nonlinear least squares regression | https://www.itl.nist.gov/div898/handbook/pmd/section1/pmd142.htm | spec/handbook | US Government work (not shown on page) | checked 2026-10-28 | 10 | 13 (primary: starting values, local minima, approximate intervals) |
| SciPy v1.18 manual: scipy.optimize.least_squares | https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html | docs | not shown on page (SciPy is BSD) | v1.18.0 page; pin 1.18.1 | 11 | 13 (primary: residual function, method 'lm'/'trf', result .x/.jac) |
| NumPy v2.5 manual: numpy.linalg.lstsq | https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html | docs | not shown on page (NumPy is BSD) | v2.5 | 10 | 13 (primary: polynomial fit; rcond default changed in 2.0) |
| PyPI: SALib | https://pypi.org/project/SALib/ | docs (package page) | MIT (stated) | 1.6.0, released 2026-09-19; py3-none-any wheel; Python ≥ 3.10 | 11 | 14 (primary: pin, quick-start API) |
| SALib documentation: Concise API Reference | https://salib.readthedocs.io/en/latest/api.html | docs | not shown on page (SALib is MIT) | latest docs | 11 | 14 (primary: sample.sobol.sample N(D+2) rows, analyze.sobol.analyze follows Saltelli 2010 for S1/ST, morris sample/analyze mu_star/sigma; saltelli.sample deprecated since 1.4.6) |
| Saltelli, Annoni, Azzini, Campolongo, Ratto, Tarantola (2010), Variance based sensitivity analysis of model output: design and estimator for the total sensitivity index, Comput. Phys. Commun. 181(2) 259-270, doi:10.1016/j.cpc.2009.09.018 | https://publications.jrc.ec.europa.eu/repository/handle/JRC52955 | paper (JRC repository record; formulas read in the author's copy https://www.andreasaltelli.eu/file/repository/PUBLISHED_PAPER.pdf) | © Elsevier; author's copy for non-commercial education use (cited, not copied) | 2010; checked 2026-10-28 | 12 | 14 (primary: A, B, A_B^(i) matrices; cost N(k+2); Table 2 (b) S1 = mean f(B)(f(A_B^(i)) − f(A))/V, (f) Jansen ST = mean (f(A) − f(A_B^(i)))²/(2V) recommended) |
| FMI Specification 3.0.2 | https://fmi-standard.org/docs/3.0.2/ | spec | text CC BY-SA 4.0, code BSD-2-Clause (stated) | 3.0.2, 2024-11-27 | 11 | 15 (primary: FMU = ZIP + modelDescription.xml + binaries/sources; ME/CS/SE; communication points t_i, h_i) |
| Functional Mock-up Interface (home) | https://fmi-standard.org/ | spec (project page) | not shown on page | current release 3.0.2; layered standards listed | 9 | 15 (supporting: current version) |
| OpenModelica User's Guide: Functional Mock-up Interface | https://openmodelica.org/doc/OpenModelicaUsersGuide/latest/fmitlm.html | docs | not shown on page (OpenModelica: OSMC-PL) | v1.28.0-dev page; FMI 2.0.5 supported, 3.0.2 experimental | 11 | 15 (primary: buildModelFMU(..., version="2.0", fmuType="cs"), OMEdit File > Export > FMU, CS default forward Euler) |
| PyPI: FMPy | https://pypi.org/project/FMPy/ | docs (package page) | not shown on page | 0.3.32, released 2026-09-09; py3-none-any wheel; Python ≥ 3.10 | 10 | 15 (primary: FMI 1.0/2.0/3.0, CS and ME, Windows/Linux/macOS) |
| FMPy example: custom_input.py | https://github.com/CATIA-Systems/FMPy/blob/main/src/fmpy/examples/custom_input.py | repo | not shown on page | main branch, checked 2026-10-28 | 10 | 15 (primary: FMU2Slave instantiate/setupExperiment/enter/exitInitializationMode/setReal/getReal/doStep/terminate/freeInstance) |
| Gomes et al., Co-simulation: State of the art (arXiv:1702.00686) | https://arxiv.org/abs/1702.00686 | paper (abstract page) | arXiv licence (not restated) | v1, 2017-02-01; abstract only | 8 | 15 (supporting: stable/accurate coupling is the main research need) |
| Python docs: multiprocessing | https://docs.python.org/3/library/multiprocessing.html | docs | not shown on page | 3.15.2 docs | 11 | 16 (primary: spawn default on Windows and macOS, forkserver default on POSIX since 3.14, main-module guard, picklable top-level targets) |

**L300 count:** 14 new sources kept (11 primary, 3 supporting/background) plus 3 reused. Dropped: see `research/L300-evidence.md` (blogs and vendor tutorials scored ≤ 7).

**R3-13 update (2026-10-28):** the Wikipedia page on variance-based sensitivity analysis was replaced by the primary paper (Saltelli et al. 2010) in lesson 14's sources. The paper's Table 2 confirms the lab's S1 and ST estimators and the N(k+2) cost.


## L400 (lessons 17-21 + capstone 22), checked 2026-10-28
| Title | URL | Type | Licence | Version / date checked | Score /12 | Used in lesson(s) |
|---|---|---|---|---|---|---|
| Welch & Bishop, An Introduction to the Kalman Filter, UNC TR 95-041 | https://techreports.cs.unc.edu/papers/95-041.pdf | report | not shown on page | updated 2004-04-05 | 11 | 17 (primary: eq. 1.9-1.13, innovation) |
| NIST/SEMATECH e-Handbook 6.3.2.3 CUSUM control charts | https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm | docs (government handbook) | U.S. Government work | current | 11 | 17 (primary: tabular CUSUM, k and h) |
| NIST IR 8356, Security and Trust Considerations for Digital Twin Technology | https://nvlpubs.nist.gov/nistpubs/ir/2025/NIST.IR.8356.pdf | report | U.S. Government work | final, Feb 2025 | 9 | 17 (primary: synchronised virtual representation, monitoring and bidirectional links) |
| JSON Lines | https://jsonlines.org/ | spec | not shown on page | current | 9 | 17, 22 (primary: feed format) |
| Fu, Chen & Shi (2008), Some topics for simulation optimization, Proc. WSC | https://informs-sim.org/wsc08papers/006.pdf | paper | © 2008 IEEE (cited, not copied) | 2008 | 12 | 18 (primary: OCBA procedure, Figure 3), 22 (supporting) |
| Kim & Nelson (2001), A fully sequential procedure for indifference-zone selection in simulation, ACM TOMACS 11(3) | https://users.iems.northwestern.edu/~nelsonb/Publications/KimNelsonKN.pdf | paper (author copy) | © 2001 ACM | 2001 | 10 | 18 (primary: indifference zone) |
| Jones, Schonlau & Welch (1998), Efficient global optimization of expensive black-box functions, J. Global Optim. 13 | https://link.springer.com/article/10.1023/A:1008306431147 | paper (publisher page; author PDF used for equations) | © 1998 Kluwer | 1998 | 9 | 18 (primary: expected improvement) |
| Hansen, The CMA Evolution Strategy: A Tutorial | https://arxiv.org/abs/1604.00772 | paper (arXiv) | arXiv licence (not restated) | v2, 2023-03-10 | 9 | 18 (equivalent) |
| Chen, Lin, Yücesan & Chick (2000), DEDS 10:251-270 | (University of Michigan Deep Blue copy; bibliography only) | paper | © 2000 Kluwer | 2000 | 8 | 18 (supporting: original OCBA; rule read in Fu, Chen & Shi) |
| Rasmussen & Williams (2006), Gaussian Processes for Machine Learning, ch. 2 | http://gaussianprocess.org/gpml/chapters/RW2.pdf | book chapter (free online) | © MIT Press, free web edition (no open licence) | 2006 | 11 | 19 (primary: Algorithm 2.1), 18 (supporting) |
| Rahimi & Recht (2007), Random Features for Large-Scale Kernel Machines, NIPS 20 | https://people.eecs.berkeley.edu/~brecht/papers/07.rah.rec.nips.pdf | paper (author copy) | not shown on page | 2007 | 10 | 19 (primary) |
| McKay, Beckman & Conover (1979), Technometrics 21(2) (Latin hypercube) | https://www.jstor.org/stable/1268522 | paper (JSTOR record) | © ASA | 1979 | 9 | 19 (primary) |
| SciPy 1.18: scipy.stats.qmc.LatinHypercube | https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.qmc.LatinHypercube.html | docs | BSD (SciPy) | v1.18.0 | 10 | 19 (equivalent) |
| SQLite: Atomic Commit | https://www.sqlite.org/atomiccommit.html | docs | public domain (SQLite) | current | 12 | 20 (primary) |
| SQLite: Write-Ahead Logging | https://sqlite.org/wal.html | docs | public domain (SQLite) | current (notes the WAL-reset fix in 3.51.3) | 12 | 20 (primary), 22 |
| NumPy v2.5: SeedSequence | https://numpy.org/doc/stable/reference/random/bit_generators/generated/numpy.random.SeedSequence.html | docs | BSD (NumPy) | v2.5 | 11 | 20 (primary: spawn_key), 22 |
| L'Ecuyer, Munger, Oreshkin & Simard (2017), Random numbers for parallel computers, Math. Comput. Simul. 135 | https://www.iro.umontreal.ca/~lecuyer/myftp/papers/parallel-rng-imacs.pdf | paper (author preprint) | not shown on page | preprint 2015-04-17 | 10 | 20 (primary) |
| PyPI: pyarrow | https://pypi.org/project/pyarrow/ | docs (package page) | Apache-2.0 (stated) | 26.0.0, 2026-10-09; Python >= 3.11; macOS arm64 + win_amd64 wheels | 10 | 20 (primary: Parquet export, pending-ci) |
| Apache Parquet: overview | https://parquet.apache.org/docs/overview/ | docs | Apache-2.0 (project) | current | 9 | 20 (supporting) |
| Amdahl (1967), AFIPS Conf. Proc. 30 (IEEE SSCS News reprint) | https://users.cs.duke.edu/~lkw34/papers/amdahl-afips1967.pdf | paper (reprint) | not shown on page | 1967 / reprint 2007 | 8 | 20 (primary: Amdahl's law; the paper has no equations) |
| Sargent (2010), Verification and validation of simulation models, Proc. WSC | https://www.informs-sim.org/wsc10papers/016.pdf | paper | © 2010 IEEE (cited, not copied) | 2010 | 12 | 21 (primary), 22 |
| NASA-STD-7009B Standard for Models and Simulations (catalogue page) | https://standards.nasa.gov/standard/nasa/nasa-std-7009 | standard (catalogue) | public | Version B, 2024-03-05 | 8 | 21 (primary; PDF not opened) |
| US FDA (2023), Assessing the Credibility of Computational Modeling and Simulation in Medical Device Submissions | https://www.fda.gov/regulatory-information/search-fda-guidance-documents/assessing-credibility-computational-modeling-and-simulation-medical-device-submissions | guidance (government) | U.S. Government work | issued 2023-11-17 | 10 | 21 (primary: model influence × decision consequence, after ASME V&V 40) |
| Mitchell et al. (2019), Model Cards for Model Reporting (arXiv:1810.03993) | https://arxiv.org/abs/1810.03993 | paper (arXiv abstract) | arXiv licence (not restated) | FAT* '19 | 9 | 21 (primary) |
| Semantic Versioning 2.0.0 | https://semver.org/ | spec | CC BY 3.0 | 2.0.0 | 10 | 21 (primary) |
| Gans, Koole & Mandelbaum (2003), Telephone Call Centers: Tutorial, Review, and Research Prospects, M&SOM 5(2) | https://faculty.wharton.upenn.edu/wp-content/uploads/2012/04/Gans-Koole-Mandelbaum-CCReview.pdf | paper (author copy) | not shown on page | 2003 | 10 | 22 (primary) |
| Halfin & Whitt (1981), Heavy-traffic limits for queues with many exponential servers, Oper. Res. 29(3) | https://www.columbia.edu/~ww2040/Halfin81.pdf | paper (author copy) | not shown on page | 1981 | 9 | 22 (primary) |
| Lewis & Shedler (1979), Simulation of nonhomogeneous Poisson processes by thinning, NRLQ 26(3) | https://calhoun.nps.edu/server/api/core/bitstreams/45ac1cd2-5bd3-41df-82b4-9902c1dda86e/content | paper (NPS Calhoun) | U.S. Government work (no copyright in the US) | 1979 | 10 | 22 (primary: thinning) |

**L400 count:** 28 sources kept (24 primary, 4 supporting/equivalent), of which 1 is bibliography only. Dropped: Kleijnen (2009), because only a snippet of the bibliography was retrieved; DoD VV&A, because it is military. Details are in `research/L400-evidence.md`. The research sub-agent's fetches of the Python `sqlite3`/`multiprocessing` pages were truncated before the sections we needed (see KNOWN-GAPS).

## L500 (lessons 23-27: theory, ethics, readings), retrieved 2026-10-30
Score rubric as above. "Current" = 2 for classic results that are still standard. Details and dropped candidates: `research/L500-evidence.md`.

| Title | URL | Type | Licence | Version / date checked | Score /12 | Used in lesson(s) |
|---|---|---|---|---|---|---|
| Grinstead & Snell, Introduction to Probability (CHANCE edition) | https://math.dartmouth.edu/~prob/prob/prob.pdf | book | GNU FDL (stated) | version 4 July 2006 (2nd ed., AMS 2003) | 11 | 23 (primary), 27 |
| Gallager, MIT OCW 6.262 ch. 2 Poisson processes | https://ocw.mit.edu/courses/6-262-discrete-stochastic-processes-spring-2011/resources/mit6_262s11_chap02/ | course | MIT OCW terms (not read) | Spring 2011; **search only** | 8 | 23 (further reading) |
| Verschelde, MCS 471 Lecture 30: Runge-Kutta methods (UIC) | https://homepages.math.uic.edu/~jan/mcs471/rungekutta.pdf | course notes | not shown | 31 Oct 2022 | 9 | 24 (primary) |
| Princeton COS 323 (Fall 2011) lecture 19 notes | https://www.cs.princeton.edu/courses/archive/fall11/cos323/notes/cos323_f11_lecture19_pde2.pdf | course notes | not shown | 2011 | 9 | 24 (primary) |
| Goldberg (1991), What Every Computer Scientist Should Know About Floating-Point Arithmetic (Oracle reprint) | https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html | paper | © 1991 ACM, reprinted by permission | 1991 | 10 | 24 (primary) |
| Python docs: Floating-Point Arithmetic: Issues and Limitations | https://docs.python.org/3/tutorial/floatingpoint.html | docs | not shown | 3.15.2 docs | 11 | 24 (primary) |
| Hull & Dobell (1962), Random Number Generators, SIAM Review 4(3) | https://dspace.library.uvic.ca/bitstream/handle/1828/3142/Random_Number_Generators.pdf?sequence=3 | paper (repository copy) | reprinted with SIAM permission | 1962 | 10 | 25 (primary) |
| O'Neill (2014), PCG paper page (HMC-CS-2014-0905) | https://www.pcg-random.org/paper.html | paper page | not shown | 2014 | 9 | 25 (primary) |
| Salmon, Moraes, Dror & Shaw (2011), Parallel Random Numbers: As Easy as 1, 2, 3 (SC11) | https://www.thesalmons.org/john/random123/papers/random123sc11.pdf | paper | © 2011 ACM (personal/classroom copies allowed) | 2011 | 11 | 25 (primary) |
| NumPy docs: PCG64 | https://numpy.org/doc/stable/reference/random/bit_generators/pcg64.html | docs | not shown | v2.5 | 11 | 25 (primary) |
| NumPy docs: Philox | https://numpy.org/doc/stable/reference/random/bit_generators/philox.html | docs | not shown | v2.5 | 11 | 25 (primary) |
| NIST/SEMATECH e-Handbook 1.3.5.15 Chi-Square Goodness-of-Fit | https://www.itl.nist.gov/div898/handbook/eda/section3/eda35f.htm | handbook | not shown (US Government work) | checked 2026-10-30 | 10 | 25 (primary) |
| NIST/SEMATECH e-Handbook 1.3.5.16 Kolmogorov-Smirnov | https://www.itl.nist.gov/div898/handbook/eda/section3/eda35g.htm | handbook | not shown (US Government work) | checked 2026-10-30 | 10 | 25 (primary) |
| Owen, Monte Carlo theory, methods and examples (index; ch. 8 Ch-var-basic.pdf, ch. 9 Ch-var-is.pdf) | https://artowen.su.domains/mc/ | book (in progress) | © Art Owen; "do not distribute" (linked, not copied) | 2013/2018 | 9 | 25 (primary) |
| Ofqual (2020), Awarding GCSE, AS & A levels in summer 2020: interim report (landing page) | https://www.gov.uk/government/publications/awarding-gcse-as-a-levels-in-summer-2020-interim-report | regulator report | not shown (gov.uk) | published 13 Aug 2020 | 11 | 26 (primary) |
| Ofqual interim report, full PDF (executive summary read) | https://assets.publishing.service.gov.uk/media/5f3571778fa8f5173f593d61/6656-1_Awarding_GCSE__AS__A_level__advanced_extension_awards_and_extended_project_qualifications_in_summer_2020_-_interim_report.pdf | regulator report | not shown | Ofqual/20/6656/1 | 11 | 26 (primary) |
| Ofqual (17 Aug 2020), Statement from Roger Taylor, Chair | https://www.gov.uk/government/news/statement-from-roger-taylor-chair-ofqual | regulator statement | not shown (gov.uk) | 17 Aug 2020 | 10 | 26 (primary) |
| OSR (2021), Ensuring statistical models command public confidence | https://osr.statisticsauthority.gov.uk/publications/ensuring-statistical-models-command-public-confidence/ | regulator review | not shown | 2 Mar 2021 | 12 | 26 (primary) |
| ACM Code of Ethics and Professional Conduct | https://www.acm.org/code-of-ethics | professional code | © 2018 ACM; may be republished unchanged with notice | adopted 22 Jun 2018 | 12 | 26 (primary) |
| IEEE Code of Ethics (IEEE Policies 7.8) | https://www.ieee.org/about/corporate/governance/p7-8.html | professional code | not shown | revisions through June 2020 | 11 | 26 (primary) |
| The AQuA Book (2025) | https://www.gov.uk/guidance/the-aqua-book | government guidance | not shown (gov.uk content is normally OGL v3; not claimed) | 30 Jul 2025 | 11 | 26 (primary) |
| HM Treasury (2015), The Aqua Book | https://analysisfunction.civilservice.gov.uk/wp-content/uploads/2018/03/Aqua-Book-4.pdf | government guidance | © Crown 2015, OGL v3 (stated) | Mar 2015 | 10 | 26 (history) |
| NASA-STD-7009B, Standard for Models and Simulations (public PDF) | https://standards.nasa.gov/sites/default/files/standards/NASA/B/1/NASA-STD-7009B-Final-3-5-2024.pdf | standard | cleared for public access (index page) | approved 2024-03-05; front matter + ToC read | 9 | 26 (primary), 21 (upgrade from catalogue page) |
| Royal Commission into the Robodebt Scheme, report page | https://www.royalcommission.gov.au/robodebt/report | inquiry report | © Commonwealth 2023, CC BY 4.0 (on report) | 7 Jul 2023 (PDF links failed; text read from a CC BY copy) | 9 | 26 (contrast) |
| mrc-ide/covid-sim | https://github.com/mrc-ide/covid-sim | repo | GPL-3.0 | fetched 2026-10-30 | 10 | 26 (contrast) |
| Singh Chawla (2020), Critiqued coronavirus simulation gets thumbs up from code-checking efforts, Nature 582 | https://www.nature.com/articles/d41586-020-01685-y | news (journal) | © Springer Nature | 18 Jun 2020 | 9 | 26 (contrast) |
| Metropolis & Ulam (1949), The Monte Carlo Method, JASA 44(247) | https://www.jstor.org/stable/2280232 | paper | JSTOR terms; no open licence (summarised only) | 1949 | 10 | 27 (primary reading) |
| Sargent (2010), Verification and validation of simulation models, Proc. WSC | https://www.informs-sim.org/wsc10papers/016.pdf | paper | © 2010 IEEE (summarised only) | 2010 | 12 | 27 (primary reading), 21, 6 |
| Sargent (2020), Verification and Validation of Simulation Models: An Advanced Tutorial, Proc. WSC | https://www.informs-sim.org/wsc20papers/002.pdf | paper | © 2020 IEEE | 2020 | 10 | 27 (companion) |
| ACM/IEEE-CS/AAAI CS2023 knowledge areas | https://csed.acm.org/knowledge-areas/ | curriculum | not shown | Jan 2024 report | 11 | assessment/syllabus.md |
| ABET Criteria for Accrediting Computing Programs 2026-2027 | https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-computing-programs-2026-2027/ | accreditation criteria | all rights reserved (paraphrased) | 2026-27 | 10 | assessment/syllabus.md |
| ABET Criteria for Accrediting Engineering Programs 2025-2026 | https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-engineering-programs-2025-2026/ | accreditation criteria | all rights reserved (paraphrased) | 2025-26 (2026-27 page search only) | 10 | assessment/syllabus.md |

**L500 count:** 32 sources: 23 primary in a lesson, 9 for history, contrast cases, further reading or the syllabus mappings. Search only: Gallager ch. 2. Not used: Park & Miller (1988; abstract only), the TestU01 page (search only; named in the text without a link) and Imperial Report 9's PDF (search only; the case cites CovidSim through its repo and the Nature article).

