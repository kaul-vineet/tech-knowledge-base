"""Build content/L300.json from the lesson metadata below + the lab files on disk.

Run from the domain folder:  python tools/build_l300_json.py
`code` is always read from the lab file, so it stays an exact copy. Solution paths and concept notes are checked.
L300 = "Harden it" (kb/L300-SPEC.md): every lesson has a failureLab and tradeOffs.
"""
import json
import os
import posixpath

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABS = "labs/L300"

ENV = ("Mac mini or Windows 11; Python 3.12 venv (lesson 1); numpy 2.5.3 for the main lab (numpy simulator in "
       "labs/_shared/qsim). SDK path: {sdk} (pending CI).")
PLATFORMS = {"mac": "expected", "windows": "expected"}
PLATFORM_NOTE = ("mac/windows 'expected': authored and run on Linux only; lab code uses pathlib, utf-8 file I/O, "
                 "sys.executable and 127.0.0.1; CI matrix runs the same tools/run_labs.py on macos-latest and windows-latest.")
RAN = "Ran locally (Python 3.12.15, numpy 2.5.3, no quantum SDKs installed in the authoring sandbox): "

S = {  # only URLs retrieved during research (see research/L300-evidence.md)
    "aer_noise": ("Qiskit Aer tutorial: Building noise models", "https://qiskit.github.io/qiskit-aer/tutorials/3_building_noise_models.html"),
    "aer_noisemodel": ("Qiskit Aer NoiseModel API", "https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.noise.NoiseModel.html"),
    "aer_damping": ("Qiskit Aer amplitude_damping_error API", "https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.noise.amplitude_damping_error.html"),
    "aer_sampler": ("Qiskit Aer SamplerV2 API", "https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.primitives.SamplerV2.html"),
    "aer_sim": ("AerSimulator API (density_matrix method)", "https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html"),
    "ibm_mitigation": ("Error mitigation and suppression techniques (IBM guide)", "https://quantum.cloud.ibm.com/docs/en/guides/error-mitigation-and-suppression-techniques"),
    "mitiq_zne": ("Mitiq 1.1.0: How do I use ZNE?", "https://mitiq.readthedocs.io/en/stable/guide/zne-1-intro.html"),
    "mitiq_zne_opts": ("Mitiq 1.1.0: ZNE options (folding, factories)", "https://mitiq.readthedocs.io/en/stable/guide/zne-3-options.html"),
    "mitiq_rem": ("Mitiq 1.1.0: How do I use REM?", "https://mitiq.readthedocs.io/en/stable/guide/rem-1-intro.html"),
    "mitiq_pypi": ("mitiq on PyPI (1.1.0)", "https://pypi.org/project/mitiq/"),
    "mthree_probs": ("mthree: converting quasi-probabilities to probabilities", "https://qiskit.github.io/qiskit-addon-mthree/probs.html"),
    "cirq_depol": ("cirq.depolarize API", "https://quantumai.google/reference/python/cirq/depolarize"),
    "qaoa_tut": ("Quantum approximate optimization algorithm (IBM tutorial)", "https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm"),
    "qaoa_ansatz": ("QAOAAnsatz API", "https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.QAOAAnsatz"),
    "cobyla": ("scipy.optimize.minimize(method='COBYLA')", "https://docs.scipy.org/doc/scipy/reference/optimize.minimize-cobyla.html"),
    "scipy_pypi": ("scipy on PyPI (1.18.1)", "https://pypi.org/project/scipy/"),
    "vqe_tut": ("Ground-state energy estimation of the Heisenberg chain with VQE (IBM tutorial, SPSA)", "https://quantum.cloud.ibm.com/docs/en/tutorials/spin-chain-vqe"),
    "spsa": ("SPSA algorithm (J. C. Spall, JHU APL)", "https://www.jhuapl.edu/SPSA/"),
    "spsa_gains": ("Spall (1998), Implementation of the Simultaneous Perturbation Algorithm for Stochastic Optimization, IEEE TAES 34(3): gains alpha 0.602, gamma 0.101 (author's copy)",
                   "https://www.jhuapl.edu/SPSA/PDF-SPSA/Spall_Implementation_of_the_Simultaneous.PDF"),
    "sv_estimator": ("StatevectorEstimator API", "https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.primitives.StatevectorEstimator"),
    "sv_sampler": ("StatevectorSampler API", "https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.primitives.StatevectorSampler"),
    "pl_pypi": ("pennylane on PyPI (0.45.1)", "https://pypi.org/project/pennylane/"),
    "pl_angle": ("qp.AngleEmbedding (PennyLane 0.45.1)", "https://docs.pennylane.ai/en/stable/code/api/pennylane.AngleEmbedding.html"),
    "pl_bel": ("qp.BasicEntanglerLayers (PennyLane 0.45.1)", "https://docs.pennylane.ai/en/stable/code/api/pennylane.BasicEntanglerLayers.html"),
    "pl_bp": ("PennyLane demo: Barren plateaus in quantum neural networks", "https://pennylane.ai/demos/tutorial_barren_plateaus"),
    "pl_vc": ("PennyLane demo: Variational classifier", "https://pennylane.ai/demos/tutorial_variational_classifier"),
    "pl_qp": ("PennyLane blog: import pennylane as qp (2026-03-19)", "https://pennylane.ai/blog/2026/03/import-pennylane-as-qp-growing-beyond-just-qml/"),
    "ollama_openai": ("Ollama: OpenAI compatibility (/v1/chat/completions)", "https://docs.ollama.com/api/openai-compatibility"),
}


def src(*keys):
    return [{"title": S[k][0], "url": S[k][1]} for k in keys]


def step(title, detail, expected, if_not, mac=None, windows=None):
    out = {"title": title, "detail": detail, "expected": expected, "ifNot": if_not}
    if mac:
        out["mac"], out["windows"] = mac, windows
    return out


def build_step(module, naive, expected, if_not):
    """The build-task check plus the failureLab proof: the naive lab module must FAIL the same test."""
    cmd = "python -m unittest test_build_task -v"
    return step("Build task: harden it, then prove it",
                f"Write {module}.py (see buildTask) and run the check; then run the same test against the naive lab module ({naive}), which must fail.",
                expected, if_not,
                f"BUILD_TASK_MODULE={module} {cmd}; BUILD_TASK_MODULE={naive} {cmd}",
                f'$env:BUILD_TASK_MODULE = "{module}"; {cmd}; $env:BUILD_TASK_MODULE = "{naive}"; {cmd}; Remove-Item Env:BUILD_TASK_MODULE')


EXTRAS_MAC = ("python3.12 -m venv .venv-extras && source .venv-extras/bin/activate && "
              "python -m pip install -r labs/L300/requirements-extras.txt")
EXTRAS_WIN = ("py -3.12 -m venv .venv-extras; .venv-extras\\Scripts\\Activate.ps1; "
              "python -m pip install -r labs\\L300\\requirements-extras.txt")
SDK_MAC = "python -m pip install -r labs/L300/requirements.txt"
SDK_WIN = "python -m pip install -r labs\\L300\\requirements.txt"

MANUAL = "Pending a manual run (tool not runnable in the authoring sandbox). "
QVIS = {"name": "Qiskit visualization (qiskit.visualization)", "role": "SEE", "mac": "pip install 'qiskit[visualization]'",
        "windows": "pip install \"qiskit[visualization]\"", "licence": "Apache-2.0 (OSI: yes)",
        "url": "https://quantum.cloud.ibm.com/docs/en/api/qiskit/visualization"}
JUPYTER = {"name": "JupyterLab (+ JupyterLab Desktop)", "role": "CHECK", "mac": "pip install jupyterlab, or Desktop arm64 installer",
           "windows": "pip install jupyterlab, or Desktop x64 installer / winget install jupyterlab", "licence": "BSD-3-Clause (OSI: yes)",
           "url": "https://pypi.org/project/jupyterlab/"}
MITIQ = {"name": "Mitiq", "role": "CHECK",
         "mac": "pip install mitiq (Python >=3.11,<3.13; Cirq is a core dependency; add mitiq[qiskit] for Qiskit circuits)",
         "windows": "pip install mitiq (same Python range; PyPI classifiers list macOS and Windows)", "licence": "GPL-3.0 (OSI: yes)",
         "url": "https://pypi.org/project/mitiq/"}
MARIMO = {"name": "marimo", "role": "SEE", "mac": "pip install marimo (marimo tutorial intro)", "windows": "pip install marimo (marimo tutorial intro)",
          "licence": "Apache-2.0 (OSI: yes)", "url": "https://pypi.org/project/marimo/"}


def tool(base, exercise, expected, role=None):
    return {"name": base["name"], "role": role or base["role"], "exercise": exercise, "expected": MANUAL + expected,
            "mac": base["mac"], "windows": base["windows"], "licence": base["licence"], "url": base["url"]}


