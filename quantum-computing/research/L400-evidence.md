# L400 research evidence — quantum computing ("Design it", lessons 17–21 + capstone 22)

Method: kb/SPEC.md research method with the rubric of `L100-evidence.md` (I implementable, C current, A authoritative, O open, T transferable, D right depth; 0–2 each; keep ≥ 8/12). Every URL below was retrieved with web_fetch on 2026-10-28 unless marked otherwise. Vendor pages are used only for API facts or as one-line equivalents; numbers that drive decisions come from papers, standards or code that ran here.

Design decision for all six labs: as at L300, the sandbox cannot install Qiskit, Aer, Mitiq, PennyLane or the QDK. Every main lab, failureLab, build task, fitness test and tryIt therefore runs on numpy (labs/_shared/qsim and the new labs/_shared/qopt) plus cryptography 50.0.2, and each SDK path is a separate file listed in `validation.pendingCi`. Time-dependent behaviour (queues, retries, sessions) is modelled with a FakeClock, so no assertion depends on wall-clock time.

## Lesson 17 — Hybrid quantum-classical architecture
**Questions:** 1. Which execution modes do providers offer, and what do they cost? 2. How is a batch of parameter sets submitted as one job in Qiskit 2.x? 3. Which SPSA gains are standard?

| source | I C A O T D | score | decision |
|---|---|---|---|
| IBM docs "Introduction to Quantum Compute execution modes" | 2 2 2 1 2 2 | 11 | kept (vendor, facts only): job / batch / session; batch parallelises pre-processing, no exclusive access, no benefit for a single job; session = exclusive window, interactive TTL, max TTL, "Open Plan users cannot submit session jobs" |
| StatevectorSampler API (already listed, L300) | 2 2 2 2 2 2 | 12 | reused: one PUB with a parameter array = one job (sampler_qiskit.py) |
| Spall (1998) SPSA implementation (already listed, L300) | 2 1 2 1 2 2 | 10 | reused: gain exponents 0.602 / 0.101 |
| qiskit.compiler.transpile API | 2 2 2 2 2 2 | 12 | kept: optimization_level default 2, `seed_transpiler`, layout/routing method names |

**Key facts:** IBM's execution-modes guide states batches "do not provide any benefits when running a single job" and that sessions give exclusive access during a window that a TTL can end. The lab's numbers (486.8 / 66.8 / 11.7 s) are from its own FakeClock cost model, which is illustrative, not vendor pricing.

## Lesson 18 — Benchmarking honestly vs classical
**Questions:** 1. What did the original QAOA paper guarantee at p = 1? 2. What benchmarking practice does the quantum-optimisation community recommend? 3. Which classical baselines are standard?

