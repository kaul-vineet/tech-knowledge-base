"""Build content/L400.json (lessons 17-21 "Design it" + capstone 22) from the metadata below + the lab files on disk.

Run from the domain folder:  python tools/build_l400_json.py
`code` is always read from the lab file, so it stays an exact copy. Solution, ADR, fitness-test and concept-note paths
are checked. L400 adds designBrief, options, decisionRecord, fitnessFunction and scalingLimits (kb/L400-SPEC.md).
"""
import json
import os
import posixpath

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABS = "labs/L400"
ENV = ("Mac mini or Windows 11; Python 3.12 venv (lesson 1); numpy 2.5.3 (+ cryptography 50.0.2 for lesson 21) from "
       "labs/L400/requirements.txt; shared numpy simulators in labs/_shared (qsim, qopt). SDK path: {sdk} (pending CI).")
PLATFORMS = {"mac": "expected", "windows": "expected"}
PLATFORM_NOTE = ("mac/windows 'expected': authored and run on Linux only; lab code uses pathlib, utf-8 file I/O, "
                 "sys.executable, 127.0.0.1 and a FakeClock instead of wall-clock assertions; CI runs tools/run_labs.py on "
                 "macos-latest and windows-latest.")
RAN = "Ran locally (Python 3.12.15, numpy 2.5.3, cryptography 50.0.2, no quantum SDKs in the authoring sandbox): "

S = {  # only URLs retrieved during research (research/L400-evidence.md)
    "ibm_modes": ("Introduction to Quantum Compute execution modes (job, batch, session)", "https://quantum.cloud.ibm.com/docs/en/guides/execution-modes"),
    "sv_sampler": ("StatevectorSampler API", "https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.primitives.StatevectorSampler"),
    "spsa_gains": ("Spall (1998), Implementation of the Simultaneous Perturbation Algorithm for Stochastic Optimization (author's copy)",
                   "https://www.jhuapl.edu/SPSA/PDF-SPSA/Spall_Implementation_of_the_Simultaneous.PDF"),
    "preset": ("Qiskit preset pass managers: optimization levels 0-3", "https://quantum.cloud.ibm.com/docs/en/api/qiskit/transpiler_preset"),
    "transpile": ("qiskit.compiler.transpile API (layout_method, routing_method, seed_transpiler)", "https://quantum.cloud.ibm.com/docs/en/api/qiskit/compiler"),
    "generic": ("GenericBackendV2 API", "https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.providers.fake_provider.GenericBackendV2"),
    "vf2post": ("VF2PostLayout API (error-rate scoring of layouts)", "https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.transpiler.passes.VF2PostLayout"),
    "nishio": ("Nishio et al. (2020), Extracting Success from IBM's 20-Qubit Machines Using Error-Aware Compilation, arXiv:1903.10963",
               "https://arxiv.org/abs/1903.10963"),
    "farhi": ("Farhi, Goldstone, Gutmann (2014), A Quantum Approximate Optimization Algorithm, arXiv:1411.4028", "https://arxiv.org/abs/1411.4028"),
    "kirkpatrick": ("Kirkpatrick, Gelatt, Vecchi (1983), Optimization by simulated annealing, Science 220 (PubMed record)",
                    "https://pubmed.ncbi.nlm.nih.gov/17813860/"),
    "abbas": ("Abbas et al. (2024), Challenges and Opportunities in Quantum Optimization, Nat Rev Phys, arXiv:2312.02279", "https://arxiv.org/abs/2312.02279"),
    "dual_annealing": ("scipy.optimize.dual_annealing (SciPy 1.18.0)", "https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.dual_annealing.html"),
    "fowler": ("Fowler et al. (2012), Surface codes: Towards practical large-scale quantum computation, arXiv:1208.0928", "https://arxiv.org/abs/1208.0928"),
    "gidney2019": ("Gidney & Ekera (2021), How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits, Quantum 5, 433",
                   "https://arxiv.org/abs/1905.09749"),
    "gidney2025": ("Gidney (2025), How to factor 2048 bit RSA integers with less than a million noisy qubits, arXiv:2505.15917",
                   "https://arxiv.org/abs/2505.15917"),
    "beverland": ("Beverland et al. (2022), Assessing requirements to scale to practical quantum advantage, arXiv:2211.07629",
                  "https://arxiv.org/abs/2211.07629"),
    "ross": ("Ross & Selinger (2016), Optimal ancilla-free Clifford+T approximation of z-rotations, arXiv:1403.2975", "https://arxiv.org/abs/1403.2975"),
    "amy": ("Amy, Maslov, Mosca, Roetteler (2013), A meet-in-the-middle algorithm for fast synthesis of depth-optimal quantum circuits, arXiv:1206.0758",
            "https://arxiv.org/abs/1206.0758"),
    "qre_surface": ("qdk.qre.models.qec.SurfaceCode (crossing_prefactor 0.03, error_correction_threshold 0.01)",
                    "https://learn.microsoft.com/en-us/python/qdk/qdk.qre.models.qec.surfacecode?view=qsharp-py"),
    "qre_install": ("How to install and use the Microsoft Quantum resource estimator (qdk.qre)",
                    "https://learn.microsoft.com/en-us/azure/quantum/install-run-resource-estimator"),
    "qre_intro": ("What is the Microsoft Quantum resource estimator?", "https://learn.microsoft.com/en-us/azure/quantum/intro-to-resource-estimation"),
    "qdk_pypi": ("qdk on PyPI (1.33.1)", "https://pypi.org/project/qdk/"),
    "nist8547": ("NIST IR 8547 (final, October 2026), Transition to Post-Quantum Cryptography Standards", "https://nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8547.pdf"),
    "fips203": ("FIPS 203, Module-Lattice-Based Key-Encapsulation Mechanism Standard (ML-KEM)", "https://csrc.nist.gov/pubs/fips/203/final"),
    "cswp39": ("NIST CSWP 39, Considerations for Achieving Cryptographic Agility (2025; superseded by CSWP 39upd1)",
               "https://csrc.nist.gov/pubs/cswp/39/considerations-for-achieving-cryptographic-agility/final"),
    "roetteler": ("Roetteler et al. (2017), Quantum resource estimates for computing elliptic curve discrete logarithms, arXiv:1706.06752",
                  "https://arxiv.org/abs/1706.06752"),
    "crypto_mlkem": ("cryptography: ML-KEM key encapsulation (MLKEM768PrivateKey, added in 47.0.0)",
                     "https://cryptography.io/en/latest/hazmat/primitives/asymmetric/mlkem/"),
    "mitiq_rem": ("Mitiq 1.1.0: How do I use REM?", "https://mitiq.readthedocs.io/en/stable/guide/rem-1-intro.html"),
    "ollama_openai": ("Ollama: OpenAI compatibility (/v1/chat/completions)", "https://docs.ollama.com/api/openai-compatibility"),
}


def src(*keys):
    return [{"title": S[k][0], "url": S[k][1]} for k in keys]


def step(title, detail, expected, if_not, mac=None, windows=None):
    out = {"title": title, "detail": detail, "expected": expected, "ifNot": if_not}
    if mac:
        out["mac"], out["windows"] = mac, windows
    return out


def build_step(mine, naive, expected, if_not):
    """buildTask check against YOUR file (BUILD_TARGET=mine) and the fail-before proof on the shipped (unfixed) lab file."""
    cmd = "python -m unittest test_build_task test_fitness -v"
    return step("Build task: make the design decision true, then prove it",
                f"Write {mine}.py (see buildTask), run the build-task and fitness tests against it, then against the shipped lab "
                f"module ({naive}), which must fail.", expected, if_not,
                f"BUILD_TARGET=mine {cmd}; BUILD_TASK_MODULE={naive} {cmd}",
                f'$env:BUILD_TARGET = "mine"; {cmd}; Remove-Item Env:BUILD_TARGET; $env:BUILD_TASK_MODULE = "{naive}"; {cmd}; '
                "Remove-Item Env:BUILD_TASK_MODULE")


SDK_MAC = "python -m pip install -r labs/L400/requirements-sdk.txt"
SDK_WIN = "python -m pip install -r labs\\L400\\requirements-sdk.txt"
MANUAL = "Pending a manual run (tool not runnable in the authoring sandbox). "
QVIS = {"name": "Qiskit visualization (qiskit.visualization)", "role": "SEE", "mac": "pip install 'qiskit[visualization]'",
        "windows": "pip install \"qiskit[visualization]\"", "licence": "Apache-2.0 (OSI: yes)",
        "url": "https://quantum.cloud.ibm.com/docs/en/api/qiskit/visualization"}
JUPYTER = {"name": "JupyterLab (+ JupyterLab Desktop)", "role": "CHECK", "mac": "pip install jupyterlab, or Desktop arm64 installer",
           "windows": "pip install jupyterlab, or Desktop x64 installer / winget install jupyterlab", "licence": "BSD-3-Clause (OSI: yes)",
           "url": "https://pypi.org/project/jupyterlab/"}
MARIMO = {"name": "marimo", "role": "SEE", "mac": "pip install marimo (marimo tutorial intro)", "windows": "pip install marimo (marimo tutorial intro)",
          "licence": "Apache-2.0 (OSI: yes)", "url": "https://pypi.org/project/marimo/"}
QDK = {"name": "Microsoft Quantum Development Kit (qdk + VS Code extension)", "role": "CHECK",
       "mac": "pip install qdk ; VS Code extension 'Microsoft Quantum Development Kit (QDK)' (or vscode.dev/quantum/playground)",
       "windows": "pip install qdk ; same VS Code extension", "licence": "MIT (OSI: yes)", "url": "https://pypi.org/project/qdk/"}
MITIQ = {"name": "Mitiq", "role": "CHECK",
         "mac": "pip install mitiq (Python >=3.11,<3.13; Cirq is a core dependency; add mitiq[qiskit] for Qiskit circuits)",
         "windows": "pip install mitiq (same Python range; PyPI classifiers list macOS and Windows)", "licence": "GPL-3.0 (OSI: yes)",
         "url": "https://pypi.org/project/mitiq/"}


def tool(base, exercise, expected, role=None):
    return {"name": base["name"], "role": role or base["role"], "exercise": exercise, "expected": MANUAL + expected,
            "mac": base["mac"], "windows": base["windows"], "licence": base["licence"], "url": base["url"]}