LESSONS = [
    {
        "dir": "12-noise-models", "file": "noise_lab.py", "id": "noise-models", "number": 12,
        "title": "Noise models: how Bell and GHZ results degrade",
        "phase": "Noise", "category": "noise models",
        "description": "Attach depolarizing, amplitude-damping and readout noise to a Bell/GHZ circuit, measure fidelity vs noise level, and harden an exact-outcome test.",
        "outcome": "You can build a noise model, predict fidelity and success from it, read the JSON-lines sweep, and write a statistical check that passes correct noisy runs and still fails broken circuits.",
        "sdk": "qiskit 2.6.1 + qiskit-aer 0.18.2 (NoiseModel, Aer SamplerV2)",
        "estimatedTime": "45-60 minutes",
        "overview": ["Noise turns 'impossible' outcomes into rare ones; tests and dashboards must compare against what the noise model predicts, not against perfection."],
        "prerequisites": ["Lesson 4 (Bell pair)", "Lesson 3 (shots, binomial spread)", "Lesson 11 (devices have basis gates)"],
        "glossary": [
            {"term": "density matrix ρ", "meaning": "A weighted mix of possible states; diag(ρ) gives the outcome probabilities."},
            {"term": "depolarizing error p", "meaning": "ρ → (1 − p)ρ + p·I/2^k on the k qubits of a gate (Aer convention)."},
            {"term": "amplitude damping γ", "meaning": "Decay of |1⟩ toward |0⟩ (T1); asymmetric."},
            {"term": "readout error", "meaning": "Classical flips at measurement: P(read 1 | 0), P(read 0 | 1)."},
            {"term": "fidelity ⟨ψ|ρ|ψ⟩", "meaning": "Overlap of the noisy state with the ideal one (needs ρ, not counts)."},
        ],
        "concepts": ["Noise models attach channels to gate names and to measurement.", "Fidelity falls with noise level and circuit size.",
                     "Success = P(all 0) + P(all 1) is what counts can measure.", "Test against the model's prediction with a statistical margin."],
        "steps": [
            step("Run the lab", "python noise_lab.py", "ideal {'00': 998, '11': 1002}; noisy {'00': 962, '01': 82, '10': 70, '11': 886}.",
                 "ModuleNotFoundError qsim: run from the lab folder so labs/_shared is found."),
            step("Read the JSON lines", "One line per (n, p2): fidelity and success.", "Bell p2 0.02: fidelity 0.9719, success 0.925; GHZ-4 p2 0.1: fidelity 0.7473.",
                 "Different numbers: check NOISE in the lab file (p1 0.002, p2 0.02, damp 0.01, p01 0.02, p10 0.04)."),
            step("Find the asymmetry", "Compare p_all0 with p_all1 on any line.", "p_all0 > p_all1 (0.4818 vs 0.4433 for the Bell pair): damping and p10 > p01.",
                 "Equal values: damping and readout are switched off."),
            step("See the fault", "Read the last two lines.", "naive bell_check: True on ideal counts, False on noisy counts.",
                 "True on noisy counts means the sample had no 01/10: check shots = 2000 and seed 7."),
            step("Try it", "python try_it.py", "symmetric noise: p_all0 = p_all1 = 0.4454; readout-only 0.8145 vs CX-only 0.9037 success for GHZ-4.",
                 "Compare with the tryIt predictions."),
            build_step("my_check", "noise_lab", "OK: correct circuits pass for n = 2, 3 over 20 seeds; missing CX, missing H and a broken GHZ link fail. Naive module: FAIL test_correct_circuit_passes_on_noisy_device (n=2 seed=0). Solution: Ran 5 tests ... OK.",
                       "A missing H still passes: add the all-1 share check."),
            step("Run the tests (and the SDK path in CI)", "python -m unittest -v; SDK: install labs/L300/requirements.txt, then python noise_aer.py",
                 "OK (15 tests, 3 SDK tests skipped without qiskit-aer). Aer success within ±0.02 of numpy (CI).",
                 "Aer import errors: qiskit-aer 0.18.2 needs Python ≥ 3.11.", SDK_MAC + " && python labs/L300/12-noise-models/noise_aer.py",
                 SDK_WIN + "; python labs\\L300\\12-noise-models\\noise_aer.py"),
        ],
        "codeWalkthrough": [
            {"title": "NOISE = {\"p1\": 0.002, \"p2\": 0.02, \"damp\": 0.01, \"p01\": 0.02, \"p10\": 0.04}", "detail": "The seeded 'device'. Every number is explicit, so a test can recompute what the device should give."},
            {"title": "noisy_steps(ops, noise)", "detail": "Inserts a depolarizing channel after every gate (p1 or p2 by gate size) and amplitude damping on its qubits: what Aer's add_all_qubit_quantum_error does per gate name."},
            {"title": "dm.run(n, steps)", "detail": "Density-matrix simulation: unitaries as UρU†, channels as Σ KρK† (labs/_shared/qsim/density.py, self-tested)."},
            {"title": "dm.readout_matrix(p01, p10, n) @ dm.probabilities(rho)", "detail": "Readout is classical: a Kronecker product of per-qubit assignment matrices applied to diag(ρ)."},
            {"title": "metrics(n, noise)", "detail": "Fidelity from ρ and success from measured probabilities, emitted as JSON lines so they can be grepped and diffed."},
            {"title": "bell_check(counts, ...)", "detail": "The naive L100 assertion (only all-0/all-1 allowed). Correct for an ideal simulator, wrong for any noisy one: the failure this lab hardens."},
        ],
        "failureLab": {"fault": "The seeded NOISE model (p1 0.002, p2 0.02, damping 0.01, readout 0.02/0.04) on a correct Bell pair; counts from seed 7, 2000 shots.",
                       "symptom": "bell_check returns False: counts {'00': 962, '01': 82, '10': 70, '11': 886} contain 01 and 10, so a correct circuit is reported broken.",
                       "fix": "bell_check compares the observed success with the model's prediction minus 4 binomial standard errors, and checks that the all-1 share matches the model.",
                       "proof": "BUILD_TASK_MODULE=noise_lab python -m unittest test_build_task -> FAIL test_correct_circuit_passes_on_noisy_device; default (solution_tolerant_check) -> Ran 5 tests OK, incl. missing-CX/missing-H/broken-GHZ cases still failing."},
        "tradeOffs": [
            {"option": "Exact-outcome assertion", "gains": "Trivial, catches every deviation on an ideal simulator", "costs": "Fails every correct run on hardware or with noise", "chooseWhen": "Noise-free simulator unit tests only"},
            {"option": "Fixed threshold (e.g. success ≥ 0.8)", "gains": "Simple, tolerant", "costs": "No statistical basis; passes a missing H (success near 1)", "chooseWhen": "Quick smoke tests where a false pass is cheap"},
            {"option": "Model-based check (prediction − Z·σ, plus balance)", "gains": "Known false-alarm rate; still catches structural bugs", "costs": "Needs a current noise model and shot count", "chooseWhen": "Regression tests and monitoring on noisy backends"},
        ],
        "buildTask": {"task": "Rewrite bell_check(counts, n, shots, noise) so a correct circuit passes on the noisy model for 20 seeds while a missing CX, a missing H and a broken GHZ link still fail.",
                      "hints": ["Expected success and the all-1 share come from noise_lab.metrics(n, noise).", "Binomial standard error: sqrt(s(1 − s)/shots).",
                                "A missing H gives almost only 00, so success alone is not enough."],
                      "solution": "labs/L300/12-noise-models/solution_tolerant_check.py",
                      "check": "python -m unittest test_build_task -v (5 tests; numpy, runs locally)"},
        "expectedResults": ["Bell fidelity 0.9719, success 0.925 at the default model", "GHZ-4 fidelity 0.7473 at p2 = 0.1",
                            "Naive check False on noisy counts; hardened check True for 200/200 seeds of GHZ-3"],
        "testCases": [{"action": "metrics(n, noise) for n = 2..4 and p2 = 0..0.1", "expected": "fidelity strictly decreasing in p2 and n"},
                      {"action": "bell_check on counts from [h(0)] only (missing CX)", "expected": "False (solution)"},
                      {"action": "noise_aer.aer_success(n, NOISE) vs metrics(n, NOISE)['success'] (CI)", "expected": "within 0.02"}],
        "tryIt": [
            {"task": "Set damp = 0 and p01 = p10 = 0.03 for GHZ-3 (try_it.symmetric_noise).", "predict": "Does P(000) still beat P(111)?",
             "expected": "No: p_all0 = p_all1 = 0.4454. The imbalance came from damping and asymmetric readout.", "validatedBy": "local: try_it.py (observed); Aer variant pending-ci"},
            {"task": "GHZ-4 with only 5% readout flips vs only p2 = 0.05 on each CX.", "predict": "Which costs more success?",
             "expected": "Readout: 0.8145 (= 0.95⁴) vs CX noise: 0.9037. For shallow circuits readout dominates.", "validatedBy": "local: try_it.py (observed); Aer variant pending-ci"},
        ],
        "troubleshooting": [{"symptom": "Fidelity < 1 with p2 = 0", "action": "Expected: p1 and damping are still on. Zero every key for an ideal run (IDEAL)."},
                            {"symptom": "Aer success differs from numpy by > 0.02", "action": "Check compose order (depolarizing then damping) and the ReadoutError rows (true 0, true 1)."}],
        "equivalents": ["Qiskit Aer: NoiseModel + depolarizing_error / amplitude_damping_error / ReadoutError, run with AerSimulator(method='density_matrix') or Aer SamplerV2 (noise_aer.py).",
                        "Cirq: circuit.with_noise(cirq.depolarize(p)) on cirq.DensityMatrixSimulator (cirq's p is the total Pauli probability: p_cirq = p·(4^k − 1)/4^k).",
                        "Device-derived models: NoiseModel.from_backend(backend) builds depolarizing + thermal relaxation + readout from calibration data."],
        "inRealSystems": ["Hardware teams publish per-qubit T1/T2, gate and readout errors daily; noise models built from them go stale quickly.",
                          "CI for quantum code runs ideal unit tests plus noisy regression tests with statistical tolerances."],
        "useWhen": "Use a noise model to set expectations and test tolerances before running on hardware; avoid treating it as the device itself.",
        "simulatorVsReal": "numpy density-matrix simulator (labs/_shared/qsim/density.py), exact and seeded. The noise model is illustrative, not a calibrated device: real devices add crosstalk, leakage and drift that these channels omit.",
        "checkYourself": [{"q": "Why is success lower than fidelity for the same run?", "a": "Readout flips act after the state is prepared: they lower measured success but not ⟨ψ|ρ|ψ⟩."},
                          {"q": "Which bug passes a 'success ≥ 0.8' check?", "a": "A missing H: almost only 00, so success looks excellent; check the 0/1 balance too."},
                          {"q": "What sets the tolerance in the hardened check?", "a": "Shot count and the model's success: Z·sqrt(s(1 − s)/shots), Z = 4."}],
        "checkpoint": "PASS if you can read fidelity and success from the JSON lines, the naive check fails on noisy counts, and your check passes test_build_task.",
        "learningTools": [
            tool(QVIS, "plot_histogram([ideal, noisy], legend=['ideal', 'noise model']) with the two counts dicts from noise_lab.py; then plot_state_city(DensityMatrix(rho)) for rho from measured_probabilities(2, NOISE).",
                 "The ideal bars show only 00/11 (998/1002); the noisy bars add 01: 82 and 10: 70. In the city plot the |00⟩⟨11| bar drops from 0.5 to 0.4817 and small 01/10 diagonal bars (0.0098) appear."),
        ],
        "seeAlso": ["simulation L200 #10 Warm-up, replications and confidence: the same standard-error reasoning sets this lesson's test tolerance."],
        "sources": src("aer_noise", "aer_noisemodel", "aer_damping", "aer_sampler", "aer_sim", "cirq_depol"),
        "next": "L300 #13 Error mitigation: readout correction and zero-noise extrapolation: remove part of the bias this noise model creates.",
        "how": RAN + "`python noise_lab.py`, `python try_it.py`, `python solution_tolerant_check.py` (outputs in README); `python -m unittest` -> 15 tests: 12 OK, 3 Aer tests skipped; fail-before proof with BUILD_TASK_MODULE=noise_lab observed.",
        "pendingCi": ["noise_aer.py (Qiskit Aer NoiseModel + SamplerV2)", "test_noise.py AerAgrees (2 tests)", "test_try_it.py TryItSdk (Aer variant)"],
        "projectFiles": [("noise_lab.py", "main lab: noise model, density-matrix runs, JSON-lines sweep, naive check"),
                         ("solution_tolerant_check.py", "buildTask reference: model-based statistical check"), ("test_build_task.py", "buildTask + failureLab proof"),
                         ("noise_aer.py", "SDK path: same model in Qiskit Aer"), ("test_noise.py", "unittest: numpy always, Aer in CI"),
                         ("README.md", "run commands and observed output"), ("../../_shared/qsim/density.py", "shared density-matrix simulator (self-tested)")],
        "summary": "A noise model attaches error channels to gates and measurement; the state becomes a density matrix. Fidelity and measurable success fall with noise and size, so tests must compare against the model's prediction with a statistical margin.",
    },
    {
        "dir": "13-error-mitigation", "file": "mitigation_lab.py", "id": "error-mitigation", "number": 13,
        "title": "Error mitigation: readout correction and zero-noise extrapolation",
        "phase": "Noise", "category": "error mitigation",
        "description": "Invert a measured readout calibration matrix, extrapolate gate-folded circuits to zero noise, and fix the negative probabilities that too few shots produce.",
        "outcome": "You can calibrate and invert readout errors, run ZNE with folding and Richardson/linear fits, and return valid probability distributions under small shot budgets.",
        "sdk": "mitiq 1.1.0 + its Cirq (zne.execute_with_zne, fold_gates_at_random, RichardsonFactory, rem)",
        "estimatedTime": "45-60 minutes",
        "overview": ["Mitigation removes bias from noisy estimates at the price of variance and extra runs; with too few shots the plain readout inverse returns negative 'probabilities'."],
        "prerequisites": ["Lesson 12 (noise models)", "Lesson 10 (fitting)"],
        "glossary": [
            {"term": "calibration (assignment) matrix M", "meaning": "Column j = observed distribution when basis state j was prepared."},
            {"term": "quasi-probability", "meaning": "Sums to 1 but may have negative entries (the plain inverse M⁻¹·p)."},
            {"term": "unitary folding", "meaning": "G → G·G†·G: same logic, about 3× the noise (scale factor 3)."},
            {"term": "Richardson extrapolation", "meaning": "Exact polynomial through all (scale, value) points, evaluated at scale 0."},
            {"term": "TVD", "meaning": "Total variation distance, ½·Σ|p − q|: how far a distribution is from the ideal one."},
        ],
        "concepts": ["Readout mitigation = invert a measured assignment matrix.", "ZNE = amplify noise on purpose, then extrapolate to zero.",
                     "Mitigation trades bias for variance.", "Constrain the inverse to the probability simplex."],
        "steps": [
            step("Run the lab", "python mitigation_lab.py", "First JSON line (4000 shots): mitigated [0.5038, 0.0003, -0.0105, 0.5064], tvd 0.082 → 0.0105.",
                 "ModuleNotFoundError qsim: run from the lab folder."),
            step("See the fault", "Read the second JSON line (100 calibration / 200 run shots).", "mitigated P(01) = -0.0241 and 'downstream sampling failed: Probabilities are not non-negative'.",
                 "No failure: the seeds or shot counts were changed."),
            step("Read the ZNE lines", "One line per scale factor (CX folded 1×, 3×, 5×).", "P000 0.9039, 0.7474, 0.6234 with 4, 12, 20 CX.",
                 "Values rise with scale: folding is not applied to the CX gates."),
            step("Compare extrapolations", "Read the last line.", "raw 0.9039 | linear 0.9687 | Richardson 0.9944 (ideal 1.0).",
                 "Richardson > 1.0: noise does not grow smoothly with scale; prefer the linear fit."),
            step("Try it", "python try_it.py", "ZNE std 0.017 vs raw 0.0069 at 2000 shots; clip TVD 0.0436 vs constrained 0.0426.", "Compare with the tryIt predictions."),
            build_step("my_mitigation", "mitigation_lab", "OK: always a valid distribution at both budgets; mean TVD ≤ plain inverse; at 4000 shots better than raw. Naive module (plain inverse): FAIL test_always_a_probability_distribution (-0.0082 at 100/200 shots). Solution: Ran 3 tests ... OK.",
                       "Negative entries remain: project onto the simplex after every gradient step, not only at the end."),
            step("Run the tests (and the Mitiq path in CI)", "python -m unittest -v; Mitiq path in a separate venv: python mitiq_zne.py",
                 "OK (12 tests, 1 Mitiq test skipped). Mitiq Richardson ≈ 0.9944 (CI).", "Mitiq pins its own Cirq: keep it out of the lesson 1 venv.",
                 EXTRAS_MAC + " && python labs/L300/13-error-mitigation/mitiq_zne.py", EXTRAS_WIN + "; python labs\\L300\\13-error-mitigation\\mitiq_zne.py"),
        ],
        "codeWalkthrough": [
            {"title": "calibrate(shots, rng)", "detail": "Prepares each basis state and measures it through the (unknown) readout flips; the columns form the estimated M, shot noise included."},
            {"title": "mitigate(p_noisy, m_est): np.linalg.solve", "detail": "Plain inverse. Unbiased on average, but its output is a quasi-probability that goes negative where the truth is 0."},
            {"title": "rng.choice(4, p=quasi)", "detail": "The realistic downstream consumer: sampling (or entropy, log-likelihood) needs real probabilities and raises on negatives."},
            {"title": "mirror_ops(): GHZ then its inverse", "detail": "Ideal output |000⟩ with P = 1, so any deficit is noise; the same trick as Mitiq's randomized-benchmarking example."},
            {"title": "folded(ops, scale)", "detail": "Local unitary folding of every CX: scale 3 → CX·CX·CX. Logically identical, three times the CX noise."},
            {"title": "exact_value / noisy_value", "detail": "Cached exact density-matrix value per scale; shots add binomial noise on top (tryIt 1)."},
            {"title": "richardson(scales, values) / linear(...)", "detail": "Lagrange polynomial at 0 vs least-squares line intercept: lower bias vs lower variance."},
        ],
        "failureLab": {"fault": "Too few shots: 100 calibration shots per basis state and 200 run shots (numpy seed 11) for a Bell pair with readout flips 0.03/0.06.",
                       "symptom": "Mitigated distribution [0.5072, -0.0241, -0.0126, 0.5294]; rng.choice raises 'Probabilities are not non-negative'.",
                       "fix": "mitigate() solves min ‖M·p − p_noisy‖² subject to p ≥ 0, Σp = 1 (projected gradient on the simplex), and calibration and runs use ≥ 4000 shots each.",
                       "proof": "BUILD_TASK_MODULE=mitigation_lab python -m unittest test_build_task -> FAIL test_always_a_probability_distribution; default (solution_constrained) -> Ran 3 tests OK."},
        "tradeOffs": [
            {"option": "Plain inverse M⁻¹", "gains": "Unbiased on average; one line of code", "costs": "Negative quasi-probabilities; amplifies noise in M", "chooseWhen": "You only need expectation values from large shot counts"},
            {"option": "Constrained least squares (simplex)", "gains": "Always a valid distribution; lower mean TVD (0.0426 vs 0.055 at small budgets)", "costs": "Iterative; slightly biased toward the boundary", "chooseWhen": "Results feed sampling, reports or anything that expects probabilities"},
            {"option": "ZNE (Richardson vs linear)", "gains": "Removes most gate-noise bias (0.9039 → 0.9944)", "costs": "3× runs; variance 2.5× larger (std 0.017 vs 0.0069)", "chooseWhen": "Expectation values with enough shots; prefer linear when noise is not smooth in scale"},
        ],
        "buildTask": {"task": "Rewrite mitigate(p_noisy, m_est) so it always returns a probability distribution and is never worse (mean TVD) than the plain inverse.",
                      "hints": ["Start from the plain inverse, projected onto the simplex.", "Gradient of ‖M·p − p_noisy‖² is 2·Mᵀ(M·p − p_noisy); step 1/‖M‖².",
                                "Sort-based simplex projection: subtract a threshold, clip at 0."],
                      "solution": "labs/L300/13-error-mitigation/solution_constrained.py",
                      "check": "python -m unittest test_build_task -v (3 tests; numpy, runs locally)"},
        "expectedResults": ["Readout: TVD 0.082 → 0.0105 at 4000 shots (plain inverse, still slightly negative)", "ZNE: 0.9039 raw → 0.9687 linear → 0.9944 Richardson",
                            "Constrained mitigation valid for 100 seeds at both budgets"],
        "testCases": [{"action": "mitigate(M @ p_true, M) with the exact M", "expected": "returns p_true"},
                      {"action": "richardson([1,3,5], quadratic values)", "expected": "exact intercept 0.9"},
                      {"action": "mitiq_zne.mitiq_zne(RichardsonFactory([1,3,5])) vs numpy Richardson (CI)", "expected": "equal to 3 decimals"}],
        "tryIt": [
            {"task": "Estimate P(000) from 2000 shots per scale over 200 seeds (try_it.zne_shot_noise).", "predict": "Does ZNE make the estimate more or less precise?",
             "expected": "Less precise, more accurate: raw mean 0.9041 std 0.0069; Richardson mean 0.9942 std 0.017.", "validatedBy": "local: try_it.py (observed)"},
            {"task": "Clip negatives to 0 and renormalise instead of constrained least squares.", "predict": "Is clipping good enough?",
             "expected": "Close: mean TVD 0.0436 vs 0.0426 (100/200 shots, 200 seeds); clipping is not the closest valid distribution.", "validatedBy": "local: try_it.py (observed)"},
        ],
        "troubleshooting": [{"symptom": "Mitigated values sum to 1 but some are negative", "action": "Expected from the plain inverse; use the constrained version before sampling or reporting."},
                            {"symptom": "ZNE result above the ideal value", "action": "Richardson over-fits noise; switch to linear or add shots per scale."}],
        "equivalents": ["Mitiq: zne.execute_with_zne(circuit, executor, factory=RichardsonFactory([1, 3, 5]), scale_noise=fold_gates_at_random); rem.execute_with_rem with generate_inverse_confusion_matrix (mitiq_zne.py).",
                        "mthree (Qiskit addon): M3Mitigation.apply_correction returns quasi-probabilities; nearest_probability_distribution() is the L2-closest valid one.",
                        "IBM Quantum Estimator resilience options (TREX readout twirling, ZNE with gate folding or PEA): vendor service, one line here."],
        "inRealSystems": ["Readout calibration runs are repeated often because assignment errors drift.",
                          "ZNE is a default option in hardware estimator services; its cost is reported as extra circuit executions per noise factor."],
        "useWhen": "Use readout mitigation whenever measurement error is significant, and ZNE for expectation values with shots to spare; avoid both when the shot budget is tiny.",
        "simulatorVsReal": "numpy density-matrix simulator with depolarizing gate noise and classical readout flips. On hardware, folding may not scale noise linearly (coherent and idle errors), so extrapolations can overshoot.",
        "checkYourself": [{"q": "Why can M⁻¹·p be negative?", "a": "Shot noise in p and M; where the true probability is 0 the inverse has nothing to hold it at 0."},
                          {"q": "What does scale factor 3 mean for a CX?", "a": "CX → CX·CX·CX: the same logical gate with about three times the noise."},
                          {"q": "Why did ZNE's std grow from 0.0069 to 0.017?", "a": "Extrapolation weights (+15/8, −10/8, +3/8 for 1, 3, 5) amplify each point's shot noise."}],
        "checkpoint": "PASS if you can explain each JSON line, the plain inverse goes negative with few shots, and your constrained mitigation passes test_build_task.",
        "learningTools": [
            tool(JUPYTER, "In a notebook import mitigation_lab, plot P000 against scale (1, 3, 5), then draw the least-squares line and the quadratic through the three points down to scale 0.",
                 "Points 0.9039 / 0.7474 / 0.6234; the line hits 0.9687 at 0 and the quadratic 0.9944 (the lab's printed values); ideal 1.0."),
            tool(MITIQ, "In the extras venv run python mitiq_zne.py, then call mitiq_zne.mitiq_zne(zne.inference.LinearFactory(scale_factors=[1, 3, 5])) and "
                        "RichardsonFactory(scale_factors=[1, 3, 5]) yourself and compare each zero-noise value with mitigation_lab.linear() / richardson() on [0.9039, 0.7474, 0.6234].",
                 "Not observed yet (mitiq_zne.py is pending CI). The lab README expects raw P(000) 0.9039, linear ≈ 0.9687 and Richardson ≈ 0.9944 "
                 "(agreement to ~1e-4: Cirq's simulator is float32); a larger gap points at the depolarizing conversion to_cirq_p or at folding non-CX gates."),
        ],
        "seeAlso": ["simulation L100 #6 Is the model right? Verification vs validation: a mitigation result is only as good as the calibration model behind it.",
                    "simulation L300 #13 Calibration: fit to data, validate on data you did not fit: the readout matrix is a fitted model too, and Richardson's exact fit through 3 points vs the linear fit is the same more-parameters bias/variance choice."],
        "sources": src("ibm_mitigation", "mitiq_zne", "mitiq_zne_opts", "mitiq_rem", "mitiq_pypi", "mthree_probs", "cirq_depol"),
        "next": "L300 #14 QAOA on MaxCut vs the classical optimum: a full variational algorithm where every evaluation would need this mitigation on hardware.",
        "how": RAN + "`python mitigation_lab.py`, `python try_it.py`, `python solution_constrained.py` (outputs in README); `python -m unittest` -> 12 tests: 11 OK, 1 Mitiq test skipped; fail-before proof with BUILD_TASK_MODULE=mitigation_lab observed.",
        "pendingCi": ["mitiq_zne.py (Mitiq 1.1.0 + Cirq DensityMatrixSimulator)", "test_mitigation.py MitiqAgrees", "mitiq 1.1.0 resolving next to its own Cirq version (CI job l300-extras)"],
        "projectFiles": [("mitigation_lab.py", "main lab: calibration, plain inverse, folding, Richardson/linear ZNE"),
                         ("solution_constrained.py", "buildTask reference: constrained least squares on the simplex"), ("test_build_task.py", "buildTask + failureLab proof"),
                         ("mitiq_zne.py", "SDK path: Mitiq ZNE and REM"), ("test_mitigation.py", "unittest: numpy always, Mitiq in CI"), ("README.md", "run commands and observed output")],
        "summary": "Readout mitigation inverts a measured assignment matrix; ZNE folds gates to amplify noise and extrapolates back to zero. Both trade bias for variance, and the plain inverse returns negative quasi-probabilities unless you constrain it and spend enough shots.",
    },
    {
        "dir": "14-qaoa-maxcut", "file": "qaoa_lab.py", "id": "qaoa-maxcut", "number": 14,
        "title": "QAOA on MaxCut vs the classical optimum",
        "phase": "Variational algorithms", "category": "optimisation",
        "description": "Run QAOA (p = 1, 2) on a 5-node graph, map the p = 1 landscape, grade results by approximation ratio against brute force, and escape a local minimum.",
        "outcome": "You can build the QAOA cost and mixer layers, grade QAOA against a brute-force optimum, and make the optimiser robust with warm starts and restarts.",
        "sdk": "qiskit 2.6.1 StatevectorEstimator + scipy 1.18.1 COBYLA",
        "estimatedTime": "45-60 minutes",
        "overview": ["QAOA's circuit is short; the risk sits in the classical optimiser, which happily stops in a local minimum unless you compare against references."],
        "prerequisites": ["Lesson 10 (parameterized circuits and sweeps)", "Lesson 12 (noise models)", "Lesson 13 (error mitigation)"],
        "glossary": [
            {"term": "MaxCut", "meaning": "Split the nodes in two sets so the most edges cross between them."},
            {"term": "cost layer e^{−iγC}", "meaning": "Phase proportional to each bitstring's cut size; RZZ(−γ) per edge up to a global phase."},
            {"term": "mixer layer", "meaning": "RX(2β) on every qubit: moves amplitude between bitstrings."},
            {"term": "approximation ratio", "meaning": "⟨C⟩ / brute-force maximum cut."},
        ],
        "concepts": ["Brute force grades every small instance.", "p = 1 landscape on a grid finds the right basin.",
                     "Local optimisers stop in the nearest minimum.", "Warm starts and restarts make the result reproducible."],
        "steps": [
            step("Run the lab", "python qaoa_lab.py", "brute force: max cut 5 by ['01001', '01011', '10100', '10110'].", "ModuleNotFoundError qsim: run from the lab folder."),
            step("Read the p = 1 landscape", "Second and third lines.", "grid γ = 0.6283, β = 0.3927, ratio 0.8188; grid + descent 0.822.",
                 "Ratio below 0.8: the grid ranges were changed."),
            step("See the fault", "Fourth line: p = 2 from random seed 0.", "ratio 0.7002, params [2.067, 0.909, -0.493, 0.029]: worse than p = 1.",
                 "Higher ratio: check seed 0 and lr = 0.05 in optimize()."),
            step("Read the samples", "Last line.", "most likely bitstring 01101 (cut 4), P(any optimal cut) = 0.1137 at the stuck parameters.",
                 "Compare with tryIt 2 at the good parameters (0.707)."),
            step("Try it", "python try_it.py", "2 of 8 random starts reach 0.9247; 20 shots at the optimum contain 13 optimal cuts.", "Compare with the tryIt predictions."),
            build_step("my_restarts", "qaoa_lab", "OK: p = 1 ≥ 0.82, p = 2 ≥ 0.92, p = 2 ≥ p = 1. Naive module (one random start): FAIL p1 (0.6997) and p2 (0.7002). Solution: Ran 3 tests ... OK.",
                       "p = 2 stuck: start from [γ/2, γ, β, β/2] of the p = 1 optimum."),
            step("Run the tests (and the Qiskit + COBYLA path in CI)", "python -m unittest -v; SDK: python qaoa_qiskit.py",
                 "OK (12 tests, 2 SDK tests skipped). Qiskit ⟨C⟩ = numpy; COBYLA from the warm start ≥ 0.92 (CI).",
                 "scipy missing: install labs/L300/requirements.txt.", SDK_MAC + " && python labs/L300/14-qaoa-maxcut/qaoa_qiskit.py",
                 SDK_WIN + "; python labs\\L300\\14-qaoa-maxcut\\qaoa_qiskit.py"),
        ],
        "codeWalkthrough": [
            {"title": "CUT = sum(((Z >> i) & 1) != ((Z >> j) & 1) ...)", "detail": "Cut size of all 32 bitstrings at once: the cost function and the brute-force reference in one array."},
            {"title": "psi * np.exp(-1j * gamma * CUT)", "detail": "The cost layer is diagonal, so on a simulator it is a phase per basis state; in a circuit it is one RZZ(−γ) per edge."},
            {"title": "sv.apply(psi, (sv.rx(2 * beta), q, ()))", "detail": "Mixer: RX(2β) on every qubit, reusing the shared numpy simulator."},
            {"title": "cost(params) = -<C>", "detail": "Optimisers minimise, so the expected cut is negated; ratio() divides by the brute-force maximum."},
            {"title": "landscape(): 41 × 21 grid", "detail": "Cheap at p = 1 and shows the basin structure; also the warm start for p = 2."},
            {"title": "optimize(x0): central-difference descent", "detail": "Exact gradients on a statevector, lr 0.05: it converges to the nearest minimum, which is the point of the fault."},
            {"title": "solve(p, seed): one random start", "detail": "The naive strategy the build task replaces."},
        ],
        "failureLab": {"fault": "p = 2 started from one random point (numpy seed 0, angles uniform in [0, π)).",
                       "symptom": "Descent converges to ratio 0.7002, below the p = 1 grid (0.8188); 100 more steps do not move it; P(optimal cut) only 0.1137.",
                       "fix": "solve() uses the p = 1 grid optimum interpolated to [γ/2, γ, β, β/2] plus 3 seeded random restarts and keeps the best (0.9247).",
                       "proof": "BUILD_TASK_MODULE=qaoa_lab python -m unittest test_build_task -> FAIL (0.6997 / 0.7002); default (solution_restarts) -> Ran 3 tests OK."},
        "tradeOffs": [
            {"option": "One random start", "gains": "Fewest evaluations", "costs": "6 of 8 starts end below 0.92; result depends on the seed", "chooseWhen": "Never alone; only inside a restart loop"},
            {"option": "Grid / interpolated warm start", "gains": "Lands in the right basin for p = 1 → p = 2", "costs": "Grid cost grows exponentially with p", "chooseWhen": "Small p, structured problems"},
            {"option": "Seeded restarts (keep best)", "gains": "Robust and reproducible", "costs": "k× the evaluations (and shots on hardware)", "chooseWhen": "Any non-convex landscape; log every start's ratio"},
        ],
        "buildTask": {"task": "Rewrite solve(p, seed) so p = 1 reaches ≥ 0.82 and p = 2 ≥ 0.92 for seed 0, and p = 2 is never worse than p = 1.",
                      "hints": ["Start p = 1 from the grid optimum (landscape()).", "Warm-start p = 2 with [γ/2, γ, β, β/2] from the optimised p = 1 answer.",
                                "Add a few seeded random restarts and keep the lowest cost."],
                      "solution": "labs/L300/14-qaoa-maxcut/solution_restarts.py",
                      "check": "python -m unittest test_build_task -v (3 tests; numpy, runs locally)"},
        "expectedResults": ["Brute-force max cut 5 (4 optimal strings)", "p = 1 ratio 0.822; p = 2 ratio 0.9247 with warm start + restarts", "Seed-0 single start stuck at 0.7002"],
        "testCases": [{"action": "cost([0, 0])", "expected": "-3.0 (each of 6 edges cut with probability 1/2)"},
                      {"action": "optimize(solve(2, seed=0), steps=100)", "expected": "still 0.7002: a local minimum, not slow convergence"},
                      {"action": "qaoa_qiskit.expected_cut(x) vs -cost(x) (CI)", "expected": "equal to 6 decimals"}],
        "tryIt": [
            {"task": "Run 8 random starts for p = 2 without a warm start (try_it.random_starts).", "predict": "How many reach ratio ≥ 0.92?",
             "expected": "2 of 8: [0.7002, 0.8352, 0.9247, 0.9247, 0.7009, 0.8329, 0.7002, 0.8329].", "validatedBy": "local: try_it.py (observed)"},
            {"task": "Sample 20 shots from the p = 2 optimum [0.585, 1.029, 0.517, 0.309].", "predict": "Ratio 0.92 is an average; is the best sample optimal?",
             "expected": "Yes: P(optimal) = 0.707, 13 of 20 samples cut 5 edges.", "validatedBy": "local: try_it.py (observed)"},
        ],
        "troubleshooting": [{"symptom": "Ratio drops after descent from the grid point", "action": "Learning rate too large (0.1 jumped basins in testing); use 0.05."},
                            {"symptom": "p = 2 worse than p = 1", "action": "Optimiser failure, not physics: warm-start from p = 1 and add restarts."}],
        "equivalents": ["Qiskit: QAOAAnsatz(cost_operator, reps=p) + StatevectorEstimator + scipy minimize(method='COBYLA') as in IBM's QAOA tutorial (qaoa_qiskit.py builds the same circuit with rzz/rx).",
                        "PennyLane: qp.qaoa module (cost/mixer layers) with any PennyLane optimiser; not verified for this lab."],
        "inRealSystems": ["QAOA studies always report a classical baseline and the approximation ratio, often with many restarts or transferred parameters.",
                          "On hardware every landscape point costs shots and queue time, so warm starts matter more than on a simulator."],
        "useWhen": "Use QAOA to prototype quantum heuristics on problems you can still grade classically; avoid claiming an advantage without a strong classical baseline.",
        "simulatorVsReal": "Exact numpy statevector (no shots, no noise): every difference comes from the optimiser. On hardware, add shot noise (lesson 15) and gate noise (lessons 12-13).",
        "checkYourself": [{"q": "Why is ratio 0.7002 at p = 2 a bug and not a limit?", "a": "Setting the second layer's angles to 0 reproduces p = 1 (≥ 0.822), so a better point exists."},
                          {"q": "What does ⟨C⟩ = 4.62 mean for the answer you return?", "a": "It is an average; return the best sampled bitstring (P(optimal) = 0.707)."},
                          {"q": "Why brute force here?", "a": "32 bitstrings: it gives the exact optimum to grade QAOA against."}],
        "checkpoint": "PASS if you can grade QAOA against brute force, reproduce the seed-0 local minimum, and your solve() passes test_build_task.",
        "learningTools": [
            tool(MARIMO, "Create qaoa_landscape.py with `marimo edit`: two sliders for γ ∈ [0, π] and β ∈ [0, π/2], one cell that imports qaoa_lab and shows ratio([γ, β]).",
                 "Moving the sliders updates the ratio reactively; the peak sits near γ = 0.63, β = 0.39 with ratio ≈ 0.82, matching the lab's grid line (0.8188)."),
            tool(QVIS, "Build the p = 2 circuit with qaoa_qiskit.circuit([0.585, 1.029, 0.517, 0.309]), add measure_all(), sample 1000 shots with StatevectorSampler and call plot_histogram.",
                 "The four optimal cuts (01001, 01011, 10100, 10110) carry about 0.707 of the shots together, as computed by try_it.py."),
        ],
        "seeAlso": ["simulation L200 #11 A supply-chain model: (s, S) inventory with common random numbers: another optimise-a-simulated-objective loop where the search strategy decides the answer."],
        "sources": src("qaoa_tut", "qaoa_ansatz", "cobyla", "scipy_pypi", "sv_estimator"),
        "next": "L300 #15 A hybrid variational loop (VQE) under shot noise: the general version of this optimiser loop, when every evaluation is noisy.",
        "how": RAN + "`python qaoa_lab.py`, `python try_it.py`, `python solution_restarts.py` (outputs in README); `python -m unittest` -> 12 tests: 10 OK, 2 Qiskit/scipy tests skipped; fail-before proof with BUILD_TASK_MODULE=qaoa_lab observed.",
        "pendingCi": ["qaoa_qiskit.py (rzz/rx circuit, StatevectorEstimator, scipy COBYLA)", "test_qaoa.py QiskitAgrees (2 tests)"],
        "projectFiles": [("qaoa_lab.py", "main lab: cut table, QAOA state, landscape, local descent, naive solve"),
                         ("solution_restarts.py", "buildTask reference: warm start + seeded restarts"), ("test_build_task.py", "buildTask + failureLab proof"),
                         ("qaoa_qiskit.py", "SDK path: Qiskit circuit + COBYLA"), ("test_qaoa.py", "unittest: numpy always, Qiskit in CI"), ("README.md", "run commands and observed output")],
        "summary": "QAOA alternates a diagonal cost phase and an RX mixer; a classical optimiser tunes the angles. Grade it against brute force by approximation ratio, and expect local minima: warm starts and seeded restarts make the result reliable.",
    },
    {
        "dir": "15-hybrid-vqe-loop", "file": "vqe_lab.py", "id": "hybrid-vqe-loop", "number": 15,
        "title": "A hybrid variational loop (VQE) under shot noise",
        "phase": "Variational algorithms", "category": "hybrid loop",
        "description": "Minimise a 2-qubit Pauli-sum energy with a shot-based estimator, log every iteration as JSON lines, and replace an optimizer that shot noise breaks.",
        "outcome": "You can build a grouped shot estimator, read convergence logs to diagnose a run, choose between finite differences, SPSA and COBYLA, and keep an agent's proposals under code control.",
        "sdk": "qiskit 2.6.1 StatevectorEstimator/StatevectorSampler + scipy 1.18.1 COBYLA",
        "estimatedTime": "60 minutes",
        "overview": ["The optimiser only sees noisy estimates; anything that divides that noise by a small step turns it into fake gradients, and the JSON-lines log is how you find out."],
        "prerequisites": ["Lesson 10 (expectation values, fitting)", "Lesson 14 (optimiser loop)", "Lesson 5 or 8 (agent assist pattern)"],
        "glossary": [
            {"term": "Pauli sum", "meaning": "H = Σ cᵢ·Pᵢ with Pᵢ ∈ {I, X, Y, Z}^⊗n; ⟨H⟩ = Σ cᵢ⟨Pᵢ⟩."},
            {"term": "measurement grouping", "meaning": "Commuting terms share one circuit: Z basis for II/ZI/IZ/ZZ, X basis for XX."},
            {"term": "SPSA", "meaning": "Simultaneous perturbation stochastic approximation: two evaluations per step for any number of parameters."},
            {"term": "JSON lines", "meaning": "One JSON object per line; easy to append, grep and load."},
        ],
        "concepts": ["Variational principle: E(θ) ≥ E0; the exact E0 is the referee.", "Shot noise ε ~ 1/√shots; finite differences amplify it by 1/h.",
                     "SPSA divides noise by 2c_k (~0.2), not by h.", "Logs are the evidence for diagnosis, by people, code or an agent."],
        "steps": [
            step("Run the lab", "python vqe_lab.py", "E0 = -1.8405; exact run error 0.0 (tail_grad_norm_median 0.007).", "ModuleNotFoundError qsim: run from the lab folder."),
            step("See the fault", "Second JSON line (1000 shots).", "error 1.5645, final_energy_est -0.27276, tail_energy_std 0.3912, tail_grad_norm_median 15.5125.",
                 "Small error: check h = 1e-3 and shots = 1000 in vqe()."),
            step("Read the log", "Open logs/vqe_gd_1000.jsonl (one line per iteration).", "grad_norm 9.907, 26.537, 8.852 in the first lines; still 9-34 at the end.",
                 "No logs folder: the lab writes it next to vqe_lab.py; check permissions."),
            step("Try it", "python try_it.py", "1e6 shots per term fix finite differences (error 0.0076) at 1.8e9 shots; SPSA needs 9e5. 8 of 150 SPSA estimates lie below E0.",
                 "Compare with the tryIt predictions."),
            build_step("my_spsa", "vqe_lab", "OK: error < 0.03 for seeds 0-3 at 1000 shots, and without noise. Naive module (finite differences): FAIL test_converges_under_shot_noise (1.5645). Solution: Ran 2 tests ... OK.",
                       "Diverging: lower a or raise A; c too small re-creates the finite-difference problem."),
            step("Agent assist", "python agent_assist.py --fake   (or without --fake for your local Ollama model)",
                 "diagnose ACCEPT (code ran SPSA: 0.0064); report REJECT (best_energy not in the log, wrong diagnosis); costly REJECT (1.8e9 shots > budget).",
                 "'No local model reachable': start Ollama or add --fake."),
            step("Run the tests (and the Qiskit path in CI)", "python -m unittest -v; SDK: python vqe_qiskit.py",
                 "OK (17 tests, 3 SDK tests skipped). COBYLA and SPSA at 4000 shots: error < 0.05 (CI).", "scipy missing: install labs/L300/requirements.txt.",
                 SDK_MAC + " && python labs/L300/15-hybrid-vqe-loop/vqe_qiskit.py", SDK_WIN + "; python labs\\L300\\15-hybrid-vqe-loop\\vqe_qiskit.py"),
        ],
        "codeWalkthrough": [
            {"title": "TERMS = {\"II\": -1.05, \"ZI\": 0.39, \"IZ\": -0.39, \"ZZ\": -0.01, \"XX\": 0.18}", "detail": "Toy H2-like Pauli sum in Qiskit label order; H is built with np.kron and E0 from eigvalsh, used only to grade."},
            {"title": "ansatz(t): RY, RY, CX, RY, RY", "detail": "Four parameters, real amplitudes; enough to reach this ground state exactly (exact-run error 0.0)."},
            {"title": "energy(t, shots, rng)", "detail": "Two measured groups: Z basis gives II/ZI/IZ/ZZ from one histogram, H⊗H then Z basis gives XX. Shot noise enters through rng.multinomial."},
            {"title": "gradient_descent(..., h=1e-3)", "detail": "Central differences: accurate on a statevector, but the gradient error is ~ε/h under shots: the fault."},
            {"title": "log({...}) → logs/vqe_gd_<shots>.jsonl", "detail": "One line per iteration: energy estimate, gradient norm, cumulative evaluations (observability)."},
            {"title": "summarize(log_path)", "detail": "Tail statistics (energy std, median gradient norm) that code, and the agent check, use to diagnose a run."},
        ],
        "failureLab": {"fault": "Shot noise: 1000 shots per measurement group (numpy seed 0) fed to finite-difference gradient descent with h = 1e-3, lr 0.4.",
                       "symptom": "Error 1.5645 vs 0.0 on the exact simulator; log tail: energy std 0.3912, median gradient norm 15.5 (exact run: 0.007).",
                       "fix": "vqe() uses SPSA (a 1.0, c 0.2, A 10, α 0.602, γ 0.101, 150 iterations): error 0.0064 with 900,000 shots in total.",
                       "proof": "BUILD_TASK_MODULE=vqe_lab python -m unittest test_build_task -> FAIL test_converges_under_shot_noise (1.5645); default (solution_spsa) -> Ran 2 tests OK."},
        "tradeOffs": [
            {"option": "Finite-difference gradient descent", "gains": "Simple; exact on a statevector", "costs": "2p evaluations per step; noise/h explodes under shots", "chooseWhen": "Exact simulators only"},
            {"option": "SPSA", "gains": "2 evaluations per step for any p; designed for noisy measurements", "costs": "Gain schedule (a, c, A) needs tuning; noisy path", "chooseWhen": "Shot-based or hardware runs with many parameters"},
            {"option": "COBYLA (scipy)", "gains": "Derivative-free trust region; robust to moderate noise", "costs": "Can stall when noise exceeds the improvement per step", "chooseWhen": "Few parameters and moderate shot counts (IBM's QAOA tutorial uses it)"},
        ],
        "buildTask": {"task": "Rewrite vqe(shots, seed, log_path) with SPSA so the error is < 0.03 for seeds 0-3 at 1000 shots, and log one JSON line per iteration.",
                      "hints": ["Δ ∈ {−1, +1}^p; gradient ≈ (f(x + c_kΔ) − f(x − c_kΔ)) / (2c_k) · Δ.",
                                "a_k = a/(A + k + 1)^α, c_k = c/(k + 1)^γ; Spall's α = 0.602, γ = 0.101.", "Grade with energy(x) − E0 after the run, never with the noisy minimum."],
                      "solution": "labs/L300/15-hybrid-vqe-loop/solution_spsa.py",
                      "check": "python -m unittest test_build_task -v (2 tests; numpy, runs locally)"},
        "expectedResults": ["E0 = -1.8405; exact finite differences error 0.0", "1000 shots: finite differences 1.5645, SPSA 0.0064",
                            "Agent assist: 1 ACCEPT after code ran the proposal, 2 REJECT"],
        "testCases": [{"action": "mean of 400 energy(t, 1000, rng) estimates", "expected": "within 0.005 of the exact energy (unbiased estimator)"},
                      {"action": "summarize(test_gd.jsonl in a per-run temporary folder)['tail_grad_norm_median']", "expected": "> 5 under shot noise"},
                      {"action": "vqe_qiskit.exact_energy(t) vs energy(t) (CI)", "expected": "equal to 6 decimals"}],
        "tryIt": [
            {"task": "Keep finite differences but raise shots per group to 1e5 and 1e6 (try_it.more_shots_same_optimizer).", "predict": "Does 'just add shots' fix it?",
             "expected": "1e5: still 0.9195; 1e6: 0.0076 but 1.8e9 shots in total, 2000× SPSA's 900,000.", "validatedBy": "local: try_it.py (observed)"},
            {"task": "Count SPSA log lines whose energy_est is below the exact E0.", "predict": "Can a variational estimate go below the ground energy?",
             "expected": "Yes, by noise: 8 of 150 lines; best_energy_est -1.84964 < E0 -1.8405. Never report the noisy minimum.", "validatedBy": "local: try_it.py (observed)"},
        ],
        "agentAssist": {
            "task": "A local model reads the convergence log summary (plus the last 5 lines), diagnoses the run and proposes optimizer settings; code checks the claims and runs the proposal itself.",
            "prompt": "System: You review convergence logs of variational quantum optimizers. Reply with one fenced code block holding {\"diagnosis\": \"converged\" | \"shot_noise\" | \"learning_rate_too_high\" | \"not_converged\", \"best_energy\": number taken from the log, \"proposal\": {\"optimizer\": \"gd\" | \"spsa\", \"shots\": int, ...settings}}. User: [[VQE-LOG]] Diagnose this run and propose new optimizer settings.\\nSummary: {...}\\nLast rows: ...",
            "check": "Code decides: best_energy must equal the log minimum (±1e-3); diagnosis must match code_diagnosis(summary); settings must be in RANGES and within a 2,000,000-shot budget; then code runs the proposal (seed 0) and accepts only if error < 0.03.",
            "expected": "diagnose ACCEPT  code ran spsa @ 1000 shots: error 0.0064\nreport   REJECT  best_energy -1.8405 is not in the log (log min -1.77348); diagnosis 'learning_rate_too_high' != code rule 'shot_noise'; code ran gd @ 1000 shots: error 0.7429\ncostly   REJECT  proposal needs 1,800,000,000 shots > budget 2,000,000 (not run)",
            "realModelNote": "Not run with a real model here. Small local models tend to quote the exact ground energy or a 'best' value that is not in the log and to suggest 'more shots'; the same checks reject those.",
            "validatedBy": "local: agent_assist.py --fake and test_agent_assist.py against the vendored fake server (observed)"},
        "caution": "Agent assist: the model only proposes; code checks every number and runs the settings itself, within a fixed shot budget, and never executes model text. Never put secrets or tokens in a prompt.",
        "troubleshooting": [{"symptom": "Energy estimate jumps around while gradient norms stay > 5", "action": "Shot noise dominates: SPSA, larger perturbations, or more shots (check the cost)."},
                            {"symptom": "Reported energy below E0", "action": "You reported a noisy minimum; re-estimate the final parameters with many shots."}],
        "equivalents": ["Qiskit: SparsePauliOp + StatevectorEstimator for exact ⟨H⟩, StatevectorSampler for shot estimates, scipy COBYLA or the IBM tutorial's hand-written SPSA (vqe_qiskit.py).",
                        "PennyLane: qp.expval of a Hamiltonian with shots on default.qubit and qp.SPSAOptimizer; not verified for this lab.",
                        "Cirq / OpenFermion: Pauli-sum Hamiltonians for chemistry; the loop is the same."],
        "inRealSystems": ["Production VQE logs every evaluation (parameters, energy, shots, job id) so runs can be audited and resumed.",
                          "Shot budgets are explicit because hardware time is billed; optimizer choice is driven by evaluations × shots."],
        "useWhen": "Use SPSA (or COBYLA for few parameters) whenever energies come from shots; avoid finite differences with small steps outside exact simulators.",
        "simulatorVsReal": "numpy statevector with multinomial shot sampling (seeded); no gate noise. On hardware add lessons 12-13: noise biases the energy upward and mitigation adds variance.",
        "checkYourself": [{"q": "Why does h = 1e-3 fail at 1000 shots?", "a": "Energy noise ε ≈ 0.01 divided by 2h = 0.002 gives gradient errors of ~5, larger than the true gradient."},
                          {"q": "How many energy evaluations does one SPSA step need for 4 parameters? For 400?", "a": "Two in both cases."},
                          {"q": "What makes the agent's 'best_energy' claim checkable?", "a": "The JSON-lines log: code recomputes the minimum and compares."}],
        "checkpoint": "PASS if you can diagnose the failing run from its log, your SPSA passes test_build_task, and the agent check rejects the hallucinated number.",
        "learningTools": [
            tool(JUPYTER, "In a notebook load logs/vqe_gd_1000.jsonl and logs/vqe_spsa_1000.jsonl with json.loads per line; plot energy_est against evals for both, with a horizontal line at E0 = -1.8405.",
                 "The finite-difference curve scatters (tail std 0.3912) and ends near -0.27; the SPSA curve settles near E0 (tail std 0.0065) with a few points below it, as in the lab summaries."),
        ],
        "seeAlso": ["distributed-systems L100 #4 Retries with exponential backoff, jitter and a retry budget: the agent check's shot budget is the same idea as a retry budget.",
                    "ai-agents L200 #11 Guardrails basics: code caps what an agent's proposal may cost before anything runs.",
                    "simulation L300 #12 Variance reduction: same precision, fewer runs: compare methods at equal cost; here SPSA beats 'just add shots' (finite differences at 1e6 shots) with 2000x fewer shots."],
        "sources": src("vqe_tut", "spsa", "spsa_gains", "cobyla", "sv_estimator", "sv_sampler", "qaoa_tut", "ollama_openai"),
        "next": "L300 #16 A quantum classifier vs a classical baseline: the same loop with a data-dependent cost, and what happens when the circuit grows.",
        "how": RAN + "`python vqe_lab.py`, `python try_it.py`, `python solution_spsa.py`, `python agent_assist.py --fake` (outputs in README); `python -m unittest` -> 17 tests: 14 OK, 3 Qiskit/scipy tests skipped; fail-before proof with BUILD_TASK_MODULE=vqe_lab observed.",
        "pendingCi": ["vqe_qiskit.py (StatevectorEstimator/Sampler, scipy COBYLA, SPSA)", "test_vqe.py QiskitAgrees (3 tests)", "agent_assist.py with a real local model"],
        "projectFiles": [("vqe_lab.py", "main lab: Pauli sum, grouped shot estimator, finite-difference loop, JSON-lines log, summarize"),
                         ("solution_spsa.py", "buildTask reference: SPSA with logging"), ("test_build_task.py", "buildTask + failureLab proof"),
                         ("agent_assist.py", "agent assist: model reads the log and proposes, code checks and runs"),
                         ("fake_vqe_rule.py", "deterministic fake-model route ([[VQE-LOG]])"), ("test_agent_assist.py", "agent-assist tests (fake server only)"),
                         ("vqe_qiskit.py", "SDK path: Qiskit primitives + COBYLA"), ("test_vqe.py", "unittest: numpy always, Qiskit in CI"), ("README.md", "run commands and observed output")],
        "summary": "VQE is a classical optimiser driving a noisy quantum estimator. Group commuting Pauli terms, log every iteration, and pick an optimizer that tolerates shot noise: finite differences with a small step fail, SPSA converges with a thousandth of the shots.",
    },
    {
        "dir": "16-quantum-classifier", "file": "classifier_lab.py", "id": "quantum-classifier", "number": 16,
        "title": "A quantum classifier vs a classical baseline",
        "phase": "Variational algorithms", "category": "quantum machine learning",
        "description": "Train a 2-qubit variational classifier (angle encoding, RY + CNOT layers) on a tiny dataset, compare it honestly with logistic regression, and fix flat gradients at scale.",
        "outcome": "You can train and evaluate a variational classifier with a held-out test set and a classical baseline, measure gradient magnitudes before training, and initialise deep circuits so they stay trainable.",
        "sdk": "pennylane 0.45.1 (qp.AngleEmbedding, qp.BasicEntanglerLayers, default.qubit)",
        "estimatedTime": "45-60 minutes",
        "overview": ["On this data the quantum model ties with three-parameter logistic regression; scaled up with random angles its gradients vanish below shot noise."],
        "prerequisites": ["Lesson 15 (hybrid loop)", "Lesson 10 (expectation values)", "Basic train/test evaluation"],
        "glossary": [
            {"term": "angle encoding", "meaning": "Each feature becomes a rotation angle (RY(x))."},
            {"term": "parameter-shift rule", "meaning": "Exact gradient of a rotation: (f(w + π/2) − f(w − π/2))/2."},
            {"term": "barren plateau", "meaning": "Gradients that shrink (exponentially) with qubits and depth under random initialisation."},
            {"term": "held-out test set", "meaning": "Data never used in training; the only fair accuracy."},
        ],
        "concepts": ["Always compare with a classical baseline on held-out data.", "Parameter shift gives exact gradients at 2 evaluations per weight.",
                     "Random init + width/depth → flat gradients.", "Near-identity init and a local readout keep gradients alive."],
        "steps": [
            step("Run the lab", "python classifier_lab.py", "quantum 2q × 2 layers: train 0.975, test 0.9; logistic regression: train 0.975, test 0.85.",
                 "ModuleNotFoundError circuit_model: run from the lab folder."),
            step("Read the training log", "logs/train_2q_2l.jsonl (one line per epoch).", "epoch 0: loss 2.0398, acc 0.425; epoch 59: loss 0.2661, acc 0.975, grad_norm 0.0116.",
                 "Loss not falling: check lr = 0.2 and the bias update."),
            step("Compare honestly", "Read the 5-seed line.", "[(1.0, 1.0), (0.95, 0.95), (0.95, 0.95), (0.9, 0.85), (0.85, 0.8)]: equal 3×, quantum +1 test point 2×.",
                 "One seed only: you are reading noise; 1 test point = 0.05."),
            step("See the fault", "Read the gradient-scan lines.", "median |grad| 0.7171 (2×2), 0.1121 (6×12), 0.0208 (10×20) vs shot floor 0.0224; 55% of inits below it.",
                 "Large gradients at 10×20: init_weights was changed."),
            step("Try it", "python try_it.py", "global readout stays flat (0.0303) even with the good init; 100 shots per prediction: test 0.9 → 0.85.", "Compare with the tryIt predictions."),
            build_step("my_init", "classifier_lab", "OK: 10 × 20 median |grad| > 10× the shot floor; the 2-qubit model still reaches train ≥ 0.9, test ≥ 0.85. Naive module (uniform init): FAIL test_wide_deep_model_has_usable_gradients (0.0163). Solution: Ran 2 tests ... OK.",
                       "Still flat: is the readout local (<Z0>)? Is sigma small (0.05)?"),
            step("Run the tests (and the PennyLane path in CI)", "python -m unittest -v; PennyLane path in a separate venv: python classifier_pennylane.py",
                 "OK (10 tests, 2 PennyLane tests skipped). PennyLane outputs = numpy to 1e-6 (CI).", "PennyLane docs now use `import pennylane as qp`; older examples use qml.",
                 EXTRAS_MAC + " && python labs/L300/16-quantum-classifier/classifier_pennylane.py", EXTRAS_WIN + "; python labs\\L300\\16-quantum-classifier\\classifier_pennylane.py"),
        ],
        "codeWalkthrough": [
            {"title": "make_dataset(seed=3): two blobs, 40 train / 20 test", "detail": "Features are already radian-scaled for angle encoding; the split happens before any training."},
            {"title": "logistic_baseline(...)", "detail": "Standardised features, 500 gradient steps, 3 parameters: the bar the quantum model must clear."},
            {"title": "cm.outputs(w, x): RY(x) encoding, [RY(w) + CNOT chain] × L, <Z0>", "detail": "Batched numpy simulation of all data points (circuit_model.py); same circuit as qp.AngleEmbedding + qp.BasicEntanglerLayers for 2 wires."},
            {"title": "cm.gradient(w, x): parameter shift", "detail": "Two evaluations per weight; exact, so any training trouble is the model's, not the estimator's."},
            {"title": "train_quantum(..., log_path)", "detail": "Full-batch MSE descent with a classical bias; one JSON line per epoch (loss, train_acc, grad_norm)."},
            {"title": "init_weights: uniform [0, 2π)", "detail": "The textbook default; harmless at 2 qubits, the cause of flat gradients at 10 × 20."},
            {"title": "gradient_scan(n, layers)", "detail": "Median |∂<Z0>/∂w| over random inits vs the 1000-shot noise floor: measure trainability before you train."},
        ],
        "failureLab": {"fault": "Scale the classifier to 10 qubits × 20 layers with angles uniform in [0, 2π) (numpy seeds 0-19).",
                       "symptom": "Median |∂<Z0>/∂w| = 0.0208, below the 1000-shot gradient noise floor 0.0224 for 55% of inits (2 × 2: 0.7171): with shots, training is a random walk.",
                       "fix": "init_weights() draws angles from N(0, 0.05²) (near-identity layers) and the readout stays local (<Z0>): median 0.863 at 10 × 20.",
                       "proof": "BUILD_TASK_MODULE=classifier_lab python -m unittest test_build_task -> FAIL test_wide_deep_model_has_usable_gradients (0.0163); default (solution_init) -> Ran 2 tests OK."},
        "tradeOffs": [
            {"option": "Logistic regression (classical)", "gains": "Milliseconds, 3 parameters, test 0.85 here", "costs": "Linear boundary only", "chooseWhen": "Always as the baseline; usually the answer for tabular data"},
            {"option": "Shallow quantum model, random init", "gains": "Trainable at 2 qubits; test 0.9 here (+1 point)", "costs": "21,600 circuit evaluations to train; shot noise costs accuracy (0.85 at 100 shots)", "chooseWhen": "Learning and benchmarking, not production"},
            {"option": "Wide/deep quantum model, near-identity init", "gains": "Gradients survive (median 0.863 at 10 × 20)", "costs": "Starts close to a shallow circuit; capacity must be earned by training", "chooseWhen": "You need depth; measure gradients first and keep a local readout"},
        ],
        "buildTask": {"task": "Write init_weights(layers, n, rng) so a 10-qubit, 20-layer model has median |∂<Z0>/∂w| > 10× the shot floor, while the 2-qubit model still trains (train ≥ 0.9, test ≥ 0.85).",
                      "hints": ["Small angles make each layer close to the identity.", "rng.normal(0, 0.05, (layers, n)) is enough here.",
                                "Keep readout='local'; tryIt 1 shows the global parity stays flat."],
                      "solution": "labs/L300/16-quantum-classifier/solution_init.py",
                      "check": "python -m unittest test_build_task -v (2 tests; numpy, runs locally)"},
        "expectedResults": ["Quantum test 0.9 vs logistic 0.85 on seed 3; a tie (±1 point) over 5 seeds", "Random init: median |grad| 0.7171 → 0.1121 → 0.0208",
                            "Near-identity init: 0.844 / 0.8312 / 0.863"],
        "testCases": [{"action": "cm.gradient vs finite differences", "expected": "equal to 1e-6 (parameter shift is exact)"},
                      {"action": "train/test split", "expected": "40/20, no shared points"},
                      {"action": "classifier_pennylane.output / gradient vs numpy (CI)", "expected": "equal to 1e-6"}],
        "tryIt": [
            {"task": "Keep the near-identity init but read out the global parity <Z0 Z1 … Z9> (try_it.global_readout_with_good_init).", "predict": "Does the good init rescue a global readout?",
             "expected": "No: median |grad| 0.0303 global vs 0.8742 local (10 inits).", "validatedBy": "local: try_it.py (observed)"},
            {"task": "Classify the 20 test points from 100 shots each instead of the exact <Z0>.", "predict": "How much accuracy does shot noise cost?",
             "expected": "Test accuracy 0.9 → 0.85 (one point flips near the boundary).", "validatedBy": "local: try_it.py (observed)"},
        ],
        "troubleshooting": [{"symptom": "Accuracy differs by 0.05 between runs", "action": "That is one test point; compare over several dataset seeds."},
                            {"symptom": "Loss flat from epoch 0", "action": "Run gradient_scan first; use near-identity init, fewer layers and a local readout."}],
        "equivalents": ["PennyLane: qp.AngleEmbedding(x, wires, rotation='Y') + qp.BasicEntanglerLayers(w, wires, rotation=qp.RY) + qp.expval(qp.Z(0)), trained with qp.GradientDescentOptimizer (classifier_pennylane.py).",
                        "Qiskit: a parameterized circuit (RY encoding + layers) with StatevectorEstimator and the parameter-shift rule; qiskit-machine-learning wraps this (not verified here).",
                        "Classical: scikit-learn LogisticRegression gives the same baseline in one call (not used, to keep numpy-only)."],
        "inRealSystems": ["Published quantum-ML results are credible only with classical baselines, held-out data and several seeds.",
                          "Teams measure gradient variance (trainability) before training large circuits, and use structured or layerwise initialisation."],
        "useWhen": "Use variational classifiers to learn the hybrid workflow and to benchmark; avoid them for production tabular data where classical models are cheaper and at least as accurate.",
        "simulatorVsReal": "Exact batched numpy statevector; no shots during training, no gate noise. On hardware every gradient entry would carry shot noise (tryIt 2) and gate noise (lesson 12).",
        "checkYourself": [{"q": "Why is 0.9 vs 0.85 not a quantum advantage?", "a": "It is one of 20 test points; over 5 seeds the models tie or differ by one point."},
                          {"q": "What does median |grad| 0.0208 mean with 1000 shots?", "a": "It is below the 0.0224 noise floor: the optimiser cannot tell the gradient's sign."},
                          {"q": "Why does near-identity init help?", "a": "Each layer starts ~identity, so the first steps see a shallow circuit with large gradients."}],
        "checkpoint": "PASS if you report test accuracy against the baseline over several seeds, reproduce the flat gradients at 10 × 20, and your init passes test_build_task.",
        "learningTools": [
            tool(MARIMO, "Create a notebook with `marimo edit`: sliders for n_qubits (2-10), layers (2-20) and an init choice (uniform / near-identity); one cell shows classifier_lab.gradient_scan(n, layers, init=...).",
                 "Uniform init: 0.7171 at 2 × 2 falling to 0.0208 at 10 × 20; near-identity: about 0.84-0.86 everywhere (the lab and solution outputs)."),
        ],
        "seeAlso": ["simulation L200 #10 Warm-up, replications and confidence: report accuracy over several seeds with a spread, not one run."],
        "sources": src("pl_vc", "pl_bp", "pl_angle", "pl_bel", "pl_pypi", "pl_qp"),
        "next": "L400 #17 Hybrid quantum-classical architecture: orchestrator, job queue and backend adapter: wrap the variational loops of lessons 14-16 in an orchestrator and measure what each execution design costs.",
        "how": RAN + "`python classifier_lab.py`, `python try_it.py`, `python solution_init.py` (outputs in README); `python -m unittest` -> 10 tests: 8 OK, 2 PennyLane tests skipped; fail-before proof with BUILD_TASK_MODULE=classifier_lab observed.",
        "pendingCi": ["classifier_pennylane.py (PennyLane 0.45.1 default.qubit, qp.grad, GradientDescentOptimizer)", "test_classifier.py PennyLaneAgrees (2 tests)",
                      "pennylane 0.45.1 with numpy 2.x resolution (CI job l300-extras)"],
        "projectFiles": [("classifier_lab.py", "main lab: dataset, baseline, training with JSON log, gradient scan"),
                         ("circuit_model.py", "helper: batched numpy simulator + parameter shift"),
                         ("solution_init.py", "buildTask reference: near-identity initialisation"), ("test_build_task.py", "buildTask + failureLab proof"),
                         ("classifier_pennylane.py", "SDK path: same model in PennyLane"), ("test_classifier.py", "unittest: numpy always, PennyLane in CI"),
                         ("README.md", "run commands and observed output")],
        "summary": "A variational classifier encodes features as angles, applies trainable layers and reads one expectation value. Judge it against a classical baseline on held-out data over several seeds, and measure gradients before scaling: random init makes wide, deep circuits flat; near-identity init and a local readout keep them trainable.",
    },
]


