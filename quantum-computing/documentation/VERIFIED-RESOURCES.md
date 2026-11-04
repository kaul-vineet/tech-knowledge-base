# Verified resources (L100 + L200 + L300 + L400 + L500)

All URLs were retrieved with web_fetch on 2026-10-28. Score = implementable + current + authoritative + open + transferable + right depth (0–2 each, max 12). Only sources scoring ≥ 8 are kept. Rubric detail and the dropped sources are in `../research/L100-evidence.md`.

| title | url | type | licence | version-or-date checked | score/12 | used in lesson(s) |
|---|---|---|---|---|---|---|
| Install Qiskit | https://quantum.cloud.ibm.com/docs/en/guides/install-qiskit | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | Qiskit v2.x page, 2026-10-28 | 11 | 1 |
| qiskit on PyPI | https://pypi.org/project/qiskit/ | docs (package index) | Apache-2.0 | 2.6.1 (released 2026-10-22), Python ≥3.10 | 10 | 1 |
| qiskit-aer on PyPI | https://pypi.org/project/qiskit-aer/ | docs (package index) | Apache-2.0 | 0.18.2 (released 2026-10-26), Python ≥3.11; "reduced maintenance mode" | 10 | 1 (optional equivalent) |
| Qiskit Aer tutorial: Simulators | https://qiskit.github.io/qiskit-aer/tutorials/1_aersimulator.html | docs | Apache-2.0 | Aer 0.18.2 docs build (notebook shows qiskit 1.0.1) | 10 | equivalents (Aer), background |
| Qiskit Aer SamplerV2 API | https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.primitives.SamplerV2.html | docs | Apache-2.0 | Aer 0.18.2 | 11 | 3 (equivalent) |
| AerSimulator API | https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html | docs | Apache-2.0 | Aer 0.18.2 | 10 | 1 (16 bytes per amplitude, supporting) |
| Bit-ordering in the Qiskit SDK | https://quantum.cloud.ibm.com/docs/en/guides/bit-ordering | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | qiskit ~=2.5.2 page | 12 | 2, 4, 6 |
| qiskit.compiler.transpile API | https://quantum.cloud.ibm.com/docs/en/api/qiskit/compiler | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | latest (2.x) | 9 | 2 |
| Exact simulation with Qiskit SDK primitives | https://quantum.cloud.ibm.com/docs/en/guides/simulate-with-qiskit-sdk-primitives | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | qiskit ~=2.5.2 page | 11 | 1, 3, 4 |
| StatevectorSampler API | https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.primitives.StatevectorSampler | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | latest (2.x); `StatevectorSampler(*, default_shots=1024, seed=None)`, `run(pubs, *, shots=None)` (re-checked 2026-10-28) | 10 | 1–4 (main L100 simulator since the F25 fix) |
| Exact and noisy simulation with Qiskit Aer primitives | https://quantum.cloud.ibm.com/docs/en/guides/simulate-with-qiskit-aer | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | qiskit ~=2.5.2, aer ~=0.17 page | 10 | 3 (supporting) |
| qiskit.qasm3 API | https://quantum.cloud.ibm.com/docs/en/api/qiskit/qasm3 | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | latest (2.x) | 12 | 5 |
| qiskit.qasm2 API | https://quantum.cloud.ibm.com/docs/en/api/qiskit/qasm2 | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | latest (2.x) | 11 | 5 |
| qiskit.quantum_info.Operator API | https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.quantum_info.Operator | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | latest (2.x) | 10 | 5 (supporting: equiv) |
| qiskit-qasm3-import on PyPI | https://pypi.org/project/qiskit-qasm3-import/ | docs (package index) | Apache-2.0 | 0.6.0 (released 2025-06-10) | 9 | 5 |
| OpenQASM spec: Introduction | https://openqasm.com/intro.html | spec | Apache-2.0 (repo) | live spec (v3.x) | 11 | 5 |
| OpenQASM 3 standard library | https://openqasm.com/language/standard_library.html | spec | Apache-2.0 (repo) | live spec (v3.x) | 10 | 2, 4, 5 |
| openqasm/openqasm repo | https://github.com/openqasm/openqasm | repo | Apache-2.0 | current version 3.1 | 10 | 5 (licence/version) |
| cirq on PyPI | https://pypi.org/project/cirq/ | docs (package index) | Apache-2.0 | 1.7.0 (released 2026-06-29), Python ≥3.11 | 10 | 6 |
| Cirq install | https://quantumai.google/cirq/start/install | docs | Apache-2.0 (Cirq) | 2026-10-28 | 11 | 1, 6 (supporting) |
| Cirq: Simulation | https://quantumai.google/cirq/simulate/simulation | docs | Apache-2.0 (Cirq) | 2026-10-28 | 11 | 3, 6 |
| cirq.Result API | https://quantumai.google/reference/python/cirq/Result | docs | Apache-2.0 (Cirq) | stable | 10 | 6 |
| Cirq: Import/export circuits | https://quantumai.google/cirq/build/interop | docs | Apache-2.0 (Cirq) | 2026-10-28 | 11 | 5 (equivalents) |
| PennyLane: Quantum circuits | https://docs.pennylane.ai/en/stable/introduction/circuits.html | docs | Apache-2.0 | PennyLane 0.45.1 | 11 | equivalents (all) |
| amazon-braket-sdk-python | https://github.com/amazon-braket/amazon-braket-sdk-python | repo | Apache-2.0 | v1.127.4 (2026-10) | 9 | equivalents (all) |
| microsoft/qdk | https://github.com/microsoft/qdk | repo | MIT | v1.33.0 | 9 | equivalents (all) |
| Qiskit/documentation repo (licence evidence) | https://github.com/Qiskit/documentation | repo | Apache-2.0 code / CC BY-SA 4.0 content | 2026-10-28 | 9 | licence check for all quantum.cloud.ibm.com pages |
| IBM Quantum Learning — Basics of quantum information: Multiple systems (J. Watrous) | https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/multiple-systems/introduction | course | content CC BY-SA 4.0 (Qiskit/documentation) | page checked 2026-10-28 | 9 | 4 (supporting: entanglement background) |