L17 = {
    "dir": "17-hybrid-architecture", "file": "orchestrator.py", "id": "hybrid-architecture", "number": 17,
    "title": "Hybrid quantum-classical architecture: orchestrator, job queue and backend adapter",
    "phase": "Design", "category": "hybrid architecture",
    "description": "Design the loop around a variational algorithm: an orchestrator with a job queue policy, a transpile cache and retries, behind a backend adapter; compare sync, batched and session execution on a fake clock.",
    "outcome": "You can separate optimiser, orchestrator and backend; choose an execution mode from measured wall time, billed time and job counts; key a transpile cache correctly; make retries idempotent; and keep the decision true with a fitness test.",
    "sdk": "qiskit 2.6.1 StatevectorSampler with a PUB parameter array per step + generate_preset_pass_manager on GenericBackendV2 (sampler_qiskit.py)",
    "estimatedTime": "60-90 minutes",
    "overview": ["The circuit is the easy part: on shared devices the queue, the compiler and failed jobs decide how long a variational run takes and what it costs."],
    "prerequisites": ["Lesson 14 (QAOA on MaxCut)", "Lesson 15 (SPSA under shot noise)", "Lesson 11 (transpiling to a device)",
                      "distributed-systems L100 #4 retries and L300 #16 backpressure (helpful, not required)"],
    "glossary": [
        {"term": "orchestrator", "meaning": "Code between optimiser and backend that owns batching, caching and retries."},
        {"term": "backend adapter", "meaning": "A small interface (transpile, run, open/close session) that hides a simulator or provider."},
        {"term": "batched job", "meaning": "One submission that carries every circuit of one optimiser step (Qiskit: one PUB with a parameter array)."},
        {"term": "session", "meaning": "A reserved device window: later jobs skip the queue, the whole window is billed, an interactive TTL ends it."},
        {"term": "idempotent retry", "meaning": "Re-running a failed job gives exactly the same result because each circuit carries its seed."},
        {"term": "FakeClock", "meaning": "A modelled clock that the code advances; tests stay deterministic and never sleep."},
    ],
    "concepts": ["Execution mode is an architecture decision with measurable cost.", "Cache compiled circuits by structure and target, never by angle.",
                 "Retries must not change the answer.", "Fitness tests keep the decision true as code changes."],
    "steps": [
        step("Run the lab", "python orchestrator.py  (shipped code: naive cache key)",
             "sync wall 606.3 s, batched 186.3 s, session 131.2 s; transpiles 240 in every mode; best_ratio 0.6922 everywhere.",
             "ModuleNotFoundError qopt: run from the lab folder so labs/_shared is on the path."),
        step("Read the JSON lines", "Compare wall_s, billed_s, jobs and transpiles per mode.",
             "Jobs 240 vs 30 vs 30; billed 4.8 s for sync/batched but the whole window (131.2 s) for the session.",
             "Different numbers: check Costs() (queue 2 s, 0.02 s per circuit, transpile 0.5 s, session gap 0.1 s)."),
        step("See the fault", "transpiles = 240 = circuits: the cache key contains the bound angles, so nothing is reused.",
             "cache_hits 0 in every line; the last line shows 3 retries for seeded failures and the same best_ratio 0.6922.",
             "cache_hits > 0: you already changed cache_key."),
        step("Run the decided design", "python solution_cache_key.py",
             "sync 486.8 s, batched 66.8 s, session 11.7 s (billed 11.7 s); 1 transpile, 239 cache hits.",
             "Still 240 transpiles: the key must ignore params and include target and optimisation level."),
        step("Try it", "python try_it.py", "busy queue: batched 906.8 s vs session 39.7 s; 70 s classical step: session billed 2165.3 s for no wall-time gain.",
             "Compare with the tryIt predictions."),
        build_step("my_cache_key", "orchestrator",
                   "Your file / solution: Ran 7 tests ... OK. Shipped orchestrator: FAILED (failures=4) - 240 != 1 transpiles, angles in the key, wall 186.3 > 90.",
                   "A different backend target must give a different key (no stale reuse)."),
        step("Run all tests (and the Qiskit path in CI)", "python -m unittest -v; SDK: python sampler_qiskit.py",
             "Ran 16 tests ... OK (skipped=1 Qiskit test). CI: batched = 1 transpile and 5 jobs for 5 steps; sync = 40 jobs.",
             "Qiskit import errors: install labs/L400/requirements-sdk.txt (Python 3.11+).",
             SDK_MAC + " && python labs/L400/17-hybrid-architecture/sampler_qiskit.py",
             SDK_WIN + "; python labs\\L400\\17-hybrid-architecture\\sampler_qiskit.py"),
    ],
    "codeWalkthrough": [
        {"title": "Template / Circuit (backend.py)", "detail": "A Template is circuit STRUCTURE (graph, depth p); a Circuit binds angles and carries its own seed - the seed is what makes a retry reproduce the same samples."},
        {"title": "SimulatorBackend.run", "detail": "One job = a list of circuits. It advances the FakeClock by a queue wait (or the session gap) plus 0.02 s per circuit, enforces max_circuits and raises TransientBackendError on seeded attempts."},
        {"title": "Orchestrator.compiled + cache_key", "detail": "The transpile cache. The shipped key includes the bound params, so 240 circuits cause 240 transpiles; the build task keys on structure + target + level."},
        {"title": "Orchestrator.submit", "detail": "Retries up to 4 attempts with exponential backoff (1, 2, 4 s on the fake clock). Same seeds -> same samples, so a retry never changes the optimiser's path."},
        {"title": "Orchestrator.evaluate", "detail": "The job-queue policy: 'sync' submits one job per circuit, 'batched'/'session' one job per optimiser step."},
        {"title": "spsa_multistart", "detail": "The classical side only ever asks for values of 8 circuits per step (4 starts x +/- perturbation) - it cannot tell which execution mode ran them."},
        {"title": "run(mode, ...)", "detail": "Opens/closes a session when asked and reports wall_s, billed_s (QPU seconds or the session window), jobs, transpiles, hits and retries as one JSON line."},
    ],
    "designBrief": {
        "context": "A multi-start SPSA QAOA loop (4 starts x 30 iterations = 240 circuits of one template) must run on a shared backend with a 2 s queue per job, 0.5 s per transpile and occasional transient job failures.",
        "constraints": ["modelled wall time <= 90 s for the reference workload", "billed device time <= 5 s", "<= 1 job per optimiser step",
                        "exactly 1 transpile per template and target", "a transient failure must not change the result"],
        "question": "Which execution mode (sync loop, batched jobs, session) and which cache/retry policy should the service use by default?"},
    "options": [
        {"name": "Synchronous loop (one job per circuit)", "description": "Submit each circuit as soon as the optimiser asks for it.",
         "evidence": "486.8 s modelled wall, 4.8 s billed, 240 jobs (with the structural cache); 7206.8 s with a 30 s queue.", "verdict": "Rejected: queue-dominated."},
        {"name": "Batched jobs (one job per optimiser step)", "description": "Submit all circuits of an SPSA step together; structural transpile cache; idempotent retries.",
         "evidence": "66.8 s wall, 4.8 s billed, 30 jobs, 1 transpile; 3 seeded failures add 10.0 s and leave best_ratio 0.6922 unchanged.", "verdict": "Chosen (ADR 0001)."},
        {"name": "Session + batches", "description": "Reserve the device; jobs after the first skip the queue; billed for the window.",
         "evidence": "11.7 s wall but 11.7 s billed (2.4x); with a 70 s classical step the TTL expires and billing reaches 2165.3 s for the same wall time as batched.",
         "verdict": "Opt-in for interactive work only."},
    ],
    "decisionRecord": "labs/L400/17-hybrid-architecture/docs/adr/0001-batched-jobs.md",
    "fitnessFunction": {"what": "The default mode stays 'batched'; one job per optimiser step; one transpile per template; wall and billing within budget.",
                        "test": "labs/L400/17-hybrid-architecture/test_fitness.py",
                        "threshold": "jobs <= 30, transpiles == 1, modelled wall <= 90 s, billed <= 5 s for the reference workload"},
    "scalingLimits": ["Queue-dominated wall time: when jobs x queue >> execution (signal: wall_s >> billed_s), batch more per job or consider sessions.",
                      "Provider batch limits (max_circuits): the adapter raises ValueError; chunking adds one queue wait per chunk.",
                      "Adaptive ansaetze create new templates each step: cache hit rate falls below ~0.99 and transpile time returns."],
    "failureLab": {"fault": "The transpile-cache key includes the bound parameter values (the shipped orchestrator.cache_key).",
                   "symptom": "transpiles = 240 = circuits and cache_hits = 0 in every mode; batched wall 186.3 s instead of 66.8 s; the fitness test fails (240 != 1, 186.3 > 90).",
                   "fix": "Key the cache on template structure + backend target + optimisation level, never on params (solution_cache_key.py).",
                   "proof": "BUILD_TASK_MODULE=orchestrator python -m unittest test_build_task test_fitness -> FAILED (failures=4); default (solution) and BUILD_TARGET=mine -> Ran 7 tests OK."},
    "tradeOffs": [
        {"option": "Sync loop", "gains": "Simplest code; matches tutorials; easy to debug one circuit at a time", "costs": "Pays the queue per circuit (486.8 s)", "chooseWhen": "Local simulators and tiny experiments"},
        {"option": "Batched jobs", "gains": "One queue wait per step; billed only for execution", "costs": "Needs an optimiser that produces several circuits per step; batch-size limits", "chooseWhen": "Default for shared devices (ADR 0001)"},
        {"option": "Session", "gains": "Lowest wall time (11.7 s) and predictable access", "costs": "Billed for the window, plan restrictions, interactive TTL expiry", "chooseWhen": "Interactive work with fast classical steps"},
    ],
    "buildTask": {"task": "Write cache_key(template, params, backend, opt_level=1) so one parameterised template is compiled once per target and level, and any change of structure, target or level misses the cache.",
                  "hints": ["The key must not contain params at all.", "Include backend.target: a cached circuit for another device is wrong.",
                            "Include template.p: a deeper circuit is a different structure."],
                  "solution": "labs/L400/17-hybrid-architecture/solution_cache_key.py",
                  "check": "BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v (7 tests; numpy, runs locally)"},
    "expectedResults": ["Same best_ratio 0.6922 in every mode and with injected failures", "Batched 66.8 s / 4.8 s billed / 30 jobs / 1 transpile",
                        "Session 11.7 s wall but billed for the whole window"],
    "testCases": [{"action": "run('batched', key=solution) with fail_jobs=(3, 4, 17)", "expected": "3 retries, +10.0 s, identical best_ratio"},
                  {"action": "Orchestrator.submit with 6 circuits on max_circuits=5", "expected": "ValueError before submission"},
                  {"action": "sampler_qiskit.run('batched', iters=5) (CI)", "expected": "1 transpile, 5 jobs"}],
    "tryIt": [
        {"task": "Raise the queue to 30 s per job (try_it.busy_queue).", "predict": "Does batching still beat a session?",
         "expected": "No: sync 7206.8 s, batched 906.8 s, session 39.7 s (billed 39.7 s). Long queues push toward sessions.", "validatedBy": "local: try_it.py (observed)"},
        {"task": "Make the classical step 70 s (> the 60 s interactive TTL) (try_it.slow_classical_step).", "predict": "What happens to the session?",
         "expected": "Every job re-queues: session wall 2165.3 s = batched, but billed 2165.3 s vs 4.8 s.", "validatedBy": "local: try_it.py (observed)"},
    ],
    "troubleshooting": [{"symptom": "best_ratio differs between modes", "action": "A circuit seed depends on the attempt or the mode; derive it from (run seed, iteration, start, sign) only."},
                        {"symptom": "TransientBackendError escapes", "action": "Four consecutive failures exhaust max_attempts; that is the intended give-up - raise it to the caller."}],
    "equivalents": ["Qiskit Runtime: mode=backend (job), mode=batch / Batch context, mode=session / Session context (execution-modes guide).",
                    "Qiskit primitives: one PUB with a parameter array = one batched job; transpile once with Parameter objects, bind per run.",
                    "Any job queue (Celery, cloud task queues) with idempotency keys gives the same retry semantics."],
    "inRealSystems": ["Cloud QPUs queue jobs for seconds to hours; providers expose batch and session modes for exactly this trade-off.",
                      "Production loops cache ISA circuits per backend calibration and bind parameters late."],
    "useWhen": "Use an orchestrator + adapter as soon as circuits leave your laptop; avoid sessions unless wall time matters more than the billed window.",
    "simulatorVsReal": "Numpy QAOA sampler behind the adapter; time is modelled with a FakeClock using illustrative costs (2 s queue, 0.5 s transpile). Real queues vary by hours and providers bill differently.",
    "checkYourself": [{"q": "Why are billed seconds equal for sync and batched?", "a": "Both pay only execution (240 x 0.02 s); the difference is queue waiting, which is wall time, not device time."},
                      {"q": "What makes a retry safe here?", "a": "Each circuit carries a seed chosen by the orchestrator, so re-running gives identical samples."},
                      {"q": "Why include the target in the cache key?", "a": "A circuit compiled for one device is invalid on another; a key without it would reuse the wrong ISA circuit."}],
    "checkpoint": "PASS if you can explain the three modes' wall vs billed numbers, your cache key passes test_build_task and test_fitness, and the shipped key fails them.",
    "learningTools": [
        tool(MARIMO, "Create a notebook with `marimo edit`: sliders for queue_s (0.5-60), classical_s (0.01-90) and a cell calling try_it.compare(backend.Costs(queue_s=...), classical_s=...).",
             "Default costs reproduce batched (66.8, 4.8) and session (11.7, 11.7); queue 30 s gives (906.8, 4.8) vs (39.7, 39.7); classical 70 s makes session billing 2165.3 s."),
        tool(JUPYTER, "Load the JSON lines of solution_cache_key.py into a notebook and plot wall_s and billed_s per mode as grouped bars.",
             "Bars: sync 486.8/4.8, batched 66.8/4.8, session 11.7/11.7 (the lab README output)."),
    ],
    "seeAlso": ["distributed-systems L100 #4 Retries with exponential backoff, jitter and a retry budget: the orchestrator's retry policy, here with idempotent per-circuit seeds.",
                "application-architecture L300 #13 Resilience patterns: timeouts, circuit breaker, bulkhead, fallback: the backend adapter is the place for these patterns.",
                "L400 #22 Capstone: an end-to-end quantum optimisation service: reuses this orchestrator and cache key unchanged."],
    "sources": src("ibm_modes", "sv_sampler", "spsa_gains", "transpile"),
    "next": "L400 #18 Benchmarking honestly against classical solvers: once execution is cheap and reliable, find out whether the quantum solver is worth running at all.",
    "how": RAN + "`python orchestrator.py`, `python solution_cache_key.py`, `python try_it.py` (outputs in README); `python -m unittest` -> 16 tests OK, 1 Qiskit test skipped; fail-before proof with BUILD_TASK_MODULE=orchestrator observed (4 failures).",
    "pendingCi": ["sampler_qiskit.py (Qiskit StatevectorSampler + generate_preset_pass_manager on GenericBackendV2)", "test_try_it.py QiskitPath (1 test)"],
    "projectFiles": [("orchestrator.py", "main lab: orchestrator, job-queue policy, naive cache key, retries, SPSA workload"),
                     ("backend.py", "adapter interface: FakeClock, Template/Circuit, SimulatorBackend (seeded faults, sessions, max_circuits)"),
                     ("solution_cache_key.py", "buildTask reference: structural cache key"), ("buildtarget.py", "BUILD_TARGET=mine / BUILD_TASK_MODULE switch"),
                     ("test_build_task.py", "buildTask + failureLab proof"), ("test_fitness.py", "fitness function for ADR 0001"),
                     ("test_orchestrator.py", "modes, retries, batch limit"), ("sampler_qiskit.py", "SDK path: Qiskit primitives (CI)"),
                     ("docs/adr/0001-batched-jobs.md", "decision record"), ("README.md", "run commands and observed output"),
                     ("../../_shared/qopt/maxcut.py", "shared MaxCut + vectorised QAOA (self-tested)")],
    "summary": "Separate optimiser, orchestrator and backend adapter. Measure execution modes on a fake clock: batched jobs cut wall time 7x versus a sync loop at the same billed time; sessions are fastest but bill the window. Cache compiled circuits by structure and target, make retries idempotent with per-circuit seeds, and guard the decision with a fitness test.",
}


