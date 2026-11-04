# L100 research evidence — Simulation (applied)

Method: SPEC.md research method. All sources retrieved 2026-10-28. Score = implementable / current / authoritative / open / transferable / depth (0-2 each); keep ≥ 8/12. Numbers in concept notes come from `research/concept_examples.py` (run, not hand-computed).

---

## Lesson 1 — Set up your simulation workbench
**Questions**
1. What are the current stable versions of SimPy, SciPy, Mesa (and numpy) and their Python requirements?
2. How do I make numpy randomness reproducible, and is the stream stable across versions?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| PyPI simpy / scipy / Mesa / numpy | kept | 10-11 | Authoritative version, date, licence, Python requirement |
| NumPy Random Generator docs | kept | 11 | `default_rng(seed)`, PCG64, seed-42 example values, no cross-version guarantee |
| Mesa 4.0.0a0 pre-release | dropped | — | Pre-release; labs pin stable 3.5.1 |

**Key facts**
- simpy 4.1.2 (2026-05-23), MIT, Python ≥ 3.8. — https://pypi.org/project/simpy/
- scipy 1.18.1 (2026-08-21), BSD, Python ≥ 3.12. — https://pypi.org/project/scipy/
- Mesa 3.5.1 (2026-03-15), Apache-2.0, Python ≥ 3.12; 4.0.0a0 is a pre-release. — https://pypi.org/project/Mesa/
- numpy latest 2.5.4 (2026-10-10); sandbox has 2.5.3, so labs pin 2.5.3. — https://pypi.org/project/numpy/
- `default_rng(seed=42).random((3,3))` starts 0.77395605, 0.43887844, 0.85859792; "Generator does not provide a version compatibility guarantee". — https://numpy.org/doc/stable/reference/random/generator.html (cross-checked: our run prints 0.773956, 0.438878, 0.858598)

## Lesson 2 — Monte Carlo
**Questions**
1. How do I sample a triangular (min, mode, max) duration in numpy, and what is its mean?
2. How do I compute a confidence interval for a Monte Carlo mean, and how does it scale with N?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| NumPy Generator docs (`triangular(left, mode, right)`) | kept | 11 | Current API |
| Owen, Monte Carlo book ch. 1-2 | kept | 9 | Error ~ 1/√n; CI μ̂ ± 1.96 s/√n; copyrighted, link only |
| NIST e-Handbook confidence limits | kept | 10 | Ȳ ± t·s/√N; width shrinks with √N |
| Python random docs (`triangular(low, high, mode)`) | supporting | 11 | Equivalents line: different argument order |
| Generic "Monte Carlo in Python" blogs | dropped | — | Not needed; quality unknown |

**Key facts**
- "the error typically decreases proportionally to 1/√n"; 95% CI μ̂ ± 1.96 s/√n. — https://artowen.su.domains/mc/Ch-intro.pdf
- Confidence limits Ȳ ± t(1−α/2, N−1)·s/√N; "As N increases, the interval gets narrower". — https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm
- Triangular mean (min+mode+max)/3 is used as the exact check; not stated in retrieved text (standard result); lab confirms 17.333 vs sampled 17.334 ± 0.015.

## Lesson 3 — Discrete-event queue
**Questions**
1. How do I implement an event list in the stdlib and keep ties stable?
2. What is the M/M/1 mean wait in queue?
3. What is the current SimPy API for a single-server resource?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Python heapq docs | kept | 11 | heappush/heappop; entry-count tie-breaker; heaps for simulation schedulers |
| MIT OCW 2.854 M/M/1 note | kept | 10 | Wq = λ/(μ(μ−λ)), Ws = 1/(μ−λ) |
| NUS CS3260 M/M/1 note | supporting | 8 | Second source: Wq = λ/(μ[μ−λ]), ρ < 1 required |
| SimPy Shared Resources guide | kept | 11 | `Resource(env, capacity=1)`, `with res.request() as req: yield req` |
| PyPI simpy | kept | 11 | Version, ports (SimSharp, ConcurrentSim, simmer) |

**Key facts**
- heapq "entry count serves as a tie-breaker"; heaps suit "simulation contexts, where the tree holds all incoming events". — https://docs.python.org/3/library/heapq.html
- Wq = 1/(μ−λ) − 1/μ = λ/(μ(μ−λ)). — MIT OCW note (URL in VERIFIED-RESOURCES); same formula in the NUS note.
- SimPy: "Resource is conceptually a semaphore"; request events are context managers. — https://simpy.readthedocs.io/en/latest/topical_guides/resources.html
- Python random docs include a multiserver queue example built on `heapq` + `expovariate`. — https://docs.python.org/3/library/random.html