Kept: **28** sources (17 cited in lesson `sources`, 4 back `equivalents` lines, 7 are supporting or licence evidence). The licence for quantum.cloud.ibm.com docs and learning pages comes from the Qiskit/documentation repository: code snippets are Apache-2.0 and prose is CC BY-SA 4.0. The pages themselves don't state it.

## Added for the concepts layer (retrieved 2026-10-28)

| title | url | type | licence | version-or-date checked | score/12 | used in lesson(s) |
|---|---|---|---|---|---|---|
| IBM Quantum Learning — Single systems: Quantum information (J. Watrous) | https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/single-systems/quantum-information | course | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | 2026-10-28 | 11 | primer; concept 02 |
| IBM Quantum Learning — Multiple systems: Quantum information (J. Watrous) | https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/multiple-systems/quantum-information | course | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | 2026-10-28 | 11 | primer; concept 04 |
| Introduction to transpilation | https://quantum.cloud.ibm.com/docs/en/guides/transpile | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | 2026-10-28 | 10 | primer; concept 01 |
| quantumlib/Stim | https://github.com/quantumlib/Stim | repo | Apache-2.0 | 2026-10-28 (main) | 9 | primer; concept 01 |
| quantumlib/OpenFermion | https://github.com/quantumlib/OpenFermion | repo | Apache-2.0 | 1.8.1 (CITATION.cff) | 9 | primer |
| S. Aaronson, Shtetl-Optimized: "Shor, I'll do it" | https://scottaaronson.blog/?p=208 | background (blog) | no open licence; quoted and summarised only, not reused | 2007 post, retrieved 2026-10-28 | 8 | primer (misconception 1) |

Concepts layer total: **6** new sources (34 kept overall). Existing sources reused in concept notes: AerSimulator API, Aer tutorial, Aer SamplerV2, bit-ordering guide, SDK primitives guide, OpenQASM intro and standard library, qiskit.qasm3, Cirq simulation, cirq.Result, Cirq interop, Install Qiskit, cirq PyPI, PennyLane, Braket SDK, QDK, qiskit PyPI.

## Platform and local-agent sources (PLATFORM-AGENT-SPEC, retrieved 2026-10-28)