L18 = {
    "dir": "18-benchmark-vs-classical", "file": "bench_lab.py", "id": "benchmark-vs-classical", "number": 18,
    "title": "Benchmarking honestly against classical solvers",
    "phase": "Design", "category": "benchmarking",
    "description": "Compare QAOA with exact, greedy and simulated-annealing MaxCut solvers at sizes the simulator handles; fix a biased comparison method and guard it with a fitness test.",
    "outcome": "You can design a fair benchmark (same budget, same seeds, medians, enforced budgets), compute quality and time-to-solution, let code pick the winner, and explain when quantum is not the right tool.",
    "sdk": "qiskit 2.6.1 StatevectorSampler sampling the same QAOA circuit (bench_qiskit.py)",
    "estimatedTime": "60-90 minutes",
    "overview": ["A benchmark is an experiment: hold the instance, seeds and budget fixed, vary only the solver, and report distributions - otherwise a 'quantum win' is an artefact of the method."],
    "prerequisites": ["Lesson 14 (QAOA on MaxCut)", "Lesson 16 (classifier vs a classical baseline)", "Lesson 17 (what a job costs)"],
    "glossary": [
        {"term": "sample", "meaning": "One candidate bitstring evaluated: a classical flip evaluation or one quantum shot - the budget unit."},
        {"term": "approximation ratio", "meaning": "Best cut found / exact optimum (1.0 = optimal)."},
        {"term": "success rate", "meaning": "Fraction of seeds whose run found the exact optimum."},
        {"term": "TTS99", "meaning": "Samples needed for 99 % confidence of seeing the optimum at least once: budget x ln(0.01) / ln(1 - success)."},
        {"term": "simulated annealing", "meaning": "Metropolis single flips with a temperature that falls on a schedule (Kirkpatrick et al. 1983)."},
    ],
    "concepts": ["Same budget, same seeds, medians: the method is what you defend.", "Exact enumeration is the reference at simulator sizes.",
                 "One instance proves nothing; check other instances.", "Code decides the winner with a rule written in advance."],
    "steps": [
        step("Run the biased benchmark", "python bench_lab.py", "n = 12: QAOA ratio 1.0 vs greedy 0.8 and annealing 0.8667 -> {\"winner\": \"qaoa\"}.",
             "Different numbers: check SIZES (8, 12, 16), SEEDS 0-9, BUDGET 200."),
        step("Find the bias", "Read compare(): BOOST, seeds[:1], max(results).",
             "QAOA got 800 samples and its best of 10 seeds; the baselines got 50 samples and one seed; every row still claims budget 200.",
             "If you cannot see it, print the 'used' field of each result."),
        step("Run the fair harness", "python solution_fair.py",
             "n = 8 annealing; n = 12 qaoa (0.9667, success 0.5, TTS99 1329 vs greedy 0.9333, 0.4, 1803); n = 16 greedy (success 0.9 vs QAOA 0.6).",
             "QAOA local_s grows fast with n: that is the 2^n simulator, not hardware."),
        step("Try it", "python try_it.py", "QAOA wins 1 of 5 other 12-node graphs; with 4096 samples all four solvers incl. exact succeed and greedy wins.",
             "Compare with the tryIt predictions."),
        build_step("my_fair", "bench_lab",
                   "Your file / solution: Ran 6 tests ... OK. Shipped bench_lab: FAILED (failures=4) - unequal budgets [(25, 1)], no BudgetViolation, runs 1 instead of 4/10.",
                   "Over-budget runs must raise (BudgetViolation is a RuntimeError)."),
        step("Run all tests (and the Qiskit path in CI)", "python -m unittest -v; SDK: python bench_qiskit.py",
             "Ran 15 tests ... OK (skipped=1). CI: Qiskit's sampled cut distribution within TVD 0.05 of numpy.",
             "Qiskit import errors: install labs/L400/requirements-sdk.txt.",
             SDK_MAC + " && python labs/L400/18-benchmark-vs-classical/bench_qiskit.py",
             SDK_WIN + "; python labs\\L400\\18-benchmark-vs-classical\\bench_qiskit.py"),
    ],
    "codeWalkthrough": [
        {"title": "solvers.py: the sample budget", "detail": "Every budgeted solver returns {cut, used, first_best}; greedy pays n samples per sweep, annealing one per proposed flip, QAOA one per shot."},
        {"title": "solvers.qaoa", "detail": "Charged like hardware: half the shots estimate <C> on a 5x5 angle grid, the other half sample answers; the answer is the best sampled cut."},
        {"title": "exact()", "detail": "Brute force over 2**n bitstrings - not budgeted, it is the reference that turns cuts into ratios."},
        {"title": "summarise() and tts99()", "detail": "Medians and success over all runs; TTS99 converts a success rate into samples for 99 % confidence (None if never found)."},
        {"title": "decide()", "detail": "The rule written before the results: median ratio, then success, then samples to the best cut; a tie goes to the classical baseline."},
        {"title": "compare() - the fault", "detail": "BOOST gives QAOA 4x and the baselines 1/4 budget, baselines run one seed, the best result is reported, 'used' is never checked."},
    ],
    "designBrief": {
        "context": "Product wants to know whether the optimisation service should offer QAOA for MaxCut on 3-regular graphs up to the sizes our simulator handles (n <= 16).",
        "constraints": ["every solver gets the same sample budget (200) and the same 10 seeds", "no run may spend more than its budget",
                        "results are medians and success rates, never a best run", "the winner rule is fixed before results are seen"],
        "question": "Which solver should the service use for these sizes, and how do we keep future comparisons honest?"},
    "options": [
        {"name": "Exact enumeration", "description": "Brute force 2^n; proves optimality.", "evidence": "n = 12 in 4096 evaluations; n = 16 in 65,536 (0.094 s locally).",
         "verdict": "Use up to n = 20 (ADR 0001)."},
        {"name": "Classical heuristics (greedy, annealing)", "description": "Cheap local search with restarts / cooling.",
         "evidence": "Fair harness, budget 200: n = 8 both 10/10; n = 12 success 0.4 / 0.3; n = 16 success 0.9 / 0.8 (greedy wins).", "verdict": "Default above exact range; tie-break winner."},
        {"name": "QAOA p = 1 (noiseless simulator)", "description": "Grid-tuned angles, best sampled cut.",
         "evidence": "n = 12 wins on graph 0 (0.9667, success 0.5) but 1 of 5 on other graphs; n = 16 success 0.6; 1.69 s simulator time per run at n = 16.",
         "verdict": "Research option only."},
    ],
    "decisionRecord": "labs/L400/18-benchmark-vs-classical/docs/adr/0001-fair-benchmark.md",
    "fitnessFunction": {"what": "The comparison method: one budget, >= 10 identical seeds, used <= budget, classical baseline and exact optimum present, reproducible report.",
                        "test": "labs/L400/18-benchmark-vs-classical/test_fitness.py",
                        "threshold": "budget equality across solvers; runs == 10 per solver; recomputed report identical (excluding local_s)"},
    "scalingLimits": ["Exact enumeration stops near n = 30 (2^n time and 16·2^n bytes of statevector for QAOA): signal = local_s doubling per added node.",
                      "Ten seeds cannot separate success 0.3 from 0.5: add seeds (cost linear) before claiming a ranking.",
                      "A sample budget ignores wall time and noise; at hardware scale queueing (lesson 17) and noise (lesson 12) dominate."],
    "failureLab": {"fault": "The shipped compare(): QAOA gets 4x budget and its best of 10 seeds; greedy and annealing run once at a quarter budget; nobody checks 'used'.",
                   "symptom": "At n = 12 the report says winner 'qaoa' (ratio 1.0 vs 0.8 / 0.8667) while every row claims budget 200.",
                   "fix": "A fair harness: same budget and seeds for all, medians over all runs, BudgetViolation for over-spending (solution_fair.py).",
                   "proof": "BUILD_TASK_MODULE=bench_lab python -m unittest test_build_task test_fitness -> FAILED (failures=4); solution / BUILD_TARGET=mine -> Ran 6 tests OK."},
    "tradeOffs": [
        {"option": "Equal sample budget", "gains": "Hardware-neutral, easy to audit", "costs": "Ignores wall time and queueing", "chooseWhen": "Comparing algorithms"},
        {"option": "Equal wall-clock budget", "gains": "What users feel", "costs": "Depends on machine, simulator and queue; hard to reproduce", "chooseWhen": "Comparing deployed services"},
        {"option": "Best-of-N reporting", "gains": "Shows what is possible", "costs": "Hides reliability; easy to cherry-pick", "chooseWhen": "Only alongside medians and the same N for every solver"},
    ],
    "buildTask": {"task": "Write compare(n, solvers, budget, seeds, edges=None) -> (rows, winner) that gives every solver the same budget and seeds, summarises all runs, and raises a RuntimeError subclass for any run with used > budget.",
                  "hints": ["Call each solver exactly once per seed with the same budget.", "Use lab.summarise(...) over ALL results, then lab.decide(rows).",
                            "Check r['used'] <= budget before summarising."],
                  "solution": "labs/L400/18-benchmark-vs-classical/solution_fair.py",
                  "check": "BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v (6 tests; numpy, runs locally)"},
    "expectedResults": ["Biased method claims a QAOA win at n = 12", "Fair method: annealing (n = 8), qaoa (n = 12, one instance), greedy (n = 16)",
                        "QAOA wins only 1 of 5 other 12-node graphs"],
    "testCases": [{"action": "spy solvers through compare(8, ..., budget=100, seeds=(1, 2, 3))", "expected": "every solver called with (100, 1), (100, 2), (100, 3)"},
                  {"action": "a solver that spends 2x the budget", "expected": "RuntimeError (BudgetViolation)"},
                  {"action": "bench_qiskit.compare_distributions() (CI)", "expected": "TVD < 0.05 between Qiskit and numpy cut distributions"}],
    "tryIt": [
        {"task": "Re-run the fair comparison on five other 12-node graphs (try_it.other_instances).", "predict": "Does QAOA keep winning?",
         "expected": "No: {1: annealing, 2: greedy, 3: qaoa, 4: annealing, 5: annealing} - 1 of 5.", "validatedBy": "local: try_it.py (observed)"},
        {"task": "Give every solver - including exact enumeration - 2^12 = 4096 samples (try_it.exact_in_budget).", "predict": "Who wins now?",
         "expected": "All four succeed (1.0); greedy wins on samples to the best cut; exact also proves optimality.", "validatedBy": "local: try_it.py (observed)"},
    ],
    "troubleshooting": [{"symptom": "tts99_samples is null", "action": "Success rate 0: the solver never found the optimum in any run - no finite time-to-solution."},
                        {"symptom": "Results change between runs", "action": "A solver uses an unseeded RNG; every random choice must come from default_rng(seed)."}],
    "equivalents": ["Qiskit: sample the QAOA circuit with StatevectorSampler / SamplerV2 (bench_qiskit.py); scipy.optimize.dual_annealing is a continuous-domain annealer.",
                    "Abbas et al. (2024) propose benchmarking metrics for quantum optimisation (time-to-solution, approximation ratio, comparisons with tuned classical solvers).",
                    "Classical MaxCut at scale: Goemans-Williamson SDP rounding or industrial MIP solvers."],
    "inRealSystems": ["Vendor 'advantage' claims are judged against the strongest tuned classical baseline on the same instances.",
                      "Benchmark harnesses pin seeds, budgets and instance generators in version control and fail CI on method drift."],
    "useWhen": "Use a fair harness before any 'quantum vs classical' statement; avoid single-instance or best-seed claims entirely.",
    "simulatorVsReal": "Noiseless numpy QAOA (labs/_shared/qopt); shots are free and exact. Hardware adds gate/readout noise and queue time, which lower QAOA's success further.",
    "checkYourself": [{"q": "Why is the n = 12 QAOA win not a reason to ship QAOA?", "a": "One instance at a sample budget on a noiseless simulator; it won 1 of 5 other graphs and exact enumeration needs only 4096 evaluations."},
                      {"q": "What does TTS99 = 1329 mean?", "a": "At success 0.5 per 200-sample run, about 1329 samples give 99 % confidence of seeing the optimum."},
                      {"q": "Why do ties go to the classical solver?", "a": "It is cheaper to run and operate; a quantum solver must win outright to justify its cost."}],
    "checkpoint": "PASS if the biased method's 'qaoa' claim at n = 12 is explained, your harness passes test_build_task and test_fitness, and bench_lab fails them.",
    "learningTools": [
        tool(MARIMO, "`marimo edit`: sliders for n (8/12/16), budget (50-2000) and number of seeds; one cell runs solution_fair.compare(n, budget=..., seeds=range(k)).",
             "Budget 200 / 10 seeds reproduces winners annealing, qaoa, greedy; raising the budget to 2000 makes all three succeed at n = 8-16."),
        tool(JUPYTER, "Plot success rate vs budget (100, 200, 400) per solver for n = 12 and n = 16 from repeated compare() calls.",
             "At budget 200: n = 12 greedy 0.4, annealing 0.3, QAOA 0.5; n = 16 0.9 / 0.8 / 0.6 (the lab README output)."),
    ],
    "seeAlso": ["simulation L300 #12 Variance reduction: same precision, fewer runs: comparing methods at equal cost and with common random numbers.",
                "simulation L200 #10 Warm-up, replications and confidence: report a spread over seeds, not one run.",
                "L400 #22 Capstone: an end-to-end quantum optimisation service: the service's winner comes from this harness."],
    "sources": src("farhi", "kirkpatrick", "abbas", "dual_annealing"),
    "next": "L400 #19 Resource estimation: logical vs physical qubits and feasibility: what it would take for QAOA (or Shor) to run at sizes where classical solvers struggle.",
    "how": RAN + "`python bench_lab.py`, `python solution_fair.py`, `python try_it.py` (outputs in README); `python -m unittest` -> 15 tests OK, 1 Qiskit test skipped; fail-before proof with BUILD_TASK_MODULE=bench_lab observed (4 failures).",
    "pendingCi": ["bench_qiskit.py (Qiskit StatevectorSampler sampling of the QAOA circuit)", "test_try_it.py QiskitPath (1 test)"],
    "projectFiles": [("bench_lab.py", "main lab: metrics, decide(), the biased compare()"), ("solvers.py", "exact, greedy, annealing, QAOA with sample accounting"),
                     ("solution_fair.py", "buildTask reference: fair harness with BudgetViolation"), ("buildtarget.py", "BUILD_TARGET=mine / BUILD_TASK_MODULE switch"),
                     ("test_build_task.py", "buildTask + failureLab proof"), ("test_fitness.py", "fitness function for the comparison method"),
                     ("test_bench.py", "solver and metric tests, observed tables"), ("bench_qiskit.py", "SDK path (CI)"),
                     ("docs/adr/0001-fair-benchmark.md", "decision record"), ("README.md", "run commands and observed output")],
    "summary": "Hold instance, seeds and budget fixed and report medians and success; exact enumeration is the reference. The biased method fabricated a QAOA win; the fair one shows a single-instance QAOA win at n = 12 that does not generalise, and classical solvers win elsewhere. Code decides; ties go classical.",
}