| source | I C A O T D | score | decision |
|---|---|---|---|
| Farhi, Goldstone, Gutmann (2014) arXiv:1411.4028 | 1 2 2 2 2 2 | 11 | kept: QAOA definition; p = 1 on 3-regular graphs gives ratio ≥ 0.6924 (consistent with the lab's 0.6922 p = 1 SPSA result in lesson 17) |
| Abbas et al. (2024) Nat Rev Phys, arXiv:2312.02279 | 1 2 2 2 2 2 | 11 | kept: proposes clear metrics and comparisons with classical optimisation for benchmarking |
| Kirkpatrick et al. (1983) Science (PubMed record) | 1 1 2 1 2 2 | 9 | kept: original simulated annealing reference (the science.org page could not be fetched; PubMed abstract used) |
| scipy.optimize.dual_annealing (SciPy 1.18.0) | 2 2 2 2 1 1 | 10 | kept as an equivalent only (continuous domain) |

**Key facts:** TTS99 = budget × ln(0.01) / ln(1 − success) is computed in code (`tts99(0.5, 200) = 1329`). The n = 12 "QAOA win" is reported with its context: 1 of 5 other instances (try it 1).

## Lesson 19 — Resource estimation
**Questions:** 1. Which surface-code error model and constants does a maintained estimator use? 2. What do current RSA-2048 estimates say? 3. What are the T costs of rotations and Toffolis?

| source | I C A O T D | score | decision |
|---|---|---|---|
| Fowler et al. (2012) arXiv:1208.0928 | 1 1 2 2 2 2 | 10 | kept: surface-code logical error model (Eq. 11 cited by the QDK) |
| qdk.qre.models.qec.SurfaceCode API (Microsoft Learn) | 2 2 2 2 2 2 | 12 | kept: crossing_prefactor 0.03 (Fowler Eq. 11), error_correction_threshold 0.01, references to lattice surgery (arXiv:1111.4022) |
| Learn: How to install and use the resource estimator (updated 2026-07-31) | 2 2 2 1 2 2 | 11 | kept: `pip install "qdk[qre]"`, `QSharpApplication` from `qdk.qre.application`, `GateBased(error_rate, gate_time, measurement_time)`, `estimate(app, arch, isa_query=SurfaceCode.q() * RoundBasedFactory.q(), max_error=0.01)`, `as_frame()` |
| Learn: What is the Microsoft Quantum resource estimator? (updated 2026-10-21) | 1 2 2 1 2 2 | 10 | kept: application/architecture/QEC/error-budget inputs; OpenQASM accepted; Pareto frontier |
| qdk on PyPI (1.33.1, 2026-10-08) | 1 2 2 2 1 1 | 9 | kept: version, MIT, Python ≥ 3.10, `qdk.qre` submodule, telemetry opt-out `QDK_PYTHON_TELEMETRY=none` |
| pandas on PyPI (3.1.0) | 1 2 2 2 1 1 | 9 | kept for the pin (as_frame needs pandas), Python ≥ 3.11 |
| Gidney & Ekerå (2021) arXiv:1905.09749 | 2 2 2 2 2 2 | 12 | kept: 3n + 0.002 n lg n logical qubits, 0.3n³ + 0.0005 n³ lg n Toffolis, 500n² + n² lg n measurement depth; 20 M qubits / 8 h at p = 1e-3, 1 µs cycles, 10 µs reaction |
| Gidney (2025) arXiv:2505.15917 | 1 2 2 2 2 2 | 11 | kept: < 1 M noisy qubits, < 1 week, same assumptions |
| Ross & Selinger (2016) arXiv:1403.2975 | 2 1 2 2 2 2 | 11 | kept: typical T-count 3 log2(1/ε) per z-rotation |
| Amy et al. (2013) arXiv:1206.0758 | 1 1 2 2 2 1 | 9 | kept: Toffoli in Clifford+T with T-depth 3 (the 7-T count itself is verified in code against the Toffoli unitary) |
| Beverland et al. (2022) arXiv:2211.07629 | 1 2 2 2 2 2 | 11 | kept: layered estimation framework; "hundreds of thousands to millions of physical qubits" for practical advantage |

**Key facts:** ≈ 2d² physical qubits per logical qubit is d² data + (d² − 1) measurement qubits of the rotated code (arithmetic, stated as such). Our model is data-blocks-only; the QDK path in CI measures how much factories add. `OpenQASMApplication`'s import path (`qdk.qre.application`) is inferred from `QSharpApplication`'s (KNOWN-GAPS).

## Lesson 20 — Error-aware compilation
**Questions:** 1. What does each Qiskit optimisation level do with layout and noise? 2. How does Qiskit rescore layouts by error rate? 3. Is a product-of-fidelities metric established?

| source | I C A O T D | score | decision |
|---|---|---|---|
| Qiskit preset pass managers (levels 0–3) | 2 2 2 2 2 2 | 12 | kept: level 0 trivial layout; level 2 "best gate fidelities"; level 3 "noise adaptive qubit mapping" |
| VF2PostLayout API | 2 2 2 2 2 2 | 12 | kept: rescoring layouts with target error rates (avg 1q and 2q errors) after routing |
| GenericBackendV2 API | 2 2 2 2 2 2 | 12 | kept: seeded backend properties sampled from historical ranges; basis id/rz/sx/x/cx (we build a Target with our own errors instead) |
| Nishio et al. (2020) arXiv:1903.10963 | 1 1 2 2 2 2 | 10 | kept: error-aware compilation, estimated success probability as a "useful but imperfect" single-number metric |

**Key facts:** ESP ranked the options the same way as the lab's density-matrix simulation (0.2084 vs 0.7835 ESP; 0.8959 vs 0.9878 simulated fidelity), matching Nishio et al.'s "useful but imperfect".

## Lesson 21 — Quantum and post-quantum
**Questions:** 1. What exactly does NIST's final transition plan deprecate and when? 2. Is ML-KEM usable from Python today? 3. What do current Shor estimates say for RSA and ECC?

| source | I C A O T D | score | decision |
|---|---|---|---|
| NIST IR 8547 (final, Oct 2026) PDF + CSRC page | 2 2 2 2 2 2 | 12 | kept: RSA/ECDSA/EdDSA/DH/ECDH/MQV "deprecated after 2030, disallowed after 2035"; HNDL; Mosca's X + Y > Z; symmetric standards not expected to transition; hybrid composite Z' = Z ‖ T via SP 800-56C; crypto agility |
| FIPS 203 (ML-KEM) | 1 2 2 2 2 2 | 11 | kept: ML-KEM-512/768/1024 |
| cryptography docs: ML-KEM | 2 2 2 2 2 2 | 12 | kept: `MLKEM768PrivateKey.generate()`, `encapsulate()` → (32-byte secret, 1088-byte ciphertext), 1184-byte public key, added in 47.0.0 — all reproduced locally with 50.0.2 |
| NIST CSWP 39 (crypto agility, Dec 2025) | 1 2 2 2 2 1 | 10 | kept: definition of crypto agility; page says superseded by CSWP 39upd1 (the upd1 page could not be fetched) |
| Roetteler et al. (2017) arXiv:1706.06752 | 1 1 2 2 2 2 | 10 | kept: ≤ 9n + 2⌈log2 n⌉ + 10 qubits, ≤ 448 n³ log2 n + 4090 n³ Toffolis for n-bit ECC |
| NIST news 2026-10-27 | 1 2 2 2 1 1 | 9 | background only: prioritise FIPS 203 for long-lived data |

**Dropped:** postquantum.com and thequbitreport.com summaries of IR 8547 (secondary; the NIST PDF was fetched instead); quantumresourceestimator.com and entangledfuture.com (secondary calculators/blogs; the 2d² arithmetic is stated from the code structure instead).

## Capstone
Reuses lessons 13, 17–20 by import; sources: IBM execution modes, Farhi et al., Nishio et al., Fowler et al., Mitiq REM guide (L300), Abbas et al., Ollama OpenAI compatibility (L300). No new facts beyond those above.

## Numbers in the concept notes
Every number in `content/concepts/L400/*.md` is printed by a lab script or test that ran here (READMEs show the outputs): lesson 17 `solution_cache_key.py` / `try_it.py`; lesson 18 `solution_fair.py` / `try_it.py`; lesson 19 `solution_distance.py` / `try_it.py` / `test_estimate.py`; lesson 20 `compile_lab.py` / `solution_layout.py` / `test_compile.py`; lesson 21 `pqc_lab.py` / `solution_scanner.py` / `agent_assist.py --fake`; capstone `run_capstone.py`. Published figures (20 M qubits / 8 h; < 1 M / < 1 week; 2330 logical qubits for P-256 computed from Roetteler's bound; 2030 / 2035) are from the sources above.