| title | url | type | licence | version-or-date checked | score/12 | used in lesson(s) |
|---|---|---|---|---|---|---|
| Python docs: venv | https://docs.python.org/3/library/venv.html | docs | PSF-2.0 (docs) | 3.15.2 docs; activation per shell, Windows `Set-ExecutionPolicy` note | 12 | 1, HARDWARE |
| Python docs: Using Python on Windows | https://docs.python.org/3/using/windows.html | docs | PSF-2.0 (docs) | 3.15.2 docs; `py -3.x` launcher (install-manager route not used: the canonical install is winget `Python.Python.3.12`, see kb/shared/WORKSTATION-SETUP.md) | 12 | background |
| Python docs: os, Python UTF-8 Mode | https://docs.python.org/3/library/os.html#utf8-mode | docs | PSF-2.0 (docs) | UTF-8 mode default only from 3.15 (PEP 686); `PYTHONUTF8` | 11 | HARDWARE, CI |
| Homebrew formula python@3.12 | https://formulae.brew.sh/formula/python@3.12 | docs (package index) | BSD-2 (Homebrew); Python-2.0 | 3.12.16, Apple-silicon bottle | 10 | 1 |
| winget-pkgs: Python.Python.3.12 manifests | https://github.com/microsoft/winget-pkgs/tree/master/manifests/p/Python/Python/3/12 | repo (package index) | MIT | 3.12.0–3.12.10 manifests | 9 | 1 (canonical id) |
| Homebrew formula ollama | https://formulae.brew.sh/formula/ollama | docs (package index) | MIT | 0.40.11, Apple-silicon bottle, `brew services start ollama` | 10 | 1, HARDWARE |
| winget-pkgs: Ollama.Ollama manifests | https://github.com/microsoft/winget-pkgs/tree/master/manifests/o/Ollama/Ollama | repo (package index) | MIT | up to 0.34.2 (lags the 0.40.x releases, so lesson 1 uses the ollama.com installer) | 9 | HARDWARE (why not used) |
| Ollama: OpenAI compatibility | https://docs.ollama.com/api/openai-compatibility | docs | MIT (project) | `/v1/chat/completions` endpoint, temperature, seed | 11 | 1, 5, 8 |
| Ollama: Hardware support | https://docs.ollama.com/gpu | docs | MIT (project) | Metal on Apple; NVIDIA CC 5.0+ / driver 550+; Vulkan on Windows | 10 | HARDWARE |
| Ollama library: qwen2.5 | https://ollama.com/library/qwen2.5 | docs (model index) | Apache-2.0 for 1.5b (3B/72B Qwen licence) | `qwen2.5:1.5b` 986 MB | 8 | 1, 5 |
| qiskit-aer-gpu on PyPI | https://pypi.org/project/qiskit-aer-gpu/ | docs (package index) | Apache-2.0 | 0.18.0; wheels x86_64 Linux only | 10 | HARDWARE |
| Visualize circuits (Qiskit) | https://quantum.cloud.ibm.com/docs/en/guides/visualize-circuits | docs | code Apache-2.0 / content CC BY-SA 4.0 | qiskit ~=2.5.2 page; text drawer output uses box-drawing characters | 10 | HARDWARE (Windows UTF-8) |
| GitHub Actions runner images | https://github.com/actions/runner-images | repo | MIT | `macos-latest` = macOS 26 arm64, `windows-latest` = Server 2025 x64 | 10 | CI |

Platform layer: **13** new sources (47 kept overall). The qiskit-aer PyPI page (already listed) confirms the MacOS and Windows classifiers for 0.18.2.

## L200 additions (lessons 7–11)

All retrieved with web_fetch on 2026-10-28; rubric and dropped candidates in `../research/L200-evidence.md`. Reused from above: StatevectorSampler API (7, 10), Bit-ordering guide (7), Ollama OpenAI compatibility (8).

| title | url | type | licence | version-or-date checked | score/12 | used in lesson(s) |
|---|---|---|---|---|---|---|
| IBM Quantum Learning: The Deutsch-Jozsa algorithm (BV section) | https://quantum.cloud.ibm.com/learning/en/courses/fundamentals-of-quantum-algorithms/quantum-query-algorithms/deutsch-jozsa-algorithm | course | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation), as for the L100 IBM Learning pages | 2026-10-28; `bv_query`, 1 vs n queries | 12 | 7 |
| Cirq example: bernstein_vazirani.py | https://github.com/quantumlib/Cirq/blob/main/examples/bernstein_vazirani.py | repo | Apache-2.0 | main branch, 2026-10-28; bias bit | 12 | 7 |
| Grover's algorithm (IBM tutorial) | https://quantum.cloud.ibm.com/docs/en/tutorials/grovers-algorithm | docs (tutorial) | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | Qiskit SDK v2.0+; oracle, iteration formula, 2Q depth table | 12 | 8, 11 |
| grover_operator API | https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.grover_operator | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | latest (2.x) | 12 | 8 |
| Cirq: Textbook algorithms | https://quantumai.google/cirq/experiments/textbook_algorithms | docs (notebook) | Apache-2.0 | Cirq docs 2026-10-28; QFT, inverse, Grover | 12 | 8, 9 |
| QFTGate API | https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.QFTGate | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | latest (2.x); +i sign, 2^{-n/2} | 12 | 9 |
| QFT class API (deprecated) | https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.QFT | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | deprecated since 2.1, removal in 3.0 | 10 | 9 |
| cirq.qft API | https://quantumai.google/reference/python/cirq/qft | docs | Apache-2.0 | Cirq reference, 2026-10-28 | 12 | 9 |
| Statevector API | https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.quantum_info.Statevector | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | latest (2.x); evolve, probabilities_dict | 11 | 8, 9 |
| Parameter API | https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.Parameter | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | latest (2.x) | 12 | 10 |
| QuantumCircuit API | https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.QuantumCircuit | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | latest (2.x); parameters order, assign_parameters, find_bit | 11 | 10, 11 |
| StatevectorEstimator API | https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.primitives.StatevectorEstimator | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | latest (2.x); PUB broadcasting example | 12 | 10 |
| Cirq: Parameter sweeps | https://quantumai.google/cirq/simulate/params | docs | Apache-2.0 | Cirq docs 2026-10-28 | 12 | 10 |
| GenericBackendV2 API | https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.providers.fake_provider.GenericBackendV2 | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | latest (2.x); default basis id/rz/sx/x/cx | 12 | 11 |
| CouplingMap API | https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.transpiler.CouplingMap | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | latest (2.x); from_line/ring/heavy_hex | 12 | 11 |
| generate_preset_pass_manager API | https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.transpiler.generate_preset_pass_manager | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | latest (2.x); default level 2, seed_transpiler | 12 | 11 |
| Set transpiler optimization level (guide) | https://quantum.cloud.ibm.com/docs/en/guides/set-optimization | docs (guide) | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | qiskit ~=2.5.2 page | 11 | 11 |
| Cirq: Qubit routing | https://quantumai.google/cirq/transform/routing_transformer | docs (notebook) | Apache-2.0 | Cirq docs 2026-10-28; RouteCQC | 12 | 11 |