L19 = {
    "dir": "19-resource-estimation", "file": "estimate_lab.py", "id": "resource-estimation", "number": 19,
    "title": "Resource estimation: logical vs physical qubits and feasibility",
    "phase": "Design", "category": "resource estimation",
    "description": "Estimate qubits, depth, CX and T counts for growing QAOA and Shor workloads, convert logical to physical qubits with a surface-code model and an error budget, and decide feasibility thresholds.",
    "outcome": "You can derive logical counts (validated against counted circuits), choose a code distance from an error budget, refuse estimates above threshold, classify workloads (simulate / NISQ / fault-tolerant / infeasible) and cross-check with the QDK estimator.",
    "sdk": "Microsoft QDK qdk 1.33.1 qdk.qre estimator (estimate_qdk.py, CI job l400-qdk) and Qiskit 2.6.1 transpile counts (count_qiskit.py)",
    "estimatedTime": "60-90 minutes",
    "overview": ["Algorithms count logical qubits; machines are built from physical ones. The surface-code distance, chosen from an error budget, turns one into the other - and decides what is feasible."],
    "prerequisites": ["Lesson 11 (transpiling: CX counts and depth)", "Lesson 12 (gate error rates)", "Lesson 14 (QAOA circuit structure)"],
    "glossary": [
        {"term": "logical qubit", "meaning": "An error-corrected qubit encoded in many physical qubits."},
        {"term": "code distance d", "meaning": "Surface-code size; errors are suppressed as (p / p_th)^((d+1)/2); about 2d^2 physical qubits per logical qubit."},
        {"term": "T-count", "meaning": "Number of non-Clifford T gates; dominates fault-tolerant cost (magic-state factories)."},
        {"term": "logical cycle", "meaning": "One logical time step, lasting d surface-code cycles (1 us each here)."},
        {"term": "error budget", "meaning": "Allowed total failure probability for the whole run (1 % here)."},
        {"term": "threshold p_th", "meaning": "Physical error rate (1 %) above which a larger code makes things worse."},
    ],
    "concepts": ["Logical counts first, then a code model, then a policy threshold.", "Distance comes from the budget, not from habit.",
                 "Estimates include assumptions; say which overheads are left out.", "Validate formulas against counted circuits."],
    "steps": [
        step("Run the shipped estimator", "python estimate_lab.py",
             "RSA-2048: 6190 logical qubits, 1.84e10 T gates, distance 3, 111,420 physical qubits, 6430 s - class fault-tolerant-feasible, p_fail 1.0.",
             "ModuleNotFoundError: run from the lab folder (counting.py and labs/_shared are imported)."),
        step("See the fault", "Compare 'class' with 'p_fail' on every line.",
             "Every workload has p_fail 1.0 (certain failure) yet four are called feasible: d = 3 for everything.",
             "If p_fail < budget you changed choose_distance already."),
        step("Run the decided estimator", "python solution_distance.py",
             "QAOA n=100 p=4: d 11, 24,200 qubits, 13.8 ms (FT-feasible); RSA-2048: d 27, 9,025,020 qubits, 57,870 s (infeasible); every p_fail <= 0.01.",
             "A distance that never satisfies the budget: check logical_cycles, not depth, is used."),
        step("Check the counts", "python -m unittest test_estimate -v",
             "Formulas = counted circuits for n = 6-12, p = 1-3 (CX, rotations; depth is an upper bound, tight with 4 colours); Toffoli = 7 T, unitary exact.",
             "Depth mismatch: greedy edge colouring used 5 colours for that graph - the formula assumes the colour count you pass."),
        step("Try it", "python try_it.py", "p = 1e-4: RSA-2048 d 13, 2,092,220 qubits, 27,860 s; QAOA near threshold: d 37 at p = 0.005, no d <= 101 at 0.009, refused at 0.011.",
             "Compare with the tryIt predictions."),
        build_step("my_distance", "estimate_lab",
                   "Your file / solution: Ran 7 tests ... OK. Shipped estimate_lab: FAILED (failures=5) - d 3 != 27, budget not met, no refusal, decision table differs.",
                   "Above the threshold raise ValueError instead of looping or returning a number."),
        step("QDK and Qiskit cross-checks (CI)", "Separate venv: python estimate_qdk.py; SDK venv: python count_qiskit.py",
             "CI: QDK physical qubits within 0.3-30x of our data-only bound (it adds factories); Qiskit CX and depth equal the counted circuit.",
             "qdk.qre import errors: install labs/L400/requirements-qdk.txt; set QDK_PYTHON_TELEMETRY=none to opt out of telemetry.",
             "python3.12 -m venv .venv-qdk && source .venv-qdk/bin/activate && python -m pip install -r labs/L400/requirements-qdk.txt && QDK_PYTHON_TELEMETRY=none python labs/L400/19-resource-estimation/estimate_qdk.py",
             "py -3.12 -m venv .venv-qdk; .venv-qdk\\Scripts\\Activate.ps1; python -m pip install -r labs\\L400\\requirements-qdk.txt; $env:QDK_PYTHON_TELEMETRY = \"none\"; python labs\\L400\\19-resource-estimation\\estimate_qdk.py"),
    ],
    "codeWalkthrough": [
        {"title": "counting.qaoa_ops / count", "detail": "Builds the QAOA circuit as explicit ops (RZZ = CX RZ CX, edges grouped by colour) and counts CX, rotations and ASAP depth - the ground truth for small n."},
        {"title": "counting.toffoli_ok", "detail": "Checks the textbook 7-T Toffoli decomposition against the exact Toffoli unitary: the 7 T per Toffoli used for Shor is verified, not assumed."},
        {"title": "qaoa_logical", "detail": "Formulas that scale to any n: CX = 2|E|p, rotations = p(|E| + n), depth = 1 + p(3c + 1), T = rotations x 3 log2(1/eps) (Ross-Selinger), logical cycles include T-limited rotation layers."},
        {"title": "rsa_logical", "detail": "Gidney & Ekera's abstract formulas: 3n + 0.002 n lg n logical qubits, 0.3n^3 + 0.0005 n^3 lg n Toffolis, 500n^2 + n^2 lg n measurement depth."},
        {"title": "logical_error / physical", "detail": "p_L(d) = 0.03 (p/0.01)^((d+1)/2) (Fowler Eq. 11, QDK SurfaceCode defaults); physical = logical x 2d^2; runtime = cycles x d x 1 us; p_fail = qubits x cycles x p_L."},
        {"title": "choose_distance (the fault)", "detail": "Shipped: always 3. The build task chooses the smallest odd d that meets the 1 % budget and refuses at or above the threshold."},
        {"title": "classify", "detail": "Policy: simulate (<= 30 qubits), NISQ candidate ((1-1e-3)^CX >= 0.5), fault-tolerant-feasible (<= 1e6 physical, <= 1 day), else infeasible."},
    ],
    "designBrief": {
        "context": "Before running any request, the service must say whether it can be simulated, tried on a noisy device, needs a fault-tolerant machine, or is out of reach - and security asks when RSA-2048 becomes breakable.",
        "constraints": ["total failure probability <= 1 %", "p = 1e-3 physical error, 1 us code cycles (stated assumptions)",
                        "fault-tolerant-feasible means <= 1,000,000 physical qubits and <= 1 day", "formulas must match counted circuits where both exist"],
        "question": "How do we estimate resources and where do we draw the feasibility lines?"},
    "options": [
        {"name": "Count a built circuit", "description": "Exact gate counts and depth from the circuit itself.", "evidence": "Equals the formulas for n = 6-12, p = 1-3 (CX, rotations); depth 40 at n = 12, p = 3.",
         "verdict": "Validation only (cannot build RSA-2048)."},
        {"name": "Analytic model with an error-budget distance", "description": "Formulas + surface-code model, distance from the budget.", "evidence": "RSA-2048 d 27, 9,025,020 physical, 16.1 h; QAOA n=100 p=4 d 11, 24,200; all p_fail <= 0.01.",
         "verdict": "Chosen as the gate (ADR 0001)."},
        {"name": "Full estimator (QDK qdk.qre)", "description": "Models factories, layout and Pareto trade-offs.", "evidence": "Pending CI; expected at or above our data-only bound (3240 physical for QAOA n=20 p=1).",
         "verdict": "Cross-check in CI."},
    ],
    "decisionRecord": "labs/L400/19-resource-estimation/docs/adr/0001-feasibility-gate.md",
    "fitnessFunction": {"what": "No estimate exceeds the error budget; 'feasible' respects the thresholds; the pinned decision table for the six reference workloads does not change.",
                        "test": "labs/L400/19-resource-estimation/test_fitness.py",
                        "threshold": "p_fail <= 0.01 for all rows; FT-feasible <= 1,000,000 physical and <= 86,400 s; classes = simulate, nisq, FT, FT, infeasible, infeasible"},
    "scalingLimits": ["Near threshold the distance explodes (d 37 at p = 0.005; nothing <= 101 at 0.009): signal = distance jumps for a small change in p.",
                      "Data-only model: factories, routing and decoding are missing; if QDK's numbers exceed ours by > 30x a model assumption is wrong.",
                      "Thresholds are policy: a new device budget or runtime limit changes the decision table and needs a new ADR."],
    "failureLab": {"fault": "choose_distance() returns 3 for every workload ('a logical qubit is 17 physical qubits').",
                   "symptom": "RSA-2048 reported fault-tolerant-feasible with 111,420 physical qubits and 6430 s while its own p_fail is 1.0; every row has p_fail 1.0.",
                   "fix": "Smallest odd d with qubits x cycles x p_L(d) <= budget; ValueError at or above the 1 % threshold (solution_distance.py).",
                   "proof": "BUILD_TASK_MODULE=estimate_lab python -m unittest test_build_task test_fitness -> FAILED (failures=5); solution / BUILD_TARGET=mine -> Ran 7 tests OK."},
    "tradeOffs": [
        {"option": "Fixed overhead factor", "gains": "One multiplication", "costs": "Ignores runtime and budget; can claim feasibility with certain failure", "chooseWhen": "Never for decisions"},
        {"option": "Budget-derived distance (data blocks)", "gains": "Transparent, fast, testable lower bound", "costs": "Omits factories and routing", "chooseWhen": "Gating requests and teaching"},
        {"option": "Full estimator (QDK)", "gains": "Factories, layouts, Pareto frontier", "costs": "Separate environment, API in flux", "chooseWhen": "Hardware planning and cross-checks"},
    ],
    "buildTask": {"task": "Write choose_distance(p, logical_qubits, cycles, budget=0.01) returning the smallest odd d >= 3 with logical_qubits x cycles x p_L(d) <= budget, and raising ValueError when p >= 0.01.",
                  "hints": ["Loop d = 3, 5, 7, ... up to a cap (101).", "Use lab.logical_error(d, p).", "Above threshold p_L grows with d - refuse instead of looping."],
                  "solution": "labs/L400/19-resource-estimation/solution_distance.py",
                  "check": "BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v (7 tests; stdlib, runs locally)"},
    "expectedResults": ["Counted CX/rotations equal the formulas; Toffoli = 7 T (exact unitary)", "RSA-2048: d 27, 9,025,020 physical qubits, 16.1 h (data only)",
                        "Decision table: simulate, nisq-candidate, FT-feasible x2, infeasible x2"],
    "testCases": [{"action": "rsa_logical(2048)", "expected": "6190 logical qubits, 2,624,225,018 Toffolis, depth 2,143,289,344"},
                  {"action": "choose_distance(0.011, 100, 1000)", "expected": "ValueError (above threshold)"},
                  {"action": "count_qiskit.check() (CI)", "expected": "Qiskit CX == analytic CX; Qiskit depth == counted depth"}],
    "tryIt": [
        {"task": "Physical error 1e-4 instead of 1e-3 for RSA-2048 (try_it.better_hardware).", "predict": "How far do distance and qubits drop?",
         "expected": "d 27 -> 13; 9,025,020 -> 2,092,220 physical qubits; 57,870 s -> 27,860 s. Still above 1e6: infeasible under our policy.", "validatedBy": "local: try_it.py (observed)"},
        {"task": "QAOA n=100 p=4 at p = 0.001, 0.005, 0.009, 0.011 (try_it.near_threshold).", "predict": "Smooth growth or a cliff?",
         "expected": "(11, 24,200), (37, 273,800), then 'no distance <= 101 meets budget 0.01', then refused above threshold.", "validatedBy": "local: try_it.py (observed)"},
    ],
    "troubleshooting": [{"symptom": "Runtime looks absurdly short", "action": "You used circuit depth as logical cycles; T-limited rotation layers add p(c+1) x T-per-rotation cycles."},
                        {"symptom": "QDK numbers far above ours", "action": "Expected up to ~10x (factories, routing); beyond 30x check the error rate, budget and gate times passed to GateBased."}],
    "equivalents": ["Microsoft QDK: qdk.qre estimate(app, GateBased(...), SurfaceCode.q() * RoundBasedFactory.q(), max_error=0.01) (estimate_qdk.py).",
                    "Qiskit: count_ops() / depth() on a transpiled circuit; transpile to a Clifford+T basis for T-counts (clifford_t_pass_manager).",
                    "Beverland et al. (2022) describe the layered estimation framework the QDK estimator implements."],
    "inRealSystems": ["Hardware roadmaps and PQC timelines are argued from resource estimates; published RSA-2048 numbers moved from 20 million to under one million qubits between 2019 and 2025.",
                      "Teams gate expensive hardware runs on an estimate checked into the repository."],
    "useWhen": "Use an estimate before every hardware or roadmap decision; avoid quoting logical qubits as machine sizes.",
    "simulatorVsReal": "No simulation: an analytic model with stated assumptions (p = 1e-3, 1 us cycles, data blocks only). Real machines add factories, routing, decoding latency and correlated errors.",
    "checkYourself": [{"q": "Why is d = 27 needed for RSA-2048 but d = 9 for QAOA n = 20?", "a": "p_fail scales with qubits x cycles; RSA-2048 has 2.1e9 cycles and 6190 qubits, so p_L must be ~1e-15."},
                      {"q": "What does 'data blocks only' leave out?", "a": "Magic-state factories, routing space and decoding - so 9,025,020 is a lower bound."},
                      {"q": "Why refuse above threshold?", "a": "For p >= p_th, p_L grows with d: no code distance can meet any budget."}],
    "checkpoint": "PASS if the shipped estimator's p_fail = 1.0 'feasible' rows are explained, your choose_distance passes test_build_task and test_fitness, and estimate_lab fails them.",
    "learningTools": [
        tool(QDK, "In the l400-qdk venv run estimate_qdk.py; then change GateBased(error_rate=1e-4) and compare the Pareto table with try_it.better_hardware().",
             "QDK's minimum physical qubits for QAOA n=20 p=1 should be at or above our data-only 3240 (d 9); lowering the error rate should shrink both."),
        tool(JUPYTER, "Plot physical qubits (log scale) against physical error p in 1e-4..9e-3 for QAOA n=100 p=4 and RSA-2048 using solution_distance.choose_distance.",
             "Curves pass through (1e-3: 24,200 and 9,025,020) and (5e-3: 273,800 for QAOA) and end where no distance <= 101 exists."),
    ],
    "seeAlso": ["L400 #21 Quantum and post-quantum: crypto inventory and migration plan: reuses this estimator for Shor's RSA-2048 in context.",
                "L400 #20 Error-aware compilation: layout, routing and a depth budget: the near-term counterpart - ESP instead of code distance.",
                "L400 #22 Capstone: an end-to-end quantum optimisation service: this estimate is the service's feasibility gate.",
                "simulation L100 #6 Is the model right? Verification vs validation: the formulas are verified against counted circuits before anyone trusts them."],
    "sources": src("fowler", "qre_surface", "gidney2019", "gidney2025", "ross", "amy", "beverland", "qre_install", "qre_intro", "qdk_pypi"),
    "next": "L400 #20 Error-aware compilation: layout, routing and a depth budget: the near-term side - squeezing fidelity out of the noisy device you do have.",
    "how": RAN + "`python estimate_lab.py`, `python solution_distance.py`, `python try_it.py` (outputs in README); `python -m unittest` -> 17 tests OK, 2 SDK tests skipped (Qiskit, QDK); fail-before proof with BUILD_TASK_MODULE=estimate_lab observed (5 failures).",
    "pendingCi": ["estimate_qdk.py (qdk 1.33.1 qdk.qre: OpenQASMApplication, GateBased, SurfaceCode x RoundBasedFactory)", "count_qiskit.py (Qiskit transpile counts)",
                  "test_estimate.py QiskitAgrees + QdkEstimator (2 tests)"],
    "projectFiles": [("estimate_lab.py", "main lab: logical counts, surface-code model, fixed-distance fault, classification"),
                     ("counting.py", "helper: explicit QAOA ops, counts, edge colouring, 7-T Toffoli check"),
                     ("solution_distance.py", "buildTask reference: budget-derived distance with threshold refusal"),
                     ("buildtarget.py", "BUILD_TARGET=mine / BUILD_TASK_MODULE switch"), ("test_build_task.py", "buildTask + failureLab proof"),
                     ("test_fitness.py", "fitness function: budget, thresholds, pinned decision table"), ("test_estimate.py", "formulas vs counts; SDK/QDK in CI"),
                     ("estimate_qdk.py", "QDK resource estimator path (CI job l400-qdk)"), ("count_qiskit.py", "Qiskit counting path (CI)"),
                     ("docs/adr/0001-feasibility-gate.md", "decision record"), ("README.md", "run commands and observed output")],
    "summary": "Count logical resources with formulas validated against built circuits, then pick the surface-code distance from an error budget (p_L = 0.03 (p/0.01)^((d+1)/2), ~2d^2 physical per logical) and classify workloads by policy thresholds. A fixed d = 3 made RSA-2048 look feasible with certain failure; the budget-derived model gives 9.0 million physical qubits, between published whole-machine estimates.",
}