def build():
    out = []
    for lesson in LESSONS:
        d = dict(lesson)
        lab_dir, main_file = d.pop("dir"), d.pop("file")
        with open(os.path.join(ROOT, LABS, lab_dir, main_file), encoding="utf-8") as f:
            code = f.read()
        assert os.path.exists(os.path.join(ROOT, d["buildTask"]["solution"])), d["buildTask"]["solution"]
        obj = {k: d[k] for k in ("id", "number")}
        obj["level"] = "L300"
        obj.update({k: d[k] for k in ("title", "phase", "category", "description", "outcome")})
        obj["environment"] = ENV.format(sdk=d["sdk"])
        obj.update({k: d[k] for k in ("estimatedTime", "overview", "prerequisites", "glossary", "concepts", "steps")})
        obj["code"] = code
        obj["codeLanguage"] = "python"
        obj["codeWalkthrough"] = d["codeWalkthrough"]
        obj["projectFiles"] = [{"path": posixpath.normpath(f"{LABS}/{lab_dir}/{p}"), "purpose": why} for p, why in d["projectFiles"]]
        obj["projectFiles"] += [{"path": f"{LABS}/{lab_dir}/try_it.py", "purpose": "runs the two tryIt changes"},
                                {"path": f"{LABS}/{lab_dir}/test_try_it.py", "purpose": "tryIt tests"}]
        obj["failureLab"], obj["tradeOffs"], obj["buildTask"] = d["failureLab"], d["tradeOffs"], d["buildTask"]
        obj["expectedResults"], obj["testCases"] = d["expectedResults"], d["testCases"]
        obj["tryIt"] = [{k: v for k, v in t.items() if k != "validatedBy"} for t in d["tryIt"]]
        if "agentAssist" in d:
            obj["agentAssist"] = {k: v for k, v in d["agentAssist"].items() if k != "validatedBy"}
        obj["troubleshooting"], obj["equivalents"] = d["troubleshooting"], d["equivalents"]
        obj["inRealSystems"], obj["useWhen"], obj["simulatorVsReal"] = d["inRealSystems"], d["useWhen"], d["simulatorVsReal"]
        if "caution" in d:
            obj["caution"] = d["caution"]
        obj["checkpoint"], obj["checkYourself"] = d["checkpoint"], d["checkYourself"]
        obj["learningTools"] = d["learningTools"]
        obj["platforms"] = dict(PLATFORMS)
        obj["seeAlso"], obj["sources"], obj["next"] = d["seeAlso"], d["sources"], d["next"]
        tried = " ".join(f"tryIt {i}: {t['validatedBy']}." for i, t in enumerate(d["tryIt"], 1))
        if "agentAssist" in d:
            tried += f" agentAssist: {d['agentAssist']['validatedBy']}."
        tried += f" buildTask + failureLab: {d['buildTask']['solution'].rsplit('/', 1)[1]} passes test_build_task locally; the naive lab module fails it (observed)."
        pending = d["pendingCi"] + [f"learningTools: {t['name']} exercise (manual run)" for t in d["learningTools"]]
        obj["validation"] = {"status": "validated-local", "how": f"{d['how']} {tried} Platforms: {PLATFORM_NOTE}", "pendingCi": pending}
        note = f"content/concepts/L300/{lab_dir}.md"
        assert os.path.exists(os.path.join(ROOT, note)), note
        obj["conceptNote"], obj["conceptSummary"] = note, d["summary"]
        assert 5 <= len(obj["codeWalkthrough"]) <= 7 and 2 <= len(obj["tradeOffs"]) <= 3 and len(obj["tryIt"]) == 2
        assert len(obj["learningTools"]) <= 2
        out.append(obj)
    path = os.path.join(ROOT, "content", "L300.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return path, out


if __name__ == "__main__":
    p, lessons = build()
    print(f"wrote {p}: {len(lessons)} lessons")