L200: **18** new sources (65 kept overall).

## Learning tools (UPDATE-TOOLS-REVIEW-SPEC, from kb/shared/LEARNING-TOOLS-CATALOG.md, checked 2026-10-28)

Facts were taken from the shared catalogue, which checked these official pages; they were not re-fetched for this topic. Scores use the same rubric. Used in the lessons' `learningTools` field and in `LEARNING-TOOLS.md`.

| title | url | type | licence | version-or-date checked | score/12 | used in lesson(s) |
|---|---|---|---|---|---|---|
| qiskit.visualization API | https://quantum.cloud.ibm.com/docs/en/api/qiskit/visualization | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | qiskit 2.6.1 | 11 | 2, 3, 4, 11 |
| qdk on PyPI | https://pypi.org/project/qdk/ | docs (package index) | MIT | 1.33.1 (2026-10-08) | 10 | 5, 6, 8 |
| microsoft/qdk (repo, VS Code extension source) | https://github.com/microsoft/qdk | repo | MIT | commit 4 days before check | 10 | 5, 6, 8 (also equivalents) |
| QDK VS Code extension (Marketplace) | https://marketplace.visualstudio.com/items?itemName=quantum.qsharp-lang-vscode | docs (extension index) | repo MIT (licence text not shown on the page) | 2026-10-28 | 8 | 5, 8 |
| openqasm3 on PyPI (reference parser) | https://pypi.org/project/openqasm3/ | docs (package index) | Apache-2.0 | 1.0.1 (2025-02-19); API not yet stable | 9 | 5 |
| jupyterlab on PyPI | https://pypi.org/project/jupyterlab/ | docs (package index) | BSD-3-Clause | 4.6.4 (2026-09-21) | 10 | 3 |
| JupyterLab Desktop releases | https://github.com/jupyterlab/jupyterlab-desktop/releases | repo | BSD-3-Clause | v4.6.3-1 (2026-08-26) | 9 | 3 (installer) |
| Quirk releases (dropped: unmaintained) | https://github.com/Strilanc/Quirk/releases | repo | Apache-2.0 | v2.3, 2019-09-11 | — | LEARNING-TOOLS "Not recommended" |
| IBM Quantum Composer guide (not catalogued: proprietary, OpenQASM 2.0 only) | https://quantum.cloud.ibm.com/docs/en/guides/composer | docs (vendor) | proprietary service | 2026-10-28 | — | LEARNING-TOOLS "Not recommended" |

Already listed above and reused: openqasm/openqasm repo, qiskit-qasm3-import on PyPI, Cirq import/export (interop), qiskit on PyPI.

## L300 ("Harden it", lessons 12–16; retrieved 2026-10-28)

Rubric detail and dropped sources: `../research/L300-evidence.md`.