## Lesson 4 — Time-stepped physics
**Questions**
1. What are the explicit Euler and RK4 update formulas and their orders?
2. What forces act on a falling object; what is terminal velocity?
3. How does SciPy solve an IVP and stop at the ground?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Berkeley Python Numerical Methods 22.3 (Euler) | kept | 10 | S(t+h) = S(t) + h F(t, S); code MIT |
| Berkeley 22.5 (RK4) | kept | 9 | k1..k4, weights 1-2-2-1, O(h⁴); read via web_search |
| Berkeley 22.4 (error/instability) | supporting | 9 | Accuracy O(hᵖ) vs stability |
| NASA Glenn falling object | kept | 10 | W = mg, D = Cd ρ V² A / 2, terminal velocity when D = W |
| NASA Glenn flight equations with drag | kept | 10 | Vt = √(2mg/(Cd ρ A)); a = −g(1 + v²/Vt²) on ascent |
| SciPy solve_ivp docs | supporting | 11 | RK45 default, events with `terminal`/`direction`, rtol 1e-3 / atol 1e-6 defaults |

**Key facts**
- Explicit Euler: S(tj+1) = S(tj) + h F(tj, S(tj)). — https://pythonnumericalmethods.berkeley.edu/notebooks/chapter22.03-The-Euler-Method.html
- RK4 "is fourth-order accurate, or O(h⁴)". — https://pythonnumericalmethods.berkeley.edu/notebooks/chapter22.05-Predictor-Corrector-Methods.html
- g = 9.8 m/s²; drag D = Cd·ρ·V²·A/2; terminal velocity when drag = weight. — https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/falling-object-with-air-resistance/
- Vt = √(2mg/(Cd·ρ·A)). — https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/flight-equations-with-drag/
- solve_ivp events: "terminal ... whether to terminate integration if this event occurs"; "direction ... If direction is positive ...". — https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html

## Lesson 5 — Agent-based modelling
**Questions**
1. What are Schelling's model rules as implemented in widely used OSS ABM tools?
2. What is the current Mesa API for agents on a grid with random activation and seeding?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| NetLogo Segregation model page | kept | 9 | %-SIMILAR-WANTED rule; wrapping topology; 30% wanted → ~70% similar |
| Mesa Schelling example (stable docs) | kept | 10 | CellAgent, OrthogonalMooreGrid(capacity=1), select_random_empty_cell, shuffle_do |
| Mesa "Creating Your First Model" (stable) | kept | 10 | `super().__init__(seed=seed)`, `create_agents`, `agents.shuffle_do` |
| Mesa raw GitHub source v3.5.1 | dropped | — | web_fetch returned no text |
| SIR ABM tutorials | dropped | — | Schelling chosen; Mesa and NetLogo both ship it |

**Key facts**
- "each blue agent wants at least 30% of its neighbors to be blue ... agents end up with (on average) 70% same-color neighbors". — https://ccl.northwestern.edu/netlogo/models/Segregation
- Mesa example: "Unhappy agents will pick a random empty cell to move to each step, until they are happy". — https://mesa.readthedocs.io/stable/examples/basic/schelling.html
- "you can use the seed kwarg ... allowing for the reproducibility of results" (stable); "latest" (4.0a0) docs say `rng`. — https://mesa.readthedocs.io/stable/tutorials/0_first_model.html
- Activation order "can impact the results of the model". — same page

## Lesson 6 — Verification vs validation
**Questions**
1. What is the accepted definition of verification vs validation for simulation models?
2. Which practical techniques (traces, sensitivity, comparison with other models, CIs) are recommended?
3. How do I make a stochastic model's tests reproducible?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Sargent WSC 2020 advanced tutorial | kept | 10 | Formal definitions; traces, reprogramming, parameter variability-sensitivity analysis, replications/CIs |
| Sargent WSC 2007-2011 versions | dropped (duplicates) | — | Same content; 2020 is the newest retrieved |
| NIST confidence limits | kept | 10 | t-interval for replication means |
| Python random docs | kept | 11 | "By reusing a seed value, the same sequence should be reproducible" |
| MIT OCW M/M/1 | kept | 10 | Analytic reference for validation |

**Key facts**
- Verification: "ensuring that the computer program of the computerized model and its implementation are correct"; validation: "substantiation that a computerized model within its domain of applicability possesses a satisfactory range of accuracy consistent with the intended application". — https://www.informs-sim.org/wsc20papers/002.pdf
- Dynamic testing techniques include "traces ... reprogramming critical components"; operational validity should use "parameter variability-sensitivity analysis"; comparisons via graphs, confidence intervals or hypothesis tests, e.g. "using the methods of replication". — same
- "By reusing a seed value, the same sequence should be reproducible from run to run as long as multiple threads are not running." — https://docs.python.org/3/library/random.html