L20 = {
    "dir": "20-error-aware-compilation", "file": "compile_lab.py", "id": "error-aware-compilation", "number": 20,
    "title": "Error-aware compilation: layout, routing and a depth budget",
    "phase": "Design", "category": "compilation",
    "description": "Compile lesson 14's QAOA circuit onto a fake 8-qubit ladder with per-edge error rates: compare trivial, connectivity-based and noise-aware layout/routing by expected fidelity and depth, and keep the result within a depth budget.",
    "outcome": "You can score compilations by ESP, CX count and depth, prove routed circuits equivalent, choose a noise-aware layout that survives calibration drift, and enforce a depth budget with a fitness test.",
    "sdk": "qiskit 2.6.1 transpile(optimization_level 0-3, seed_transpiler) against a Target carrying the same error map (compile_qiskit.py)",
    "estimatedTime": "60-90 minutes",
    "overview": ["Devices are uneven and drift daily; where you place qubits and how you route SWAPs can matter more than any other compiler choice."],
    "prerequisites": ["Lesson 11 (transpiling to a device layout)", "Lesson 12 (noise models)", "Lesson 14 (the 5-node QAOA circuit)"],
    "glossary": [
        {"term": "layout", "meaning": "Which physical qubit hosts each logical qubit."},
        {"term": "routing", "meaning": "Inserting SWAPs (3 CX each) so every two-qubit gate acts on a coupled pair."},
        {"term": "ESP", "meaning": "Estimated success probability: product of (1 - error) over all gates and measurements (Nishio et al.)."},
        {"term": "reliable path", "meaning": "Shortest path with edge weight -log(1 - CX error) instead of hop count."},
        {"term": "calibration drift", "meaning": "Error rates changing between calibrations; here edge (1,2) degrades to 15 %."},
        {"term": "depth budget", "meaning": "Maximum allowed circuit depth (22 = logical 17 + room for one SWAP)."},
    ],
    "concepts": ["Score compilations, don't just count gates.", "Noise-aware layout routes around bad couplers.",
                 "Prove equivalence before trusting any score.", "A depth budget makes trade-offs explicit and testable."],
    "steps": [
        step("Run the shipped compiler", "python compile_lab.py",
             "Drifted device: trivial ESP 0.2084 (27 CX, depth 32); degree-based + cancel 0.3059 (19 CX, depth 24); both outside the depth budget 22.",
             "ModuleNotFoundError: run from the lab folder."),
        step("Read the device", "device.py: ladder 0-1-2-3 / 4-5-6-7 with rungs; seeded CX 0.5-2 %, readout 1-4 %; DRIFT sets (1,2) to 15 %.",
             "The logical circuit has a triangle (0,1,2), so every ladder layout needs at least one SWAP.", "Check make_device(seed=5)."),
        step("Run the noise-aware layout", "python solution_layout.py",
             "Calibrated: layout [2, 3, 6, 1, 5], ESP 0.7925, 13 CX, depth 18; drifted: [5, 1, 6, 2, 3], ESP 0.7835, 19 CX, depth 21 - within budget.",
             "Slow: 6720 layouts are routed; the path table is cached per device."),
        step("Check equivalence and fidelity", "python -m unittest test_compile -v",
             "All options reproduce the logical distribution (TVD < 1e-9); simulated fidelity 0.8959 (trivial) vs 0.9878 (noise-aware) ranks like ESP.",
             "Equivalence failure = a SWAP bookkeeping bug in route()."),
        step("Try it", "python try_it.py", "drift on (5,6): new layout [1, 2, 5, 0, 4], ESP 0.7503, avoids the edge; budget 17: best is depth 21, reported as outside the budget.",
             "Compare with the tryIt predictions."),
        build_step("my_layout", "compile_lab",
                   "Your file / solution: Ran 5 tests ... OK. Shipped compile_lab: FAILED (failures=3) - ESP 0.2084 < 0.75, depth 32 > 22 on both devices.",
                   "Score = (depth within budget, ESP, -depth) and route with weighted=True."),
        step("Run all tests (and the Qiskit levels in CI)", "python -m unittest -v; SDK: python compile_qiskit.py",
             "Ran 13 tests ... OK (skipped=1). CI: level 3 ESP >= level 0 ESP on the same Target error map.",
             "Qiskit import errors: install labs/L400/requirements-sdk.txt.",
             SDK_MAC + " && python labs/L400/20-error-aware-compilation/compile_qiskit.py",
             SDK_WIN + "; python labs\\L400\\20-error-aware-compilation\\compile_qiskit.py"),
    ],
    "codeWalkthrough": [
        {"title": "device.make_device / DRIFT", "detail": "Seeded error map per edge and qubit; DRIFT models today's calibration with one bad coupler."},
        {"title": "device.all_pairs (Floyd-Warshall)", "detail": "Hop counts, or -log(1 - error) weights so the 'shortest' path is the most reliable one; cached per error map."},
        {"title": "route()", "detail": "For each CX on non-adjacent qubits, SWAP the control along the path (3 CX each) and update the logical->physical map; returns the final layout for measurement."},
        {"title": "cancel()", "detail": "Optimisation pass: removes back-to-back identical CX on the same qubits (CX.CX = I); a SWAP followed by the RZZ's first CX saves 2 CX."},
        {"title": "metrics()", "detail": "ESP over gates and readout of the final qubits, CX count and ASAP depth - the three numbers every option is judged by."},
        {"title": "choose_layout (the fault) / dense_layout", "detail": "Trivial i -> i ignores errors; degree-based uses connectivity only. The build task searches placements by ESP within the depth budget."},
        {"title": "noisy_check.equivalent / noisy_fidelity", "detail": "Independent density-matrix simulation: noiseless output must equal the logical circuit; with depolarizing noise at the device's rates it confirms ESP's ranking."},
    ],
    "designBrief": {
        "context": "The service compiles a 5-qubit QAOA circuit (12 CX, depth 17) for an 8-qubit ladder whose calibration changes daily; today one coupler drifted to 15 % error.",
        "constraints": ["depth <= 22 after routing", "ESP >= 0.75 on both the calibrated and the drifted device", "<= 20 CX",
                        "noiseless output identical to the logical circuit"],
        "question": "Which layout/routing/optimisation strategy should the compiler use, and how is its output checked?"},
    "options": [
        {"name": "A trivial layout + hop routing", "description": "Level-0 style.", "evidence": "Calibrated ESP 0.5763, 27 CX, depth 32; drifted 0.2084; simulated fidelity 0.8959.",
         "verdict": "Rejected."},
        {"name": "B degree-based layout + hop routing + CX cancellation", "description": "Level 1-2 style, error-blind.", "evidence": "Calibrated 0.7315 / 19 / 24; drifted 0.3059 / 19 / 24.",
         "verdict": "Rejected (depth and drift)."},
        {"name": "C noise-aware layout + reliable routing + cancellation", "description": "Level-3 / VF2PostLayout idea, brute force here.",
         "evidence": "Calibrated 0.7925 / 13 / 18; drifted 0.7835 / 19 / 21; simulated fidelity 0.9878.", "verdict": "Chosen (ADR 0001)."},
    ],
    "decisionRecord": "labs/L400/20-error-aware-compilation/docs/adr/0001-noise-aware-compile.md",
    "fitnessFunction": {"what": "The compiled circuit stays within the depth budget with enough expected fidelity and the same noiseless output, on both device states.",
                        "test": "labs/L400/20-error-aware-compilation/test_fitness.py",
                        "threshold": "depth <= 22, ESP >= 0.75, CX <= 20, noiseless TVD < 1e-9 (calibrated and drifted)"},
    "scalingLimits": ["Brute-force layout search grows as nPk (6720 here; 8! = 40,320 for 8 of 8): switch to VF2 / SABRE or sampled candidates (the capstone samples 200).",
                      "Stale calibration: ESP computed on yesterday's map; signal = ESP drops on today's map with no code change - recompile per calibration.",
                      "Crosstalk and leakage are not in a per-gate product; ESP may mis-rank options - validate against measured results."],
    "failureLab": {"fault": "choose_layout() is trivial (logical i -> physical i) and routing counts hops, on a device whose (1,2) coupler drifted to 15 %.",
                   "symptom": "ESP 0.2084 with 27 CX and depth 32 (> budget 22); simulated output fidelity 0.8959.",
                   "fix": "Search placements by ESP within the depth budget, route along the most reliable path, cancel CX pairs (solution_layout.py).",
                   "proof": "BUILD_TASK_MODULE=compile_lab python -m unittest test_build_task test_fitness -> FAILED (failures=3); solution / BUILD_TARGET=mine -> Ran 5 tests OK."},
    "tradeOffs": [
        {"option": "Error-blind fast compile", "gains": "Milliseconds, deterministic", "costs": "Can land on the worst coupler (ESP 0.2084)", "chooseWhen": "Simulators and uniform devices"},
        {"option": "Noise-aware search", "gains": "ESP 0.7835 under drift", "costs": "Compile time grows combinatorially; needs fresh calibration", "chooseWhen": "Any real device run"},
        {"option": "Strict depth budget", "gains": "Predictable coherence use; testable", "costs": "May be infeasible (17 on a ladder)", "chooseWhen": "Always, with a loud failure when it cannot be met"},
    ],
    "buildTask": {"task": "Write choose_layout(dev, budget=22) returning 5 physical qubits that maximise ESP among layouts whose routed (weighted, cancelled) depth fits the budget.",
                  "hints": ["itertools.permutations(range(8), 5) gives all 6720 placements.", "Use lab.compile_circuit(dev, layout, weighted=True, optimise=True).",
                            "Rank by (depth <= budget, esp, -depth)."],
                  "solution": "labs/L400/20-error-aware-compilation/solution_layout.py",
                  "check": "BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v (5 tests; numpy, runs locally)"},
    "expectedResults": ["Noise-aware ESP 0.7835 vs trivial 0.2084 on the drifted device", "Depth 21 <= 22 and 19 CX after cancellation",
                        "ESP ranking matches simulated fidelity (0.8959 vs 0.9878)"],
    "testCases": [{"action": "compile every option and run noisy_check.equivalent", "expected": "True for all (routing preserves the answer)"},
                  {"action": "depolarize() vs qsim density depolarizing_kraus on 3 qubits", "expected": "allclose"},
                  {"action": "compile_qiskit.run() (CI)", "expected": "level 3 ESP >= level 0 ESP on the same error map"}],
    "tryIt": [
        {"task": "Drift a different coupler, (5,6) to 15 % (try_it.other_drift).", "predict": "Does the layout move away from it?",
         "expected": "Yes: layout [1, 2, 5, 0, 4], ESP 0.7503, 13 CX, depth 18, uses_drifted_edge False, simulated fidelity 0.9855.", "validatedBy": "local: try_it.py (observed)"},
        {"task": "Demand depth 17, the logical depth (try_it.tight_budget).", "predict": "Can any layout meet it?",
         "expected": "No: best is ESP 0.7835 at depth 21 and within_budget False - a triangle needs a SWAP on a ladder.", "validatedBy": "local: try_it.py (observed)"},
    ],
    "troubleshooting": [{"symptom": "Equivalence check fails after routing", "action": "The logical->physical map was not swapped for both qubits; route() must update the occupant of the target qubit too."},
                        {"symptom": "solution_layout.py takes minutes", "action": "all_pairs must be cached per error map; 6720 Floyd-Warshall runs are the slow part."}],
    "equivalents": ["Qiskit: transpile(..., target=Target with InstructionProperties(error=...), optimization_level=3, seed_transpiler=7); VF2PostLayout rescoring (compile_qiskit.py).",
                    "Qiskit visualization: plot_circuit_layout / plot_error_map to see the chosen qubits on the device.",
                    "tket and other compilers offer noise-aware placement passes with the same goal."],
    "inRealSystems": ["Production pipelines recompile per calibration cycle and pick layouts with error-aware scoring (VF2PostLayout).",
                      "Circuits that cannot meet their depth budget are rejected or re-designed rather than run."],
    "useWhen": "Use error-aware layout for any run on real hardware; avoid caching compiled circuits across calibrations.",
    "simulatorVsReal": "Pure-Python compiler and a fake device with illustrative seeded error rates; independent numpy density-matrix check with depolarizing noise. Real devices add crosstalk, leakage and direction constraints.",
    "checkYourself": [{"q": "Why can depth 21 beat depth 18?", "a": "The drifted layout avoids the 15 % coupler: ESP 0.7835 with depth 21 vs layouts that use it."},
                      {"q": "Why prove equivalence before scoring?", "a": "A routing bug yields a plausible, wrong circuit whose ESP looks fine."},
                      {"q": "Why is ESP below the simulated fidelity?", "a": "ESP treats every error as fatal; many errors barely change the output distribution - only the ranking matters."}],
    "checkpoint": "PASS if you can explain the three options' ESP/depth, your layout passes test_build_task and test_fitness, and the trivial layout fails them.",
    "learningTools": [
        tool(QVIS, "Build the Target from compile_qiskit.target(make_device(drift=DRIFT)), transpile at level 0 and 3, and call plot_circuit_layout(tqc, backend-like) / plot_error_map for both.",
             "Level 0 places qubits 0-4 and uses the red (1,2) edge; the lab's noise-aware layout [5, 1, 6, 2, 3] avoids it (ESP 0.7835 vs 0.2084 in the README)."),
    ],
    "seeAlso": ["L400 #19 Resource estimation: logical vs physical qubits and feasibility: the fault-tolerant alternative to squeezing noisy devices.",
                "L400 #22 Capstone: an end-to-end quantum optimisation service: samples 200 layouts with this router for 8-qubit requests."],
    "sources": src("nishio", "preset", "transpile", "vf2post", "generic"),
    "next": "L400 #21 Quantum and post-quantum: crypto inventory and migration plan: what fault-tolerant machines would break, and what your code must do now.",
    "how": RAN + "`python compile_lab.py`, `python solution_layout.py`, `python try_it.py` (outputs in README); `python -m unittest` -> 13 tests OK, 1 Qiskit test skipped; fail-before proof with BUILD_TASK_MODULE=compile_lab observed (3 failures).",
    "pendingCi": ["compile_qiskit.py (Qiskit Target with the lab's error map, optimization_level 0-3)", "test_compile.py QiskitLevels (1 test)"],
    "projectFiles": [("compile_lab.py", "main lab: logical circuit, routing, cancellation, ESP/depth, trivial and degree layouts"),
                     ("device.py", "fake ladder device, drift, reliable shortest paths"), ("noisy_check.py", "independent density-matrix equivalence and fidelity"),
                     ("solution_layout.py", "buildTask reference: noise-aware layout search"), ("buildtarget.py", "BUILD_TARGET=mine / BUILD_TASK_MODULE switch"),
                     ("test_build_task.py", "buildTask + failureLab proof"), ("test_fitness.py", "fitness function: depth budget, ESP, CX, equivalence"),
                     ("test_compile.py", "routing correctness, metrics, noise model"), ("compile_qiskit.py", "SDK path: Qiskit Target + levels (CI)"),
                     ("docs/adr/0001-noise-aware-compile.md", "decision record"), ("README.md", "run commands and observed output")],
    "summary": "Score every compilation by ESP (product of gate and readout fidelities), CX count and depth on today's calibration, and prove equivalence first. A trivial layout on a drifted coupler gave ESP 0.2084 at depth 32; a noise-aware layout with reliability-weighted routing gave 0.7835 at depth 21, within the 22-layer budget the fitness test enforces.",
}