| title | url | type | licence | version-or-date checked | score/12 | used in lesson(s) |
|---|---|---|---|---|---|---|
| Qiskit Aer tutorial: Building noise models | https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html | docs (tutorial) | Apache-2.0 | Aer 0.18.0 docs build | 12 | 12 |
| Qiskit Aer NoiseModel API | https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.noise.NoiseModel.html | docs | Apache-2.0 | Aer 0.18.0; add_all_qubit_readout_error, from_backend | 12 | 12 |
| Qiskit Aer amplitude_damping_error API | https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.noise.amplitude_damping_error.html | docs | Apache-2.0 | page shows Aer 0.17.1 | 11 | 12 |
| Qiskit Aer SamplerV2 API (re-checked) | https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.primitives.SamplerV2.html | docs | Apache-2.0 | Aer 0.18.2; seed, options.backend_options | 12 | 12 (already listed for 3) |
| cirq.depolarize API | https://quantumai.google/reference/python/cirq/depolarize | docs | Apache-2.0 | Cirq docs 2026-10-28; p/(4^n−1) per Pauli | 12 | 12, 13 |
| Error mitigation and suppression techniques (IBM guide) | https://quantum.cloud.ibm.com/docs/en/guides/error-mitigation-and-suppression-techniques | docs (guide) | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | 2026-10-28; TREX, ZNE gate folding, PEC | 12 | 13 |
| Mitiq: How do I use ZNE? | https://mitiq.readthedocs.io/en/stable/guide/zne-1-intro.html | docs (user guide) | GPL-3.0 | Mitiq 1.1.0 | 12 | 13 |
| Mitiq: ZNE options (folding, factories) | https://mitiq.readthedocs.io/en/stable/guide/zne-3-options.html | docs (user guide) | GPL-3.0 | Mitiq 1.1.0 | 12 | 13 |
| Mitiq: How do I use REM? | https://mitiq.readthedocs.io/en/stable/guide/rem-1-intro.html | docs (user guide) | GPL-3.0 | Mitiq 1.1.0 | 12 | 13 |
| mitiq on PyPI | https://pypi.org/project/mitiq/ | docs (package index) | GPL-3.0 | 1.1.0 (2026-09-03), Python >=3.11,<3.13 | 9 | 13 |
| mthree: converting to probabilities | https://qiskit.github.io/qiskit-addon-mthree/probs.html | docs | Apache-2.0 | mthree 3.0.0 docs | 11 | 13 (equivalent) |
| Quantum approximate optimization algorithm (IBM tutorial) | https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm | docs (tutorial) | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | qiskit ≥ 2.0 page, 2026-10-28 | 12 | 14, 15 |
| QAOAAnsatz API | https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.QAOAAnsatz | docs | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | latest (2.x) | 11 | 14 |
| scipy minimize(method='COBYLA') | https://docs.scipy.org/doc/scipy/reference/optimize.minimize-cobyla.html | docs | BSD-3-Clause | SciPy 1.18.0 manual | 12 | 14, 15 |
| scipy on PyPI | https://pypi.org/project/scipy/ | docs (package index) | BSD-3-Clause | 1.18.1 (2026-08-21), Python >= 3.12 | 9 | 14, 15 (pin) |
| Ground-state energy estimation of the Heisenberg chain with VQE (IBM tutorial) | https://quantum.cloud.ibm.com/docs/en/tutorials/spin-chain-vqe | docs (tutorial) | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | 2026-10-28; hand-written SPSA | 12 | 15 |
| SPSA algorithm (J. C. Spall, JHU APL) | https://www.jhuapl.edu/SPSA/ | docs (author page) | not stated (public page) | 2026-10-28 | 11 | 15 |
| Spall (1998), Implementation of the Simultaneous Perturbation Algorithm for Stochastic Optimization, IEEE TAES 34(3) (author's copy) | https://www.jhuapl.edu/SPSA/PDF-SPSA/Spall_Implementation_of_the_Simultaneous.PDF | paper (primary) | © 1998 IEEE (author's copy, read only) | step 1: α 0.602, γ 0.101; A ≈ 10% of iterations; c ≈ noise std — fetched 2026-10-28 | 13 | 15 (replaces the golang-spsa README, R3-13) |
| pennylane on PyPI | https://pypi.org/project/pennylane/ | docs (package index) | Apache-2.0 | 0.45.1 (2026-06-26), Python >= 3.11 | 9 | 16 |
| qp.AngleEmbedding (PennyLane docs) | https://docs.pennylane.ai/en/stable/code/api/pennylane.AngleEmbedding.html | docs | Apache-2.0 | PennyLane 0.45.1 | 12 | 16 |
| qp.BasicEntanglerLayers (PennyLane docs) | https://docs.pennylane.ai/en/stable/code/api/pennylane.BasicEntanglerLayers.html | docs | Apache-2.0 | PennyLane 0.45.1 | 12 | 16 |
| PennyLane demo: Barren plateaus in quantum neural networks | https://pennylane.ai/demos/tutorial_barren_plateaus | docs (demo) | not re-checked (PennyLane demos repo) | last updated 2026-05-27 | 11 | 16 |
| PennyLane demo: Variational classifier | https://pennylane.ai/demos/tutorial_variational_classifier | docs (demo) | not re-checked (PennyLane demos repo) | last updated 2026-04-17 | 11 | 16 |
| PennyLane blog: import pennylane as qp | https://pennylane.ai/blog/2026/03/import-pennylane-as-qp-growing-beyond-just-qml/ | blog (background) | not stated | 2026-03-19 | 9 | 16 |
| marimo on PyPI | https://pypi.org/project/marimo/ | docs (package index) | Apache-2.0 | 0.25.2 (2026-10-19); `marimo edit`, `marimo tutorial intro` | 10 | 14, 16 (learning tool) |

Also reused in L300 (already listed above): AerSimulator API (12), StatevectorEstimator API (15), StatevectorSampler API (15), Ollama OpenAI compatibility (15), and the learning-tool catalogue entries for Qiskit visualization (12, 14), JupyterLab (13, 15) and marimo (14, 16; row above).