## Equivalents (one line each, all retrieved)
- SimPy (PyPI), Mesa (PyPI + docs), NetLogo (netlogo.org, Models Library), Modelica/OpenModelica (openmodelica.org: v1.27.1), FMI (fmi-standard.org: 3.0.2, Reference FMUs, fmusim) / FMPy (PyPI 0.3.32: `simulate_fmu`), SciPy `solve_ivp` (docs), Julia DifferentialEquations.jl (docs.sciml.ai: ODE/SDE/DAE, ensembles, diffeqpy).

---

## Addendum — Mac mini + Windows paths, local agent (PLATFORM-AGENT-SPEC), 2026-10-28
**Questions**
1. Which exact commands install Python 3.12 and Ollama on macOS (Homebrew) and Windows 11 (winget), and how is a venv activated in PowerShell?
2. Do numpy 2.5.3, SciPy 1.18.1, SimPy 4.1.2 and Mesa 3.5.1 install from wheels on macOS arm64 and Windows x64?
3. Which seeded results can differ between Apple silicon and x64, and why?
4. How can a local model help with a sweep without deciding anything?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Homebrew python@3.12, cask ollama-app | kept | 10 / 9 | Official index: install command, Apple Silicon bottles, macOS ≥ 14 |
| microsoft/winget-pkgs folders (Python.Python.3.12, Ollama.Ollama) | kept | 9 | The manifest repo winget installs from; confirms ids |
| winget.tulio.org / wingetly.io / winget.tech | dropped | — | Third-party mirrors with ads/upsell; used only to find the ids |
| Python docs venv, math, multiprocessing | kept | 10-11 | Activate.ps1 + ExecutionPolicy; libm wrappers; spawn default on macOS/Windows |
| NumPy random compatibility policy | kept | 11 | Same stream only on same build/machine; CPUs differ in edge cases |
| SciPy toolchain roadmap | kept | 10 | Official wheel builds: OSX arm64 (macos-14), Windows (windows-2025) |
| PyPI file lists / JSON API (numpy, scipy) | not retrievable | — | web_fetch returned no file names; CI `--only-binary=:all:` is the check |
| PyPI simpy 4.1.2, Mesa 3.5.1 release files | kept | 10 | `py3-none-any` wheels |
| GitHub-hosted runners reference | kept | 10 | macos-latest = arm64 M1 (3 CPU, 7 GB); windows-latest = x64 |
| Ollama docs macOS, OpenAI compatibility; library qwen2.5 | kept | 8-10 | Apple M CPU+GPU; `/v1/chat/completions`; 1.5b = 986 MB |
| Ollama docs Windows | not retrievable | — | Empty fetch; Windows GPU support not stated |

**Key facts**
- `brew install python@3.12` (stable 3.12.16; bottles for macOS on Apple Silicon). — https://formulae.brew.sh/formula/python@3.12
- winget id `Python.Python.3.12` (manifest folders 3.12.0-3.12.10) and `Ollama.Ollama`. — https://github.com/microsoft/winget-pkgs/tree/master/manifests/p/Python/Python/3/12 , https://github.com/microsoft/winget-pkgs/tree/master/manifests/o/Ollama/Ollama
- PowerShell: `<venv>\Scripts\Activate.ps1`; if blocked, `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`. — https://docs.python.org/3/library/venv.html
- "The math module consists mostly of thin wrappers around the platform C math library functions." — https://docs.python.org/3/library/math.html (cross-check: NumPy policy "different CPUs implement floating point arithmetic differently" — https://numpy.org/doc/stable/reference/random/compatibility.html)
- spawn is "The default on Windows and macOS"; guard with `if __name__ == '__main__'`. — https://docs.python.org/3/library/multiprocessing.html
- SciPy official builds: "OSX arm64 (OpenBLAS) macos-14 … Windows windows-2025". — https://docs.scipy.org/doc/scipy/dev/toolchain.html
- `mesa-3.5.1-py3-none-any.whl`, `simpy-4.1.2-py3-none-any.whl`. — https://pypi.org/project/Mesa/3.5.1/ , https://pypi.org/project/simpy/4.1.2/
- Ollama: macOS Sonoma 14+, "Apple M series (CPU and GPU support)"; OpenAI-compatible base `http://localhost:11434/v1/`; `qwen2.5:1.5b` 986 MB. — https://docs.ollama.com/macos , https://docs.ollama.com/api/openai-compatibility , https://ollama.com/library/qwen2.5
- Measured here (Linux, tracemalloc): lab peaks ≤ 28.9 MiB; Schelling similarity pass 53.4 MiB at 1000×1000. — `research/hardware_measure.py`
- Agent assist with the fake server: lam=1.2 rejected; `0.95`, `19.0` flagged UNVERIFIED. — `research/agent_assist_observed.txt`