L21 = {
    "dir": "21-post-quantum-migration", "file": "pqc_lab.py", "id": "post-quantum-migration", "number": 21,
    "title": "Quantum and post-quantum: crypto inventory and migration plan",
    "phase": "Design", "category": "post-quantum cryptography",
    "description": "Put Shor's resource estimates in context, inventory a toy codebase's RSA/ECDH/ECDSA use with an AST scanner, prioritise by harvest-now-decrypt-later risk, and design crypto agility with a hybrid X25519 + ML-KEM-768 that runs locally.",
    "outcome": "You can explain what quantum computing changes for software, build a tested crypto inventory, compute migration priorities with Mosca's inequality, put key establishment behind an agile interface with ML-KEM-768, and check an agent's migration notes against the facts.",
    "sdk": "none needed: cryptography 50.0.2 provides ML-KEM-768 (FIPS 203) locally",
    "estimatedTime": "60-90 minutes",
    "overview": ["The quantum threat to today's software is a migration problem: find every public-key use, move long-lived key establishment first, and make the next algorithm swap a configuration change."],
    "prerequisites": ["Lesson 19 (resource estimation)", "cryptography L200 #8 Key exchange and hybrid encryption (X25519 + HKDF + AEAD)",
                      "cryptography L200 #7 Digital signatures with Ed25519"],
    "glossary": [
        {"term": "harvest now, decrypt later", "meaning": "Recording encrypted traffic today to decrypt it once a quantum computer exists (NIST IR 8547)."},
        {"term": "Mosca's inequality", "meaning": "If secrecy years X + migration years Y > years to a quantum computer Z, the data is already at risk."},
        {"term": "ML-KEM-768", "meaning": "FIPS 203 lattice key-encapsulation mechanism; 1184-byte public key, 1088-byte ciphertext."},
        {"term": "hybrid KEM", "meaning": "Classical + post-quantum secrets combined in a KDF; secure if either part holds."},
        {"term": "crypto agility", "meaning": "Replacing algorithms by configuration through one interface, with algorithm names carried in data."},
        {"term": "ratchet test", "meaning": "A test that allows the list of known issues to shrink but never to grow."},
    ],
    "concepts": ["Shor breaks RSA/ECC, not AES-256/SHA-256.", "Inventory by parsing code, not grepping words.",
                 "Prioritise key establishment for long-lived data.", "Agility: one interface, algorithm by name, receivers first."],
    "steps": [
        step("Run the lab", "python pqc_lab.py",
             "Shor context: RSA-2048 6190 logical / 9,025,020 physical qubits / 57,870 s (lesson 19), ECC P-256 2330 logical; grep inventory: 5 findings, 0 P1.",
             "ImportError estimate_lab: lesson 19's folder must exist next to this one."),
        step("See the fault", "Read the grep findings.",
             "toy_app/auth.py:1 is a docstring ('RSA was removed'); X25519, ECDH P-384 and ECDSA are missing; usage 'unknown', so no P1.",
             "If you see 8 findings you are running the solution."),
        step("Run the AST inventory", "python solution_scanner.py",
             "8 findings; P1 = billing.py:7 RSA-3072 (OAEP, 10 years) and sync.py:7 ECDH P-384 (7 years); AES-GCM kept.",
             "Missing sync.py: resolve 'from ...asymmetric.ec import ECDH' imports too."),
        step("Measure agility options", "Read the last three lines of pqc_lab.py.",
             "x25519 32/32 B, ml-kem-768 1184/1088 B, hybrid 1216/1120 B; ms per exchange varies by machine.",
             "UnsupportedAlgorithm: cryptography < 47 or a backend without ML-KEM; install labs/L400/requirements.txt."),
        step("Try it", "python try_it.py", "8-year API secrecy adds api_client.py:11 to P1; an X25519-only receiver rejects the hybrid envelope ('unknown kem').",
             "Compare with the tryIt predictions."),
        build_step("my_scanner", "pqc_lab",
                   "Your file / solution: Ran 7 tests ... OK. Shipped pqc_lab (grep): FAILED (failures=6) - inventory differs, docstring flagged, aliases missed, ratchet and recall fail.",
                   "Track aliases: 'from ...asymmetric import ec as curves' makes curves.ECDSA an ECDSA call."),
        step("Agent assist (fake model) and all tests", "python agent_assist.py --fake; python -m unittest -v",
             "draft ACCEPT; summarise REJECT (AES replaced, P1 sync.py missing); creative REJECT (invented file, ECDSA->ML-KEM, 2029). Ran 19 tests ... OK.",
             "Real model: start Ollama and set LOCAL_MODEL_URL / LOCAL_MODEL; tests always use the fake server.",
             "export LOCAL_MODEL_URL=http://localhost:11434/v1 LOCAL_MODEL=qwen2.5:1.5b && python agent_assist.py --show",
             '$env:LOCAL_MODEL_URL="http://localhost:11434/v1"; $env:LOCAL_MODEL="qwen2.5:1.5b"; python agent_assist.py --show'),
    ],
    "codeWalkthrough": [
        {"title": "shor_context.py", "detail": "Reuses lesson 19's estimator for RSA-2048 and adds Roetteler et al.'s ECC bound (9n + 2 ceil(log2 n) + 10 logical qubits): 2330 for P-256."},
        {"title": "pqc_lab.scan (the fault)", "detail": "A regex for 'rsa' over files: finds words, not uses - a docstring is flagged, X25519/ECDH/ECDSA are invisible, usage is unknown."},
        {"title": "pqc_lab.plan", "detail": "Code decides priority: key establishment with secrecy X + 3 > 9 is P1 (HNDL); other public-key use P2 before 2030; symmetric is kept."},
        {"title": "solution_scanner.aliases / dotted", "detail": "Resolves 'ec as curves' and 'from ...ec import ECDH' to canonical names, so calls are matched by meaning, not spelling."},
        {"title": "solution_scanner.RULES", "detail": "Canonical call -> (algorithm, purpose); RSA's purpose comes from OAEP vs PSS in the same file, the curve from SECPxxxR1."},
        {"title": "agility.Hybrid + REGISTRY + CONFIG", "detail": "One KEM interface; the hybrid HKDFs ML-KEM-768 and X25519 secrets (IR 8547's composite form); envelopes name the algorithm."},
        {"title": "agent_assist.check", "detail": "Every note line is checked against the inventory: location, algorithm, replacement, priority, missing P1 items and dates."},
    ],
    "designBrief": {
        "context": "A legacy app uses RSA-OAEP for archived card tokens, ECDH for replication, X25519 for a partner API, ECDSA for session tokens and RSA/ECDHE in its TLS config. NIST IR 8547 deprecates these after 2030 and disallows them after 2035.",
        "constraints": ["inventory recall and precision = 1.0 against a hand-checked ground truth", "priorities computed by code from data lifetimes",
                        "the next algorithm swap must be a configuration change", "no new quantum-vulnerable use may be added (ratchet)",
                        "agent output never decides; it is checked fact by fact"],
        "question": "How do we find every quantum-vulnerable use, in what order do we migrate, and how do we keep the code agile?"},
    "options": [
        {"name": "A replace at each call site", "description": "Swap X25519/ECDH/RSA for ML-KEM-768 where they are used.", "evidence": "4 key-establishment sites now (and again next time); 1184/1088 B; no fallback.",
         "verdict": "Rejected."},
        {"name": "B agile interface + hybrid X25519+ML-KEM-768", "description": "establish()/accept() by name from a registry; envelopes carry 'kem'.",
         "evidence": "1216/1120 B; round-trips locally with cryptography 50.0.2; next swap = 1 config line.", "verdict": "Chosen (ADR 0001)."},
        {"name": "C wait until 2030", "description": "No change now.", "evidence": "P1 data (10 and 7 years) recorded today stays exposed beyond Z = 9 years.", "verdict": "Rejected."},
    ],
    "decisionRecord": "labs/L400/21-post-quantum-migration/docs/adr/0001-crypto-agility.md",
    "fitnessFunction": {"what": "Inventory matches ground truth; no new quantum-vulnerable use outside migration_baseline.json; the configured KEM is hybrid or post-quantum.",
                        "test": "labs/L400/21-post-quantum-migration/test_fitness.py",
                        "threshold": "recall = precision = 1.0; 0 findings outside the baseline (an injected ec.ECDH() is caught); CONFIG['kem'] in {x25519+ml-kem-768, ml-kem-768}"},
    "scalingLimits": ["Other languages, vendored libraries and binaries escape a Python AST scanner: measure recall on a hand-checked sample per repository.",
                      "~1.1 kB extra per handshake breaks MTU-bound or constrained-device protocols: signal = fragmentation or handshake timeouts.",
                      "Flag-day upgrades fail: senders that switch before receivers produce 'unknown kem' rejections - upgrade receivers first."],
    "failureLab": {"fault": "The shipped scan() greps for 'rsa' in .py and .toml files.",
                   "symptom": "5 findings (1 docstring false positive, duplicates), usage 'unknown', 0 P1 items; X25519, ECDH P-384 (P1!) and ECDSA are missing.",
                   "fix": "An AST scanner that resolves imports and aliases and classifies calls by purpose, plus comment-aware config rules (solution_scanner.py).",
                   "proof": "BUILD_TASK_MODULE=pqc_lab python -m unittest test_build_task test_fitness -> FAILED (failures=6); solution / BUILD_TARGET=mine -> Ran 7 tests OK."},
    "tradeOffs": [
        {"option": "Hybrid KEM", "gains": "Secure if either component holds; compliant composite", "costs": "Larger messages, two implementations, a second migration later", "chooseWhen": "Transition period (now)"},
        {"option": "Pure ML-KEM", "gains": "Smaller than hybrid, one algorithm", "costs": "No classical fallback if an implementation flaw appears", "chooseWhen": "Once implementations are mature and mandated"},
        {"option": "Grep inventory", "gains": "Instant, any language", "costs": "False positives and misses (recall 3/8 here)", "chooseWhen": "A first rough count only"},
    ],
    "buildTask": {"task": "Write scan(root=APP) returning the sorted inventory [{file, line, algorithm, usage}] of toy_app: resolve cryptography imports and aliases with ast, classify calls (key-establishment, signature, symmetric), parse configs without comments.",
                  "hints": ["ast.ImportFrom gives module and asname; map local names to 'ec', 'ec.ECDH', ...", "Walk ast.Call and rebuild dotted names from Attribute/Name nodes.",
                            "RSA purpose: padding.OAEP in the same file -> key-establishment, else signature."],
                  "solution": "labs/L400/21-post-quantum-migration/solution_scanner.py",
                  "check": "BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v (7 tests; stdlib + cryptography, runs locally)"},
    "expectedResults": ["AST inventory = EXPECTED_INVENTORY.json (8 items)", "P1: billing.py:7 RSA-3072 and sync.py:7 ECDH P-384",
                        "Hybrid X25519+ML-KEM-768 round-trips; 1216/1120 bytes"],
    "testCases": [{"action": "scan a copy of toy_app with one new ec.ECDH() file", "expected": "exactly 1 finding outside the baseline (ratchet fails)"},
                  {"action": "hybrid.combine with one secret changed", "expected": "a different key (both secrets matter)"},
                  {"action": "agent_assist.check('No idea.', plan)", "expected": "REJECT with 2 missing P1 items"}],
    "tryIt": [
        {"task": "Legal extends partner-API secrecy to 8 years (try_it.longer_secrecy).", "predict": "Which items become P1?",
         "expected": "api_client.py:11 joins billing.py:7 and sync.py:7 (8 + 3 > 9).", "validatedBy": "local: try_it.py (observed)"},
        {"task": "Sender uses the hybrid; a receiver only knows X25519 (try_it.old_receiver).", "predict": "Silent downgrade or failure?",
         "expected": "Failure: \"receiver rejects envelope: unknown kem 'x25519+ml-kem-768'\" - upgrade receivers first.", "validatedBy": "local: try_it.py (observed)"},
    ],
    "agentAssist": {"task": "A local model drafts migration notes (one line per vulnerable item: file:line | algorithm | replacement | priority) from the inventory facts.",
                    "prompt": "[[PQC-NOTES]] Draft the migration notes. Inventory: [{file, line, algorithm, usage, secrecy_years} ...]",
                    "check": "Code rejects any line whose file:line is not in the inventory, whose algorithm, replacement (ML-KEM-768 / ML-DSA-65) or priority differs from the plan, any symmetric item marked for replacement, any missing P1 item, and any year other than 2030/2035.",
                    "expected": "draft ACCEPT; summarise REJECT (storage.py:10 is symmetric; P1 item missing: toy_app/sync.py:7); creative REJECT (toy_app/payments.py:12 not in inventory; auth.py:11 'ML-KEM-768' != 'ML-DSA-65'; year 2029).",
                    "realModelNote": "Only paths, line numbers and algorithm names are sent - never keys or code. Small models often invent files or map signatures to KEMs; the check is the point.",
                    "validatedBy": "local: agent_assist.py --fake and test_agent_assist.py (4 tests) against the deterministic fake server"},
    "troubleshooting": [{"symptom": "UnsupportedAlgorithm for ML-KEM", "action": "cryptography >= 47 with an OpenSSL backend that supports ML-KEM is needed; the lab pins 50.0.2."},
                        {"symptom": "Leftover tmp* folder in the lab", "action": "test_fitness copies toy_app into a temp folder; on some network mounts cleanup fails - delete it (it is git-ignored)."}],
    "equivalents": ["OpenSSL 3.5+ and BoringSSL offer ML-KEM and the X25519MLKEM768 TLS group; liboqs / Open Quantum Safe for other PQC algorithms.",
                    "Inventory tools: CodeQL or Semgrep rules for crypto API calls; CycloneDX CBOM to record a cryptographic bill of materials.",
                    "Signatures: ML-DSA (FIPS 204) and SLH-DSA (FIPS 205) replace RSA/ECDSA/EdDSA."],
    "inRealSystems": ["Organisations start with cryptographic inventories (NIST IR 8547 and the NCCoE project) and migrate TLS key exchange first.",
                      "Browsers and CDNs already negotiate hybrid X25519+ML-KEM-768 key exchange."],
    "useWhen": "Use an AST-based inventory plus an agile KEM interface for any codebase with long-lived confidential data; avoid one-off call-site rewrites.",
    "simulatorVsReal": "No quantum simulation: real ML-KEM-768 and X25519 from cryptography 50.0.2 run locally. Shor numbers are estimates (lesson 19 and the cited papers), not a demonstration.",
    "caution": "Never send keys, tokens or source code to a model; the agent sees only inventory facts. The agent never decides priorities or replacements - code does. Do not use the toy app's crypto choices as a production design.",
    "checkYourself": [{"q": "Why is sync.py P1 but auth.py not?", "a": "sync.py establishes keys for 7-year data (7 + 3 > 9 -> harvestable); auth.py signs session tokens: signatures are not exposed to harvest-now-decrypt-later."},
                      {"q": "Why keep AES-256-GCM?", "a": "Shor does not break symmetric crypto; IR 8547 does not expect to transition AES-256 or SHA-256."},
                      {"q": "Why does the envelope carry the algorithm name?", "a": "Receivers pick the algorithm from data, so senders can switch by config and old receivers fail loudly."}],
    "checkpoint": "PASS if the grep inventory's misses are explained, your scanner passes test_build_task and test_fitness, the hybrid KEM round-trips, and the agent's bad notes are rejected by code.",
    "learningTools": [
        tool(JUPYTER, "Plot a Mosca timeline per inventory item: bars for X (secrecy years) + Y = 3 against Z = 9, coloured by the plan's priority.",
             "Two bars cross Z: billing.py (10 + 3) and sync.py (7 + 3); with 8-year API secrecy api_client.py (8 + 3) crosses too (try it 1)."),
    ],
    "seeAlso": ["cryptography L200 #8 Key exchange and hybrid encryption (X25519 + HKDF + AEAD): the X25519 + HKDF pattern this lesson makes hybrid with ML-KEM-768.",
                "cryptography L300 #12 Envelope encryption and key rotation: versioned envelopes that name their algorithm are what makes rotation and migration possible.",
                "cryptography L400 #17 Crypto agility: versioned envelopes, negotiation and dual signing: the cryptography topic's full agility design (negotiation, dual signing) behind this lesson's KEM registry.",
                "cryptography L400 #18 Post-quantum cryptography in practice: ML-KEM, ML-DSA and hybrids: ML-DSA signatures and hybrid details this lesson only names as phase 2.",
                "L400 #19 Resource estimation: logical vs physical qubits and feasibility: the RSA-2048 numbers used here."],
    "sources": src("nist8547", "fips203", "gidney2019", "gidney2025", "roetteler", "crypto_mlkem", "cswp39", "ollama_openai"),
    "next": "Capstone #22 Capstone: an end-to-end quantum optimisation service: put lessons 12-20 together behind one API.",
    "how": RAN + "`python pqc_lab.py`, `python solution_scanner.py`, `python try_it.py`, `python agent_assist.py --fake` (outputs in README); `python -m unittest` -> 19 tests OK (ML-KEM-768 ran locally); fail-before proof with BUILD_TASK_MODULE=pqc_lab observed (6 failures).",
    "pendingCi": [],
    "projectFiles": [("pqc_lab.py", "main lab: Shor context, grep inventory (fault), Mosca plan, agility measurements"),
                     ("shor_context.py", "reuses lesson 19's estimator; ECC bound"), ("agility.py", "KEM registry: X25519, ML-KEM-768, hybrid; envelopes"),
                     ("toy_app/", "the codebase to inventory (+ config/tls.toml, data_classification.json)"),
                     ("EXPECTED_INVENTORY.json", "hand-checked ground truth"), ("migration_baseline.json", "ratchet baseline (may only shrink)"),
                     ("solution_scanner.py", "buildTask reference: AST inventory"), ("buildtarget.py", "BUILD_TARGET=mine / BUILD_TASK_MODULE switch"),
                     ("test_build_task.py", "buildTask + failureLab proof"), ("test_fitness.py", "fitness: recall/precision, ratchet, configured KEM"),
                     ("test_pqc.py", "Shor context, priorities, agility"), ("agent_assist.py", "agent drafts notes, code checks them"),
                     ("fake_pqc_rule.py", "deterministic fake-model rule"), ("test_agent_assist.py", "agent assist tests (fake server)"),
                     ("docs/adr/0001-crypto-agility.md", "decision record"), ("README.md", "run commands and observed output")],
    "summary": "Shor breaks RSA and ECC (RSA-2048: 20 million qubits in 2019, under a million in 2025; 9.0 million in lesson 19's data-only model), and recorded traffic is at risk now. Inventory crypto by parsing code, prioritise key establishment by Mosca's X + Y > Z, and put it behind an agile interface with a hybrid X25519 + ML-KEM-768 - the next swap is a config line.",
}