L300: **23** new sources (one blog marked background; the background repo was replaced by Spall's paper in the 2026-10-28 update pass) + the marimo learning-tool page; the Aer SamplerV2 row is a re-check of an L100 source.

## L400 additions (lessons 17-21 + capstone 22; retrieved 2026-10-28)

| title | url | type | licence | version-or-date checked | score/12 | used in lesson(s) |
|---|---|---|---|---|---|---|
| Introduction to Quantum Compute execution modes (IBM) | https://quantum.cloud.ibm.com/docs/en/guides/execution-modes | docs (vendor guide; facts + equivalent) | code Apache-2.0 / content CC BY-SA 4.0 (Qiskit/documentation) | 2026-10-28; job / batch / session, TTLs | 11 | 17, 22 |
| qiskit.compiler.transpile API | https://quantum.cloud.ibm.com/docs/en/api/qiskit/compiler | docs | code Apache-2.0 / content CC BY-SA 4.0 | latest 2.x; optimization_level default 2 | 12 | 17, 20 |
| Qiskit preset pass managers (levels 0-3) | https://quantum.cloud.ibm.com/docs/en/api/qiskit/transpiler_preset | docs | code Apache-2.0 / content CC BY-SA 4.0 | latest 2.x | 12 | 20 |
| VF2PostLayout API | https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.transpiler.passes.VF2PostLayout | docs | code Apache-2.0 / content CC BY-SA 4.0 | latest 2.x | 12 | 20 |
| GenericBackendV2 API | https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.providers.fake_provider.GenericBackendV2 | docs | code Apache-2.0 / content CC BY-SA 4.0 | latest 2.x | 12 | 20 |
| Nishio et al. (2020), Extracting Success from IBM's 20-Qubit Machines Using Error-Aware Compilation | https://arxiv.org/abs/1903.10963 | paper | arXiv (author licence) | ACM JETC 16(3), 2020 | 10 | 20, 22 |
| Farhi, Goldstone, Gutmann (2014), A Quantum Approximate Optimization Algorithm | https://arxiv.org/abs/1411.4028 | paper | arXiv (author licence) | v1 2014 | 11 | 18, 22 |
| Abbas et al. (2024), Challenges and Opportunities in Quantum Optimization | https://arxiv.org/abs/2312.02279 | paper | arXiv (author licence) | Nat Rev Phys 2024, v3 | 11 | 18, 22 |
| Kirkpatrick, Gelatt, Vecchi (1983), Optimization by simulated annealing (PubMed record) | https://pubmed.ncbi.nlm.nih.gov/17813860/ | paper (record) | abstract only | Science 220(4598) | 9 | 18 |
| scipy.optimize.dual_annealing | https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.dual_annealing.html | docs | BSD-3-Clause | SciPy 1.18.0 manual | 10 | 18 (equivalent) |
| Fowler et al. (2012), Surface codes: Towards practical large-scale quantum computation | https://arxiv.org/abs/1208.0928 | paper | arXiv (author licence) | Phys. Rev. A 86, 032324 | 10 | 19, 22 |
| qdk.qre.models.qec.SurfaceCode | https://learn.microsoft.com/en-us/python/qdk/qdk.qre.models.qec.surfacecode?view=qsharp-py | docs | MIT (microsoft/qdk) | qdk.qre (2026) | 12 | 19 |
| How to install and use the Microsoft Quantum resource estimator | https://learn.microsoft.com/en-us/azure/quantum/install-run-resource-estimator | docs (vendor) | docs CC BY 4.0 / code MIT | updated 2026-07-31 | 11 | 19 |
| What is the Microsoft Quantum resource estimator? | https://learn.microsoft.com/en-us/azure/quantum/intro-to-resource-estimation | docs (vendor) | docs CC BY 4.0 | updated 2026-10-21 | 10 | 19 |
| qdk on PyPI | https://pypi.org/project/qdk/ | docs (package index) | MIT | 1.33.1 (2026-10-08), Python ≥ 3.10 | 9 | 19 (pin) |
| pandas on PyPI | https://pypi.org/project/pandas/ | docs (package index) | BSD-3-Clause | 3.1.0, Python ≥ 3.11 | 9 | 19 (pin, QDK venv) |
| Gidney & Ekerå (2021), How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits | https://arxiv.org/abs/1905.09749 | paper | arXiv (author licence) | Quantum 5, 433 (v3) | 12 | 19, 21 |
| Gidney (2025), How to factor 2048 bit RSA integers with less than a million noisy qubits | https://arxiv.org/abs/2505.15917 | paper | arXiv (author licence) | v1 2025-05-21 | 11 | 19, 21 |
| Ross & Selinger (2016), Optimal ancilla-free Clifford+T approximation of z-rotations | https://arxiv.org/abs/1403.2975 | paper | arXiv (author licence) | QIC 16 (v3) | 11 | 19 |
| Amy, Maslov, Mosca, Roetteler (2013), meet-in-the-middle synthesis (Toffoli T-depth 3) | https://arxiv.org/abs/1206.0758 | paper | arXiv (author licence) | IEEE TCAD 32(6) | 9 | 19 |
| Beverland et al. (2022), Assessing requirements to scale to practical quantum advantage | https://arxiv.org/abs/2211.07629 | paper | arXiv (author licence) | v1 2022 | 11 | 19 |
| NIST IR 8547 (final), Transition to Post-Quantum Cryptography Standards | https://nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8547.pdf | standard (NIST report) | US government work | October 2026 (final 2026-10-27) | 12 | 21 |
| FIPS 203, ML-KEM | https://csrc.nist.gov/pubs/fips/203/final | standard | US government work | 2024-08-13 | 11 | 21 |
| cryptography: ML-KEM key encapsulation | https://cryptography.io/en/latest/hazmat/primitives/asymmetric/mlkem/ | docs | Apache-2.0 / BSD | added 47.0.0; ran with 50.0.2 | 12 | 21 |
| NIST CSWP 39, Considerations for Achieving Cryptographic Agility | https://csrc.nist.gov/pubs/cswp/39/considerations-for-achieving-cryptographic-agility/final | standard (white paper) | US government work | 2025-12-19 (superseded by 39upd1) | 10 | 21 |
| Roetteler et al. (2017), Quantum resource estimates for computing elliptic curve discrete logarithms | https://arxiv.org/abs/1706.06752 | paper | arXiv (author licence) | ASIACRYPT 2017 (v3) | 10 | 21 |
| NIST news: Report provides guidelines for transition to PQC | https://www.nist.gov/news-events/news/2026/10/nist-report-provides-guidelines-transition-post-quantum-cryptography | news (background) | US government work | 2026-10-27 | 9 | 21 (background) |

Also reused in L400 (listed above): StatevectorSampler API (17), Spall 1998 (17), Mitiq REM guide (22), Ollama OpenAI compatibility (21, 22) and the catalogue entries for Qiskit visualization (20), Microsoft QDK (19), JupyterLab (17-19, 21, 22), marimo (17, 18, 22) and Mitiq (22).

L400: **27** new sources (1 news item marked background; vendor pages used for API facts or as equivalents only).

## L500 additions ("Theory & Rigour", lessons 23-27 + assessment pack; retrieved 2026-10-30)
Rubric detail, questions and dropped sources: `../research/L500-evidence.md`. Papers are summarised, never reproduced.

| title | url | type | licence | version-or-date checked | score/12 | used in lesson(s) |
|---|---|---|---|---|---|---|
| IBM Quantum Learning — Limitations on quantum information (global phase, no-cloning; J. Watrous) | https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/quantum-circuits/limitations-on-quantum-information | course | content CC BY-SA 4.0 (Qiskit/documentation) | 2026-10-30 | 12 | 23, 24 |
| IBM Quantum Learning — Entanglement in action (teleportation, superdense coding, CHSH) | https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/entanglement-in-action/introduction | course | content CC BY-SA 4.0 (Qiskit/documentation) | 2026-10-30 | 11 | 24 |
| IBM Quantum Learning — General formulation: Density matrices | https://quantum.cloud.ibm.com/learning/en/courses/general-formulation-of-quantum-information/density-matrices/introduction | course | content CC BY-SA 4.0 (Qiskit/documentation) | 2026-10-30 | 11 | 24 |
| IBM Quantum Learning — Grover's algorithm | https://quantum.cloud.ibm.com/learning/en/courses/fundamentals-of-quantum-algorithms/grover-algorithm/introduction | course | content CC BY-SA 4.0 (Qiskit/documentation) | 2026-10-30 | 11 | 25 |
| IBM Quantum Learning — Phase estimation and factoring | https://quantum.cloud.ibm.com/learning/en/courses/fundamentals-of-quantum-algorithms/phase-estimation-and-factoring/introduction | course | content CC BY-SA 4.0 (Qiskit/documentation) | 2026-10-30 | 10 | 25 |
| Cleve, Ekert, Macchiavello, Mosca (1998), Quantum algorithms revisited | https://arxiv.org/abs/quant-ph/9708016 | paper | arXiv (author licence) | Proc. R. Soc. A 454 (v1 1997) | 10 | 24, 25 |
| Grover (1996), A fast quantum mechanical algorithm for database search | https://arxiv.org/abs/quant-ph/9605043 | paper (primary reading) | arXiv distribution licence (no open content licence) | STOC '96; v3 1996-11-19 | 9 | 25, 27 |
| Boyer, Brassard, Høyer, Tapp (1998), Tight bounds on quantum searching | https://arxiv.org/abs/quant-ph/9605034 | paper | arXiv (author licence) | Fortschr. Phys. 46 (v1 1996) | 10 | 25, 27 |
| Bennett, Bernstein, Brassard, Vazirani (1997), Strengths and weaknesses of quantum computing | https://arxiv.org/abs/quant-ph/9701001 | paper | arXiv (author licence) | SIAM J. Comput. 26(5) | 9 | 25, 27 |
| Shor (1997), Polynomial-time algorithms for prime factorization and discrete logarithms | https://arxiv.org/abs/quant-ph/9508027 | paper | arXiv (author licence) | SIAM J. Comput. 26 (v2 1996) | 9 | 25 |
| Preskill (2018), Quantum Computing in the NISQ era and beyond | https://quantum-journal.org/papers/q-2018-08-06-79/ | paper (primary reading) | CC BY 4.0 (Quantum) | Quantum 2, 79; arXiv:1801.00862v3 | 11 | 25, 27 |
| Quantum (journal): Terms and Conditions announcement — CC BY 4.0 for published works | https://quantum-journal.org/terms-and-conditions-announcement/ | licence evidence | — | 2016 announcement, checked 2026-10-30 | 9 | 27 |
| Quantum (journal): Terms and Conditions / Code of Conduct | https://quantum-journal.org/about/terms-and-conditions/ | policy | — | 2026-10-30 | 10 | 26 |
| arXiv.org non-exclusive license to distribute | https://arxiv.org/licenses/nonexclusive-distrib/1.0/license.html | licence evidence | — | page 2007, licence 2004 | 9 | 27 |
| ACM Code of Ethics and Professional Conduct | https://www.acm.org/code-of-ethics | professional code | © ACM 2018 (republish unchanged with notice) | adopted 2018-06-22 | 11 | 26, 27, assessment |
| IEEE Code of Ethics (IEEE Policies 7.8) | https://www.ieee.org/about/corporate/governance/p7-8.html | professional code | © IEEE | revisions through June 2020 | 11 | 26 |
| NIST IR 8547 (final), CSRC landing page | https://csrc.nist.gov/pubs/ir/8547/final | standard (NIST report) | US government work | October 2026 | 12 | 26 (PDF listed under L400) |
| UK NCSC, Timelines for migration to post-quantum cryptography | https://www.ncsc.gov.uk/guidance/pqc-migration-timelines | regulator guidance | Crown copyright (reuse terms not checked) | published 2025-03-20 | 11 | 26 |
| US BIS interim final rule, 89 FR 72926 (quantum and other advanced-technology controls) | https://www.federalregister.gov/documents/2024/09/06/2024-19633/commerce-control-list-additions-and-revisions-implementation-of-controls-on-advanced-technologies | statute/regulation | US government work | effective 2024-09-06 | 10 | 26 |
| Commission Delegated Regulation (EU) 2025/2003 (list of dual-use items, amends Reg. 2021/821) | https://eur-lex.europa.eu/eli/reg_del/2025/2003/oj | regulation | © European Union (EUR-Lex reuse terms not checked) | OJ L 2025/2003, 14.11.2025 | 9 | 26 |
| UN GA resolution A/RES/78/287, International Year of Quantum Science and Technology 2025 | https://digitallibrary.un.org/record/4052700 | UN resolution | UN document | adopted 2024-06-07 | 9 | 26 |
| Google Research blog, Quantum Supremacy Using a Programmable Superconducting Processor | https://research.google/blog/quantum-supremacy-using-a-programmable-superconducting-processor/ | vendor blog (claim only) | © Google | 2019-10-23 | 8 | 26 |
| Arute et al. (2019), Supplementary information for "Quantum supremacy ..." (Nature 574, 505) | https://arxiv.org/abs/1910.11333 | paper (supporting) | arXiv | v2 2019-12-28 | 8 | 26 (supporting) |
| Pednault et al. (2019), Leveraging Secondary Storage to Simulate Deep 54-qubit Sycamore Circuits | https://arxiv.org/abs/1910.09534 | paper | arXiv (author licence) | v2 2019-10-22 | 9 | 26 |
| Pan, Chen, Zhang (2022), Solving the sampling problem of the Sycamore quantum circuits | https://arxiv.org/abs/2111.03011 | paper | arXiv (author licence) | PRL 129, 090502 (v2 2022) | 10 | 26 |
| ABET Criteria for Accrediting Computing Programs, 2025-2026 | https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-computing-programs-2025-2026/ | accreditation standard | © ABET | 2025-2026 cycle | 11 | syllabus |
| ABET Criteria for Accrediting Engineering Programs, 2025-2026 | https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-engineering-programs-2025-2026/ | accreditation standard | © ABET | 2025-2026 cycle | 11 | syllabus |
| ACM/IEEE-CS/AAAI CS2023 — Knowledge Areas | https://csed.acm.org/knowledge-areas/ | curriculum standard | © ACM/IEEE-CS/AAAI | CS2023 (Jan 2024) | 11 | syllabus |

Also reused in L500 (listed above): IBM Quantum Learning Single systems / Multiple systems / Deutsch-Jozsa, Bit-ordering in the Qiskit SDK, FIPS 203.

L500: **28** new sources (1 vendor blog and 1 supplementary-information preprint used for the claim only; 2 licence-evidence pages).