CAPSTONE = {
    "dir": "22-capstone", "file": "run_capstone.py", "id": "capstone-quantum-optimisation-service", "number": 22,
    "title": "Capstone: an end-to-end quantum optimisation service",
    "phase": "Capstone", "category": "capstone",
    "description": "An HTTP service that gates each MaxCut request on a resource estimate, runs noisy QAOA through the lesson 17 orchestrator on a compiled fake device, mitigates readout error, benchmarks it fairly against classical solvers, lets code pick the winner and has a local model explain the report.",
    "outcome": "You can assemble the topic's labs into one service with explicit decisions (four ADRs), prove each milestone with tests, and print a scorecard where code - not the agent - decides which solver wins under the budget.",
    "sdk": "optional: swap NoisyBackend for a Qiskit Aer adapter and the mitigation for Mitiq REM (not built; see KNOWN-GAPS)",
    "estimatedTime": "2-4 hours",
    "overview": ["One request, every lesson: feasibility gate (19), orchestrated noisy QAOA (17, 12, 20), mitigation (13), fair benchmark (18), code decides, agent explains."],
    "prerequisites": ["L400 #17-#21", "L300 #12 and #13 (noise, mitigation)", "L100 #5 agent assist pattern (model proposes, code decides)"],
    "designBrief": {
        "context": "Clients post MaxCut instances (4-16 nodes) and want the best cut and an honest answer to 'should we use the quantum solver?'. The only device is a fake 8-qubit ladder with a drifted coupler; backend jobs fail transiently.",
        "constraints": ["every solver gets the same sample budget and seeds", "a request the device cannot hold never reaches the quantum path",
                        "modelled wall time per request <= 60 s, one transpile per request", "transient job failures do not change results",
                        "the agent only explains; code decides; nothing binds beyond 127.0.0.1"],
        "question": "What does the service run for each request, and who decides which solver's answer wins?"},
    "architecture": {"diagram": "labs/L400/22-capstone/architecture.mmd",
                     "summary": "service.py validates POST /solve and calls pipeline.solve: a lesson-19 feasibility gate decides whether a quantum path exists; if so, lesson 17's Orchestrator (batched jobs, structural cache, retries) drives SPSA-trained QAOA on a NoisyBackend adapter that compiles with lesson 20's router (ESP, depth budget) and samples a white-noise + readout model checked against a density-matrix simulation; lesson 13's constrained mitigation corrects the readout bias of <C>; lesson 18's fair harness runs greedy, annealing and QAOA at the same budget and seeds and decide() picks the winner; agent_assist.py asks a local model to explain the report and code rejects explanations whose winner, numbers or claims disagree."},
    "milestones": [
        {"title": "M1 API and validation", "deliverable": "service.py: POST /solve, GET /health on 127.0.0.1; invalid input -> HTTP 400", "test": "labs/L400/22-capstone/test_milestones.py::M1Api"},
        {"title": "M2 Orchestrated quantum path", "deliverable": "Batched jobs, 1 transpile, idempotent retries through lesson 17's Orchestrator", "test": "labs/L400/22-capstone/test_milestones.py::M2Orchestration"},
        {"title": "M3 Compile + noise model", "deliverable": "noisy_backend.py: lesson 20 routing within a 60-layer budget; white-noise model within TVD 0.03 of the density matrix", "test": "labs/L400/22-capstone/test_milestones.py::M3CompileAndNoise"},
        {"title": "M4 Readout mitigation", "deliverable": "Tensored calibration + lesson 13 constrained mitigation of <C>", "test": "labs/L400/22-capstone/test_milestones.py::M4Mitigation"},
        {"title": "M5 Fair benchmark + code decides", "deliverable": "Lesson 18 harness with the request's budget and seeds; decide(); feasibility refusal for n > 8", "test": "labs/L400/22-capstone/test_milestones.py::M5BenchmarkAndDecision"},
        {"title": "M6 Agent explains, code checks", "deliverable": "agent_assist.py: explanation accepted only if winner, numbers and claims match the report", "test": "labs/L400/22-capstone/test_milestones.py::M6AgentExplains"},
    ],
    "rubric": [
        {"criterion": "correctness", "measure": "winner's median approximation ratio", "pass": ">= 0.95 (observed 1.0)"},
        {"criterion": "fairness", "measure": "budget and seed list per solver", "pass": "identical for every solver (2000 samples, 5 seeds)"},
        {"criterion": "reliability", "measure": "benchmark rows with 2 injected job failures vs none", "pass": "identical (2 retries)"},
        {"criterion": "cost", "measure": "modelled wall time and jobs per request", "pass": "<= 60 s (observed 28.8 s, 10 jobs)"},
        {"criterion": "honesty", "measure": "12-node request on the 8-qubit device", "pass": "quantum path refused with a reason; classical answer returned"},
        {"criterion": "safety", "measure": "agent 'pitch' claiming a QAOA win / quantum advantage; server bind address", "pass": "rejected by code; 127.0.0.1 only"},
    ],
    "fitnessFunctions": [
        {"what": "Execution budget: modelled wall <= 60 s and exactly 1 transpile per request (ADR 0001)", "test": "labs/L400/22-capstone/test_fitness.py::test_execution_budget", "threshold": "wall_s <= 60; transpiles == 1"},
        {"what": "Code decides and ties go classical (ADR 0002)", "test": "labs/L400/22-capstone/test_fitness.py::test_code_decides_and_ties_go_classical", "threshold": "winner == decide(rows); tie -> greedy/annealing"},
        {"what": "Mitigation helps (ADR 0003)", "test": "labs/L400/22-capstone/test_fitness.py::test_mitigation_helps", "threshold": "|mitigated - gate-only| < |raw - gate-only|"},
        {"what": "Feasibility gate (ADR 0004)", "test": "labs/L400/22-capstone/test_fitness.py::test_feasibility_gate", "threshold": "n = 12 never reaches qaoa-noisy"},
        {"what": "Rubric", "test": "labs/L400/22-capstone/test_fitness.py::test_rubric", "threshold": "6/6 rubric lines pass"},
    ],
    "decisionRecords": ["labs/L400/22-capstone/docs/adr/0001-service-execution.md", "labs/L400/22-capstone/docs/adr/0002-code-decides-winner.md",
                        "labs/L400/22-capstone/docs/adr/0003-readout-mitigation-only.md", "labs/L400/22-capstone/docs/adr/0004-feasibility-gate-first.md"],
    "steps": [
        step("Run the scorecard", "python run_capstone.py",
             "6 milestone lines and 6 rubric lines, all pass; final {\"scorecard\": \"6/6 milestones, 6/6 rubric\", \"winner\": \"annealing\", \"decided_by\": \"code\"}.",
             "ModuleNotFoundError: the capstone imports labs 13 and 17-20 from their folders; keep the repository layout."),
        step("Read the report", "python pipeline.py  (one default request, report as JSON)",
             "optimum 10; greedy/annealing/qaoa-noisy all ratio 1.0, success 1.0; samples to best 32 / 13 / 1013 -> winner annealing; execution 10 jobs, 2 retries, 1 transpile, 28.8 s.",
             "A different winner: check budget 2000, seeds 5, graph_seed 3."),
        step("Call the API yourself", "python service.py --port 8765, then POST a request from another terminal.",
             "200 with the report for {\"n\": 8}; 400 'n must be an integer in [4, 16]' for {\"n\": 30}; {\"n\": 12} -> quantum path refused, annealing answers.",
             "Connection refused: the server binds 127.0.0.1 only.",
             "python service.py --port 8765 &  curl -s -X POST 127.0.0.1:8765/solve -d '{\"n\": 12}'",
             "Start-Process python 'service.py --port 8765'; Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8765/solve -Body '{\"n\": 12}'"),
        step("Agent explanation (fake model)", "python agent_assist.py --fake",
             "explain ACCEPT; pitch REJECT (claims qaoa-noisy wins; quantum advantage; 99.9 not in the report); brief REJECT (no winner stated).",
             "Real model: start Ollama and set LOCAL_MODEL_URL / LOCAL_MODEL; tests always use the fake server."),
        step("Try it", "python try_it.py", "budget 400: annealing still wins, all three succeed; no drift: ESP 0.5103 (vs 0.5072 drifted), 47 CX, depth 48.",
             "Compare with the tryIt predictions."),
        step("Run every milestone test", "python -m unittest -v", "Ran 13 tests ... OK (6 milestone + 5 fitness + 2 tryIt).",
             "One test per milestone; a failing milestone names the measure that broke."),
    ],
    "codeWalkthrough": [
        {"title": "reuse.py", "detail": "Appends the earlier lab folders to sys.path (module names are unique) and imports them - the capstone reuses, never copies."},
        {"title": "pipeline.validate / feasibility", "detail": "Rejects out-of-range requests before work; lesson 19's estimate + the 8-qubit device size decide whether a quantum path exists."},
        {"title": "pipeline.qaoa_solver", "detail": "A lesson-18-compatible solver: half the budget trains angles via lesson 17's Orchestrator (SPSA, batched, cached, retried), half samples answers."},
        {"title": "noisy_backend.NoisyBackend", "detail": "Overrides transpile() (lesson 20 routing, ESP, layout search) and sample() (white-noise F x ideal + (1 - F) uniform, then per-qubit readout flips)."},
        {"title": "pipeline.mitigation", "detail": "Per-qubit calibration -> tensored assignment matrix -> lesson 13 constrained mitigation of the measured distribution; compares raw, mitigated, gate-only and ideal <C>."},
        {"title": "pipeline.solve -> l18_fair.compare + decide", "detail": "Same budget, same seeds, medians; code's decide() names the winner; ties go classical."},
        {"title": "run_capstone.collect / milestones / rubric", "detail": "Real HTTP calls on 127.0.0.1, a fault-free re-run for idempotency, the white-noise check and the fake-model explanation, turned into JSON scorecard lines."},
    ],
    "expectedResults": ["Scorecard 6/6 milestones, 6/6 rubric; winner annealing decided by code", "Mitigation: raw 6.774 -> mitigated 6.8549 vs gate-only 6.8418",
                        "n = 12 refused for the quantum path with a reason"],
    "testCases": [{"action": "POST {\"n\": 30}", "expected": "HTTP 400, pipeline not run"},
                  {"action": "solve({'faults': []}) vs default (faults [3, 4])", "expected": "identical benchmark rows (excluding local_s)"},
                  {"action": "agent 'pitch' explanation", "expected": "REJECT: wrong winner, quantum-advantage claim, invented 99.9"}],
    "tryIt": [
        {"task": "Cut the budget to 400 samples (try_it.small_budget).", "predict": "Does QAOA catch up when samples are scarce?",
         "expected": "No change in winner: annealing; all three still succeed at n = 8.", "validatedBy": "local: try_it.py (observed)"},
        {"task": "Remove the calibration drift (try_it.calibrated_device).", "predict": "How much fidelity did the drift cost after noise-aware layout?",
         "expected": "Little: ESP 0.5103 vs 0.5072, gate fidelity 0.6262 vs 0.6224 - the layout search already routes around the bad coupler.", "validatedBy": "local: try_it.py (observed)"},
    ],
    "agentAssist": {"task": "A local model explains the benchmark report to an engineer in 2-4 sentences.",
                    "prompt": "[[QOPT-REPORT]] Explain the result. Report: {winner, optimum, benchmark rows, feasibility, mitigation, execution}",
                    "check": "Code rejects an explanation that names a different winner than decide(), quotes any number not present in the report, or claims a quantum advantage/speed-up; it never changes the winner.",
                    "expected": "explain ACCEPT; pitch REJECT (claims qaoa-noisy wins; quantum advantage; 99.9 not in the report); brief REJECT (no winner stated).",
                    "realModelNote": "Only report numbers and solver names are sent. Expect real small models to round numbers or add superlatives; the checker will reject those - tighten the prompt, never the check.",
                    "validatedBy": "local: agent_assist.py --fake and test_milestones M6 against the deterministic fake server"},
    "troubleshooting": [{"symptom": "The run takes minutes", "action": "Each solve trains QAOA for 5 seeds; run_capstone does 3 solves (default, n = 12, fault-free). Lower seeds in the request to iterate faster."},
                        {"symptom": "M2 fails on 'rows identical'", "action": "A retry changed samples: circuit seeds must not depend on attempts."}],
    "equivalents": ["Qiskit Runtime batch/session + SamplerV2 behind the same adapter interface; Qiskit Aer NoiseModel instead of the white-noise model.",
                    "Mitiq REM (inverse confusion matrix) as the mitigation step; Microsoft QDK estimator as the feasibility gate.",
                    "Any web framework (FastAPI, Flask) instead of http.server; the pipeline is framework-free."],
    "inRealSystems": ["Quantum cloud offerings wrap optimisation in a service that routes to classical solvers when they win.",
                      "Decision logic stays in reviewed code; LLM assistants summarise reports for people."],
    "useWhen": "Use this shape (gate -> orchestrate -> benchmark -> decide -> explain) for any 'quantum or classical?' service; avoid letting a model or a single run choose the solver.",
    "simulatorVsReal": "All quantum execution is the numpy simulator behind an adapter, with a white-noise + readout model (TVD 0.0213 from a density-matrix simulation) and modelled queue time. A real backend changes timings, noise and costs, not the architecture.",
    "caution": "The service binds 127.0.0.1 only. Never expose it or a local model beyond a trusted network, and never send credentials or customer data to a model; the agent sees report numbers only.",
    "checkYourself": [{"q": "Who decided that annealing wins?", "a": "decide() in lesson 18's code: equal ratio and success, fewest samples to the best cut (13). The agent only explained it."},
                      {"q": "Why is mitigated <C> (6.8549) still below ideal (7.3525)?", "a": "Readout mitigation removes readout bias only; gate noise (fidelity 0.6224) remains."},
                      {"q": "Why does n = 12 still get an answer?", "a": "The feasibility gate refuses the quantum path for an 8-qubit device; classical solvers answer with the same harness."}],
    "checkpoint": "PASS if run_capstone.py prints 6/6 milestones and 6/6 rubric, you can trace each number to its lesson, and changing the winner requires changing code, not the model.",
    "learningTools": [
        tool(JUPYTER, "Call pipeline.solve({}) in a notebook and plot raw / mitigated / gate-only / ideal <C> as bars, plus samples-to-best per solver.",
             "Bars 6.774 / 6.8549 / 6.8418 / 7.3525; samples to best greedy 32, annealing 13, qaoa-noisy 1013 (README output)."),
        tool(MARIMO, "`marimo edit`: sliders for budget (200-4000), seeds (3-10) and drift on/off; a cell shows pipeline.solve(...)['winner'] and the benchmark rows.",
             "Default (2000, 5, drift) -> annealing; 400 samples -> annealing; no drift -> ESP 0.5103."),
        tool(MITIQ, "Build Mitiq's inverse confusion matrix (REM guide) from the report's per-qubit readout rates and apply it to the same raw distribution; compare <C> with the lab's constrained 6.8549.",
             "Should land close to 6.8549 for <C> (the plain inverse may give small negative probabilities that the lab's constrained method avoids)."),
    ],
    "seeAlso": ["L400 #17 Hybrid quantum-classical architecture: orchestrator, job queue and backend adapter: the orchestrator and cache key used unchanged.",
                "L400 #18 Benchmarking honestly against classical solvers: the fair harness and decide() that pick the winner.",
                "L400 #19 Resource estimation: logical vs physical qubits and feasibility: the feasibility gate.",
                "L400 #20 Error-aware compilation: layout, routing and a depth budget: the router and ESP inside the noisy backend.",
                "application-architecture L300 #16 Performance and architecture fitness functions in CI: the same 'fitness function keeps the decision true' idea at service level."],
    "sources": src("ibm_modes", "farhi", "nishio", "fowler", "mitiq_rem", "abbas", "ollama_openai"),
    "next": "Done: see the L400 candidates in KNOWN-GAPS for further study.",
    "how": RAN + "`python run_capstone.py` (scorecard 6/6 + 6/6), `python pipeline.py`, `python agent_assist.py --fake`, `python try_it.py` (outputs in README); `python -m unittest` -> 13 tests OK (real HTTP on 127.0.0.1, fake model server).",
    "pendingCi": [],
    "projectFiles": [("run_capstone.py", "main: end-to-end run and scorecard (JSON lines)"), ("pipeline.py", "the service logic: gate, orchestrate, mitigate, benchmark, decide"),
                     ("service.py", "HTTP API on 127.0.0.1"), ("noisy_backend.py", "backend adapter: compile + noise model + white-noise check"),
                     ("reuse.py", "imports labs 13 and 17-20"), ("agent_assist.py", "local model explains; code checks"), ("fake_explain_rule.py", "deterministic fake-model rule"),
                     ("architecture.mmd", "Mermaid architecture diagram"), ("test_milestones.py", "one test per milestone"), ("test_fitness.py", "capstone fitness functions"),
                     ("docs/adr/", "ADRs 0001-0004"), ("README.md", "run commands and observed output")],
    "summary": "One service, every lesson: a resource-estimate gate, an orchestrator with batched jobs and idempotent retries, a noise-aware compiled backend with a validated noise model, readout mitigation, a fair benchmark and a code-made decision. For simulator-sized MaxCut the classical solver wins, and the service says so with evidence; a local model may explain, but code checks every claim.",
}

LESSONS = [L17, L18, L19, L20, L21]
COMMON = ("id", "number", "level", "title", "phase", "category", "description", "outcome", "environment", "estimatedTime", "overview",
          "prerequisites")


def files(d, lab_dir):
    out = [{"path": posixpath.normpath(f"{LABS}/{lab_dir}/{p}"), "purpose": why} for p, why in d["projectFiles"]]
    return out + [{"path": f"{LABS}/{lab_dir}/try_it.py", "purpose": "runs the two tryIt changes"},
                  {"path": f"{LABS}/{lab_dir}/test_try_it.py", "purpose": "tryIt tests"}]


def exists(path):
    assert os.path.exists(os.path.join(ROOT, path.split("::")[0])), path


def validation(d):
    tried = " ".join(f"tryIt {i}: {t['validatedBy']}." for i, t in enumerate(d["tryIt"], 1))
    if "agentAssist" in d:
        tried += f" agentAssist: {d['agentAssist']['validatedBy']}."
    pending = d["pendingCi"] + [f"learningTools: {t['name']} exercise (manual run)" for t in d["learningTools"]]
    return {"status": "validated-local", "how": f"{d['how']} {tried} Platforms: {PLATFORM_NOTE}", "pendingCi": pending}


def lesson(d, level):
    lab_dir, main = d["dir"], d["file"]
    with open(os.path.join(ROOT, LABS, lab_dir, main), encoding="utf-8") as f:
        code = f.read()
    obj = {"id": d["id"], "number": d["number"], "level": level}
    obj.update({k: d[k] for k in ("title", "phase", "category", "description", "outcome")})
    obj["environment"] = ENV.format(sdk=d["sdk"])
    obj.update({k: d[k] for k in ("estimatedTime", "overview", "prerequisites")})
    for k in ("glossary", "concepts"):
        if k in d:
            obj[k] = d[k]
    obj["designBrief"] = d["designBrief"]
    if level == "Capstone":
        obj.update({k: d[k] for k in ("architecture", "milestones", "rubric", "fitnessFunctions", "decisionRecords")})
    else:
        obj.update({k: d[k] for k in ("options", "decisionRecord", "fitnessFunction", "scalingLimits")})
    obj["steps"], obj["code"], obj["codeLanguage"], obj["codeWalkthrough"] = d["steps"], code, "python", d["codeWalkthrough"]
    obj["projectFiles"] = files(d, lab_dir)
    if level != "Capstone":
        obj["failureLab"], obj["tradeOffs"], obj["buildTask"] = d["failureLab"], d["tradeOffs"], d["buildTask"]
    obj["expectedResults"], obj["testCases"] = d["expectedResults"], d["testCases"]
    obj["tryIt"] = [{k: v for k, v in t.items() if k != "validatedBy"} for t in d["tryIt"]]
    if "agentAssist" in d:
        obj["agentAssist"] = {k: v for k, v in d["agentAssist"].items() if k != "validatedBy"}
    obj["troubleshooting"], obj["equivalents"] = d["troubleshooting"], d["equivalents"]
    obj["inRealSystems"], obj["useWhen"], obj["simulatorVsReal"] = d["inRealSystems"], d["useWhen"], d["simulatorVsReal"]
    if "caution" in d:
        obj["caution"] = d["caution"]
    obj["checkpoint"], obj["checkYourself"], obj["learningTools"] = d["checkpoint"], d["checkYourself"], d["learningTools"]
    obj["platforms"] = dict(PLATFORMS)
    obj["seeAlso"], obj["sources"], obj["next"] = d["seeAlso"], d["sources"], d["next"]
    obj["validation"] = validation(d)
    note = f"content/concepts/L400/{lab_dir}.md"
    obj["conceptNote"], obj["conceptSummary"] = note, d["summary"]
    for p in [note] + [f["path"] for f in obj["projectFiles"]] + ([d["decisionRecord"], d["fitnessFunction"]["test"], d["buildTask"]["solution"]]
                                                                   if level != "Capstone" else d["decisionRecords"] + [d["architecture"]["diagram"]]
                                                                   + [m["test"] for m in d["milestones"]] + [f["test"] for f in d["fitnessFunctions"]]):
        exists(p)
    assert 5 <= len(obj["codeWalkthrough"]) <= 7 and len(obj["tryIt"]) == 2
    assert len(obj["learningTools"]) <= (3 if level == "Capstone" else 2)
    if level != "Capstone":
        assert 2 <= len(obj["options"]) <= 3 and 2 <= len(obj["tradeOffs"]) <= 3 and 2 <= len(obj["scalingLimits"]) <= 3
    else:
        assert 4 <= len(obj["milestones"]) <= 6 and 2 <= len(obj["decisionRecords"]) <= 4
    return obj


def build():
    out = [lesson(d, "L400") for d in LESSONS] + [lesson(CAPSTONE, "Capstone")]
    path = os.path.join(ROOT, "content", "L400.json")
    if os.path.exists(path):
        os.remove(path)                    # the storage mount can break in-place overwrite
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return path, out


if __name__ == "__main__":
    p, lessons = build()
    print(f"wrote {p}: {len(lessons)} lessons")
