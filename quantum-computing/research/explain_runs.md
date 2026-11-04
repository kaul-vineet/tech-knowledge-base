# Explain runs — real output quoted in content/explain/01.md … 27.md

Date: 2026-11-02 (UTC). Environment: Linux sandbox, Python 3.12.15, numpy 2.5.3, cryptography 50.0.2. Qiskit, Qiskit Aer,
Cirq, Mitiq, PennyLane and qdk are NOT installed, so every SDK-only step is written as "Expected (not run here)" in the
explanations and described from the lesson/README text, never with invented numbers. Labs were run one at a time, from the
lab folder, with the commands shown in each heading. `explain_checks.py` reads this file: every number quoted inside a
"What you see" block (or any fenced output block in a walkthrough / theorem section) must appear below.

## Differences from the lab READMEs / lesson text

- Timing fields differ by machine, as the labs say: lab 17 `local_cpu_s` and lab 18 `local_s` are elided ("…") in the
  READMEs; here QAOA at n = 16 took `local_s` 0.78 (fair) / 1.201 (biased), while lesson 18's option text quotes 1.69 s.
  Lab 21 `ms_per_exchange` was 1.941 / 3.846 / 5.597 here vs 0.398 / 0.451 / … in the README. Byte sizes, ratios,
  counts and every seeded number matched.
- Lab 13: the 4000-shot plain inverse also fails downstream sampling (min -0.0105); the lesson calls it "still slightly
  negative", consistent with this run.
- SDK scripts not runnable here: check_env.py (fails at `import qiskit` after the version table), two_frameworks_lab.py
  (`No module named 'cirq'`; the `[exit 0]` shown is `tail`'s status, the script itself failed), and gates_lab.py,
  shots_lab.py, bell_lab.py, qasm_lab.py, bv_lab.py, grover_lab.py, qft_lab.py, param_lab.py, transpile_lab.py,
  noise_aer.py, mitiq_zne.py, qaoa_qiskit.py, vqe_qiskit.py, classifier_pennylane.py, sampler_qiskit.py,
  bench_qiskit.py, estimate_qdk.py, count_qiskit.py, compile_qiskit.py (not run; their unittest variants skip).
- Labs 15 and 16 rewrite their `logs/*.jsonl` when run; md5 sums were taken before and after and are byte-identical
  (seeded runs), so no lab file changed.
- Lab 20: `noisy_check.py` has no `__main__` output; the ESP-vs-fidelity numbers come from the same calls that
  `test_compile.test_esp_ranks_like_simulated_fidelity` asserts, run as a one-liner below.

## Run log
### `cd labs/L100/01-setup-environment && python crosscheck_numpy.py`
Run: 2026-11-02T12:33Z
```text
numpy 2.5.3
P(X|0>): {'0': 0.0, '1': 1.0}
expected counts for 100 shots: {'1': 100}
[exit 0]
```

### `cd labs/L100/01-setup-environment && python check_env.py`
Run: 2026-11-02T12:33Z
```text
python 3.12.15
qiskit               missing    expected 2.6.1
qiskit-qasm3-import  missing    expected 0.6.0
cirq                 missing    expected 1.7.0
qiskit-aer           missing    expected 0.18.2 (optional)
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/quantum-computing/labs/L100/01-setup-environment/check_env.py", line 55, in <module>
    counts = run_one_qubit()
             ^^^^^^^^^^^^^^^
  File "/mnt/workspace/working/kb/quantum-computing/labs/L100/01-setup-environment/check_env.py", line 33, in run_one_qubit
    from qiskit import QuantumCircuit, transpile
ModuleNotFoundError: No module named 'qiskit'
[exit 1]
```

### `cd labs/L100/01-setup-environment && python try_it.py`
Run: 2026-11-02T12:33Z
```text
try 1  X twice, numpy counts for 100 shots: {'0': 100}
try 2  n=1  statevector bytes=32 (2.98023e-08 GiB)
try 2  n=3  statevector bytes=128 (1.19209e-07 GiB)
try 2  n=30 statevector bytes=17179869184 (16 GiB)
[exit 0]
```

### `cd labs/L100/01-setup-environment && python -m unittest 2>&1 | tail -5`
Run: 2026-11-02T12:33Z
```text
.sss..s
----------------------------------------------------------------------
Ran 7 tests in 0.001s

OK (skipped=4)
[exit 0]
```

### `cd labs/L100/02-qubits-and-gates && python crosscheck_numpy.py`
Run: 2026-11-02T12:34Z
```text
nothing        {'0': 1.0}
x              {'1': 1.0}
h              {'0': 0.5, '1': 0.5}
h_h            {'0': 1.0}
x_on_q0_of_2   {'01': 1.0}
[exit 0]
```

### `cd labs/L100/02-qubits-and-gates && python try_it.py`
Run: 2026-11-02T12:35Z
```text
h_x_h         numpy {'0': 1.0}
x_on_q1_of_2  numpy {'10': 1.0}
[exit 0]
```

### `cd labs/L100/02-qubits-and-gates && python -m unittest 2>&1 | tail -3`
Run: 2026-11-02T12:35Z
```text
Ran 6 tests in 0.001s

OK (skipped=3)
[exit 0]
```

### `cd labs/L100/03-shots-counts-probability && python crosscheck_numpy.py`
Run: 2026-11-02T12:35Z
```text
exact: {'0': 0.5, '1': 0.5}
shots=10     counts={'0': 4, '1': 6}  P('1')~0.600  +/- 0.158
shots=100    counts={'0': 45, '1': 55}  P('1')~0.550  +/- 0.050
shots=1000   counts={'0': 513, '1': 487}  P('1')~0.487  +/- 0.016
shots=10000  counts={'0': 5091, '1': 4909}  P('1')~0.491  +/- 0.005
seed 2024 twice: {'0': 51, '1': 49} {'0': 51, '1': 49}
[exit 0]
```

### `cd labs/L100/03-shots-counts-probability && python try_it.py`
Run: 2026-11-02T12:35Z
```text
try 1  numpy shots=2500 counts={'0': 1294, '1': 1206}  P('1')~0.4824  standard error=0.010
try 2  numpy seed 2024 {'0': 51, '1': 49}  seed 2025 {'0': 52, '1': 48}  identical=False
[exit 0]
```

### `cd labs/L100/03-shots-counts-probability && python -m unittest 2>&1 | tail -3`
Run: 2026-11-02T12:36Z
```text
Ran 10 tests in 0.244s

OK (skipped=6)
[exit 0]
```

### `cd labs/L100/04-bell-pair-entanglement && python crosscheck_numpy.py`
Run: 2026-11-02T12:37Z
```text
amplitudes: [0.7071+0.j 0.    +0.j 0.    +0.j 0.7071+0.j]
probabilities: {'00': 0.5, '11': 0.5}
[exit 0]
```

### `cd labs/L100/04-bell-pair-entanglement && python try_it.py`
Run: 2026-11-02T12:37Z
```text
swapped_cx  numpy {'00': 0.5, '01': 0.5}  product test 0.0
x_after_cx  numpy {'01': 0.5, '10': 0.5}  product test 0.5
[exit 0]
```

### `cd labs/L100/04-bell-pair-entanglement && python -m unittest 2>&1 | tail -3`
Run: 2026-11-02T12:38Z
```text
Ran 8 tests in 0.001s

OK (skipped=5)
[exit 0]
```

### `cd labs/L100/05-openqasm-portability && python crosscheck_qasm_numpy.py`
Run: 2026-11-02T12:38Z
```text
reference_bell_qasm3.qasm: {'00': 0.5, '11': 0.5}
reference_bell_qasm2.qasm: {'00': 0.5, '11': 0.5}
[exit 0]
```

### `cd labs/L100/05-openqasm-portability && python try_it.py`
Run: 2026-11-02T12:39Z
```text
swap_control parser {'00': 0.5, '01': 0.5}
add_s_gate   parser ValueError: unsupported statement: 's q[0]'
[exit 0]
```

### `cd labs/L100/05-openqasm-portability && python agent_assist.py --fake`
Run: 2026-11-02T12:40Z
```text
bell   ACCEPT  matches spec  counts(1000, seed 7) {'00': 502, '11': 498}
ghz3   REJECT  outcomes {'000': 0.5, '011': 0.5} != spec {'000': 0.5, '111': 0.5}
phase  REJECT  parser: unsupported statement: 'rz(pi/2) q[0]'
[exit 0]
```

### `cd labs/L100/05-openqasm-portability && python -m unittest 2>&1 | tail -3`
Run: 2026-11-02T12:42Z
```text
Ran 18 tests in 17.192s

OK (skipped=7)
[exit 0]
```

### `cd labs/L100/06-same-circuit-two-frameworks && python crosscheck_numpy.py`
Run: 2026-11-02T12:43Z
```text
bell     qiskit-order {'00': 0.5, '11': 0.5}  cirq-order {'00': 0.5, '11': 0.5}
x_on_q0  qiskit-order {'01': 1.0}  cirq-order {'10': 1.0}
[exit 0]
```

### `cd labs/L100/06-same-circuit-two-frameworks && python try_it.py`
Run: 2026-11-02T12:43Z
```text
try 1 numpy {'qiskit': '001', 'cirq_raw': '100', 'cirq_in_qiskit_order': '001'}
try 2 numpy {'qiskit': '01', 'cirq_raw': '01', 'cirq_in_qiskit_order': '10'}
[exit 0]
```

### `cd labs/L100/06-same-circuit-two-frameworks && python two_frameworks_lab.py 2>&1 | tail -2`
Run: 2026-11-02T12:44Z
```text
    import cirq
ModuleNotFoundError: No module named 'cirq'
[exit 0]
```

### `cd labs/L100/06-same-circuit-two-frameworks && python -m unittest 2>&1 | tail -3`
Run: 2026-11-02T12:44Z
```text
Ran 9 tests in 0.001s

OK (skipped=4)
[exit 0]
```

### `cd labs/L200/07-bernstein-vazirani && python crosscheck_numpy.py`
Run: 2026-11-02T12:53Z
```text
secret 1011: {'1011': 1.0}
secret 110101: {'110101': 1.0}
all 16 four-bit secrets recovered with probability 1: True
[exit 0]
```

### `cd labs/L200/07-bernstein-vazirani && python try_it.py`
Run: 2026-11-02T12:53Z
```text
no_kickback  numpy {'0000': 1.0}
unreversed   numpy {'1101': 1.0}
[exit 0]
```

### `cd labs/L200/07-bernstein-vazirani && python solution_bias.py`
Run: 2026-11-02T12:53Z
```text
secret 1011 bias 0: numpy {'1011': 1.0}
secret 1011 bias 1: numpy {'1011': 1.0}
[exit 0]
```

### `cd labs/L200/07-bernstein-vazirani && python -m unittest 2>&1 | tail -3`
Run: 2026-11-02T12:54Z
```text
Ran 10 tests in 0.082s

OK (skipped=5)
[exit 0]
```

### `cd labs/L200/08-grover-search && python crosscheck_numpy.py`
Run: 2026-11-02T12:55Z
```text
marked ['11']: oracle diagonal [1, 1, 1, -1]
  optimal k=1  P by k {0: 0.25, 1: 1.0, 2: 0.25, 3: 0.25, 4: 1.0}  matches sin^2 formula: True
marked ['101']: oracle diagonal [1, 1, 1, 1, 1, -1, 1, 1]
  optimal k=2  P by k {0: 0.125, 1: 0.7812, 2: 0.9453, 3: 0.3301, 4: 0.0122}  matches sin^2 formula: True
marked ['011', '100']: oracle diagonal [1, 1, 1, -1, -1, 1, 1, 1]
  optimal k=1  P by k {0: 0.25, 1: 1.0, 2: 0.25, 3: 0.25, 4: 1.0}  matches sin^2 formula: True
[exit 0]
```

### `cd labs/L200/08-grover-search && python try_it.py`
Run: 2026-11-02T12:55Z
```text
overshoot      numpy {'k': 3, 'P': 0.3301, 'optimal_k': 2, 'P_at_optimal': 0.9453}
two_marked_k2  numpy {'k': 2, 'P': 0.25, 'optimal_k': 1, 'P_at_optimal': 1.0}
[exit 0]
```

### `cd labs/L200/08-grover-search && python solution_search.py`
Run: 2026-11-02T12:56Z
```text
x == 5:      (['101'], 2, 0.9453)
x % 3 == 0:  (['000', '011', '110'], 1, 0.8437)
[exit 0]
```

### `cd labs/L200/08-grover-search && python agent_assist.py --fake`
Run: 2026-11-02T12:56Z
```text
single REJECT  marks ['110'] but spec needs ['011']
pair   ACCEPT  oracle ok; k=2 gives P=0.25, code uses k=1: P=1.0
even   REJECT  oracle ok, but best P(success)=0.5 at k=0: no amplification (M/N=2/4)
[exit 0]
```

### `cd labs/L200/09-qft-building-block && python crosscheck_numpy.py`
Run: 2026-11-02T12:58Z
```text
QFT gates vs numpy DFT, max |difference|: 0.0
inverse QFT gates vs numpy DFT^-1 (np.fft.fft ortho): 0.0
QFT|5> magnitudes: [0.3536, 0.3536, 0.3536, 0.3536, 0.3536, 0.3536, 0.3536, 0.3536]
QFT|5> phases (turns): [0.0, 0.625, 0.25, 0.875, 0.5, 0.125, 0.75, 0.375]
[exit 0]
```

### `cd labs/L200/09-qft-building-block && python try_it.py`
Run: 2026-11-02T12:58Z
```text
no_swaps        numpy {'max_error_vs_dft': 0.7071, 'after_bit_reversing_rows': 0.0}
negated_angles  numpy {'max_error_vs_dft': 0.7071, 'max_error_vs_np_fft_fft': 0.0}
[exit 0]
```

### `cd labs/L200/09-qft-building-block && python solution_period.py`
Run: 2026-11-02T12:58Z
```text
period 2 offset 0: QFT probabilities {'000': 0.5, '100': 0.5} -> period 2
period 2 offset 1: QFT probabilities {'000': 0.5, '100': 0.5} -> period 2
period 4 offset 0: QFT probabilities {'000': 0.25, '010': 0.25, '100': 0.25, '110': 0.25} -> period 4
period 4 offset 3: QFT probabilities {'000': 0.25, '010': 0.25, '100': 0.25, '110': 0.25} -> period 4
[exit 0]
```

### `cd labs/L200/10-parameterized-circuits && python crosscheck_numpy.py`
Run: 2026-11-02T13:00Z
```text
exact <Z> at theta = 0, pi/2, pi: [1.0, 0.0, -1.0]
fit exact <Z> [a, b, c]: [1.0, 0.0, 0.0]
fit exact <X> [a, b, c]: [0.0, 1.0, 0.0]
fit sampled <Z>, 400 shots, numpy seed 7: [0.987, -0.004, -0.005]
[exit 0]
```

### `cd labs/L200/10-parameterized-circuits && python try_it.py`
Run: 2026-11-02T13:01Z
```text
rx_instead_of_ry numpy {'fit_Z': [1.0, 0.0, 0.0], 'fit_X': [0.0, 0.0, 0.0]}
fewer_shots      numpy {25: {'fit': [0.969, 0.069, -0.044], 'worst_error': 0.069}, 400: {'fit': [0.987, -0.004, -0.005], 'worst_error': 0.013}}
[exit 0]
```

### `cd labs/L200/10-parameterized-circuits && python solution_offset.py`
Run: 2026-11-02T13:02Z
```text
exact, phi = 0.3: 0.3
400 shots, phi = 0.3: 0.311
[exit 0]
```

### `cd labs/L200/11-transpile-to-device && python crosscheck_numpy.py`
Run: 2026-11-02T13:04Z
```text
{'H == RZ.SX.RZ (global phase)': True, 'X == SX.SX': True, 'SWAP == 3 CX': True}
star CX pairs not on the all-to-all map: []
star CX pairs not on the ring map: [(0, 2), (0, 3)]
star CX pairs not on the line map: [(0, 2), (0, 3), (0, 4)]
heavy-hex distance 3 has 19 qubits
star GHZ probabilities: {'00000': 0.5, '11111': 0.5}
[exit 0]
```

### `cd labs/L200/11-transpile-to-device && python try_it.py`
Run: 2026-11-02T13:04Z
```text
ring_vs_line  local {'all-to-all': 0, 'ring': 2, 'line': 3}
h_in_basis    local {'gates': ['rz', 'sx', 'rz'], 'equals_H_up_to_phase': True, 'global_phase_turns': -0.125}
[exit 0]
```

### `cd labs/L200/11-transpile-to-device && python solution_chain.py`
Run: 2026-11-02T13:05Z
```text
chain vs star (numpy): {'same_state_as_star': True, 'non_adjacent_on_line': []}
[exit 0]
```

### `cd labs/L300/12-noise-models && python noise_lab.py`
Run: 2026-11-02T13:06Z
```text
ideal Bell counts: {'00': 998, '11': 1002}
noisy Bell counts: {'00': 962, '01': 82, '10': 70, '11': 886}
{"n": 2, "p2": 0.0, "fidelity": 0.9866, "success": 0.9337, "p_all0": 0.4862, "p_all1": 0.4475}
{"n": 2, "p2": 0.01, "fidelity": 0.9793, "success": 0.9294, "p_all0": 0.484, "p_all1": 0.4454}
{"n": 2, "p2": 0.02, "fidelity": 0.9719, "success": 0.925, "p_all0": 0.4818, "p_all1": 0.4433}
{"n": 2, "p2": 0.05, "fidelity": 0.9498, "success": 0.912, "p_all0": 0.4751, "p_all1": 0.4369}
{"n": 2, "p2": 0.1, "fidelity": 0.913, "success": 0.8904, "p_all0": 0.4641, "p_all1": 0.4263}
{"n": 3, "p2": 0.0, "fidelity": 0.9769, "success": 0.8966, "p_all0": 0.4756, "p_all1": 0.421}
{"n": 3, "p2": 0.01, "fidelity": 0.9612, "success": 0.8858, "p_all0": 0.47, "p_all1": 0.4159}
{"n": 3, "p2": 0.02, "fidelity": 0.9456, "success": 0.8752, "p_all0": 0.4644, "p_all1": 0.4108}
{"n": 3, "p2": 0.05, "fidelity": 0.8997, "success": 0.8439, "p_all0": 0.448, "p_all1": 0.3959}
{"n": 3, "p2": 0.1, "fidelity": 0.8261, "success": 0.7934, "p_all0": 0.4215, "p_all1": 0.3719}
{"n": 4, "p2": 0.0, "fidelity": 0.9673, "success": 0.8622, "p_all0": 0.466, "p_all1": 0.3962}
{"n": 4, "p2": 0.01, "fidelity": 0.9434, "success": 0.8456, "p_all0": 0.4572, "p_all1": 0.3885}
{"n": 4, "p2": 0.02, "fidelity": 0.92, "success": 0.8293, "p_all0": 0.4484, "p_all1": 0.3809}
{"n": 4, "p2": 0.05, "fidelity": 0.8521, "success": 0.7818, "p_all0": 0.4229, "p_all1": 0.3588}
{"n": 4, "p2": 0.1, "fidelity": 0.7473, "success": 0.7073, "p_all0": 0.383, "p_all1": 0.3242}
naive bell_check on ideal counts: True
naive bell_check on noisy counts: False <- the fault: a correct circuit fails
[exit 0]
```

### `cd labs/L300/12-noise-models && python try_it.py`
Run: 2026-11-02T13:06Z
```text
symmetric_noise       {'p_all0': 0.4454, 'p_all1': 0.4454}
readout_vs_gate_noise {'readout_only': 0.8145, 'cx_only': 0.9037}
[exit 0]
```

### `cd labs/L300/12-noise-models && BUILD_TASK_MODULE=noise_lab python -m unittest test_build_task 2>&1 | tail -12`
Run: 2026-11-02T13:06Z
```text
======================================================================
FAIL: test_correct_circuit_passes_on_noisy_device (test_build_task.HardenedCheck.test_correct_circuit_passes_on_noisy_device)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/mnt/workspace/working/kb/quantum-computing/labs/L300/12-noise-models/test_build_task.py", line 31, in test_correct_circuit_passes_on_noisy_device
    self.assertTrue(mod.bell_check(lab.counts(n, lab.NOISE, seed=seed), n=n), f"n={n} seed={seed}")
AssertionError: False is not true : n=2 seed=0

----------------------------------------------------------------------
Ran 5 tests in 0.559s

FAILED (failures=1)
[exit 0]
```

### `cd labs/L300/12-noise-models && python -m unittest test_build_task 2>&1 | tail -3`
Run: 2026-11-02T13:07Z
```text
Ran 5 tests in 3.428s

OK
[exit 0]
```

### `cd labs/L300/12-noise-models && python solution_tolerant_check.py`
Run: 2026-11-02T13:07Z
```text
noisy Bell counts: {'00': 962, '01': 82, '10': 70, '11': 886} -> tolerant check: True
ideal Bell counts -> tolerant check: True
GHZ-3, 200 seeds on the noisy model: 200/200 pass
[exit 0]
```

### `cd labs/L300/13-error-mitigation && python mitigation_lab.py`
Run: 2026-11-02T13:09Z
```text
{"cal_shots": 4000, "shots": 4000, "raw": [0.4768, 0.0422, 0.0398, 0.4412], "mitigated": [0.5038, 0.0003, -0.0105, 0.5064], "min": -0.0105, "tvd_raw": 0.082, "tvd_mitigated": 0.0105}
  downstream sampling failed: Probabilities are not non-negative
{"cal_shots": 100, "shots": 200, "raw": [0.46, 0.04, 0.04, 0.46], "mitigated": [0.5072, -0.0241, -0.0126, 0.5294], "min": -0.0241, "tvd_raw": 0.08, "tvd_mitigated": 0.0367}
  downstream sampling failed: Probabilities are not non-negative
{"scale": 1, "cx_count": 4, "P000": 0.9039}
{"scale": 3, "cx_count": 12, "P000": 0.7474}
{"scale": 5, "cx_count": 20, "P000": 0.6234}
ideal 1.0 | raw 0.9039 | linear ZNE 0.9687 | Richardson ZNE 0.9944
[exit 0]
```

### `cd labs/L300/13-error-mitigation && python try_it.py`
Run: 2026-11-02T13:10Z
```text
zne_shot_noise       {'raw_mean': 0.9041, 'raw_std': 0.0069, 'richardson_mean': 0.9942, 'richardson_std': 0.017}
clip_vs_constrained  {'clip': 0.0436, 'constrained': 0.0426}
[exit 0]
```

### `cd labs/L300/13-error-mitigation && BUILD_TASK_MODULE=mitigation_lab python -m unittest test_build_task 2>&1 | grep -E FAIL\|Error\|Ran\|OK`
Run: 2026-11-02T13:10Z
```text
FAIL: test_always_a_probability_distribution (test_build_task.ConstrainedMitigation.test_always_a_probability_distribution)
AssertionError: np.float64(-0.008180304680361005) not greater than or equal to 0.0 : (100, 200)
Ran 3 tests in 2.243s
FAILED (failures=1)
[exit 0]
```

### `cd labs/L300/13-error-mitigation && python -m unittest test_build_task 2>&1 | tail -3`
Run: 2026-11-02T13:10Z
```text
Ran 3 tests in 3.718s

OK
[exit 0]
```

### `cd labs/L300/14-qaoa-maxcut && python qaoa_lab.py`
Run: 2026-11-02T13:12Z
```text
brute force: max cut 5 by ['01001', '01011', '10100', '10110']
{"p": 1, "method": "grid 41x21", "gamma": 0.6283, "beta": 0.3927, "ratio": 0.8188}
{"p": 1, "method": "grid + descent", "ratio": 0.822}
{"p": 2, "method": "random start seed 0", "ratio": 0.7002, "params": [2.067, 0.909, -0.493, 0.029]}
most likely bitstring 01101 (cut 4), P(any optimal cut) = 0.1137
[exit 0]
```

### `cd labs/L300/14-qaoa-maxcut && python try_it.py`
Run: 2026-11-02T13:12Z
```text
random_starts     {'ratios': [0.7002, 0.8352, 0.9247, 0.9247, 0.7009, 0.8329, 0.7002, 0.8329], 'hits': 2}
sample_the_answer {'P_optimal': 0.707, 'best_sampled_cut': 5, 'optimal_samples': 13}
[exit 0]
```

### `cd labs/L300/14-qaoa-maxcut && BUILD_TASK_MODULE=qaoa_lab python -m unittest test_build_task 2>&1 | grep -E FAIL\|Error\|Ran\|OK`
Run: 2026-11-02T13:12Z
```text
FAIL: test_p1_reaches_grid_quality (test_build_task.Restarts.test_p1_reaches_grid_quality)
AssertionError: 0.6997 not greater than or equal to 0.82
FAIL: test_p2_reaches_best_known_ratio (test_build_task.Restarts.test_p2_reaches_best_known_ratio)
AssertionError: 0.7002 not greater than or equal to 0.92
Ran 3 tests in 12.808s
FAILED (failures=2)
[exit 0]
```

### `cd labs/L300/14-qaoa-maxcut && python -m unittest test_build_task 2>&1 | tail -3`
Run: 2026-11-02T13:13Z
```text
Ran 3 tests in 25.684s

OK
[exit 0]
```

### `cd labs/L300/15-hybrid-vqe-loop && python vqe_lab.py`
Run: 2026-11-02T13:15Z
```text
exact ground energy E0 = -1.8405
{"optimizer": "gd", "shots": null, "error": 0.0, "log": "vqe_gd_exact.jsonl", "iters": 100, "best_energy_est": -1.84046, "final_energy_est": -1.84046, "evals": 900, "tail_energy_std": 0.0001, "tail_grad_norm_median": 0.007}
{"optimizer": "gd", "shots": 1000, "error": 1.5645, "log": "vqe_gd_1000.jsonl", "iters": 100, "best_energy_est": -1.77348, "final_energy_est": -0.27276, "evals": 900, "tail_energy_std": 0.3912, "tail_grad_norm_median": 15.5125}
[exit 0]
```

### `cd labs/L300/15-hybrid-vqe-loop && head -3 logs/vqe_gd_1000.jsonl`
Run: 2026-11-02T13:16Z
```text
{"optimizer": "gd", "shots": 1000, "iter": 0, "energy_est": -1.03512, "grad_norm": 9.907, "evals": 9}
{"optimizer": "gd", "shots": 1000, "iter": 1, "energy_est": -1.5862, "grad_norm": 26.537, "evals": 18}
{"optimizer": "gd", "shots": 1000, "iter": 2, "energy_est": -1.23532, "grad_norm": 8.852, "evals": 27}
[exit 0]
```

### `cd labs/L300/15-hybrid-vqe-loop && python solution_spsa.py`
Run: 2026-11-02T13:16Z
```text
{"optimizer": "spsa", "shots": 1000, "error": 0.0064, "log": "vqe_spsa_1000.jsonl", "iters": 150, "best_energy_est": -1.84964, "final_energy_est": -1.8256, "evals": 450, "tail_energy_std": 0.0065, "tail_grad_norm_median": null}
errors over seeds 0-5: [0.0064, 0.0154, 0.0123, 0.0033, 0.0114, 0.0188]
[exit 0]
```

### `cd labs/L300/15-hybrid-vqe-loop && python try_it.py`
Run: 2026-11-02T13:16Z
```text
more_shots_same_optimizer {1000: {'error': 1.5645, 'total_shots': 1800000}, 100000: {'error': 0.9195, 'total_shots': 180000000}, 1000000: {'error': 0.0076, 'total_shots': 1800000000}}
spsa_cost (for comparison) {'error': 0.0064, 'total_shots': 900000}
below_the_ground_energy   {'E0': -1.8405, 'best_energy_est': -1.84964, 'rows_below_E0': 8, 'rows': 150}
[exit 0]
```

### `cd labs/L300/15-hybrid-vqe-loop && python agent_assist.py --fake`
Run: 2026-11-02T13:17Z
```text
diagnose ACCEPT  code ran spsa @ 1000 shots: error 0.0064
report   REJECT  best_energy -1.8405 is not in the log (log min -1.77348); diagnosis 'learning_rate_too_high' != code rule 'shot_noise'; code ran gd @ 1000 shots: error 0.7429
costly   REJECT  proposal needs 1,800,000,000 shots > budget 2,000,000 (not run)
[exit 0]
```

### `cd labs/L300/15-hybrid-vqe-loop && BUILD_TASK_MODULE=vqe_lab python -m unittest test_build_task 2>&1 | grep -E FAIL\|Error\|Ran\|OK`
Run: 2026-11-02T13:19Z
```text
FAIL: test_converges_under_shot_noise (test_build_task.RobustOptimizer.test_converges_under_shot_noise)
AssertionError: 1.5645 not less than 0.03 : seed 0
Ran 2 tests in 8.885s
FAILED (failures=1)
[exit 0]
```

### `cd labs/L300/15-hybrid-vqe-loop && python -m unittest test_build_task 2>&1 | tail -3`
Run: 2026-11-02T13:19Z
```text
Ran 2 tests in 3.229s

OK
[exit 0]
```

### `cd labs/L300/16-quantum-classifier && python classifier_lab.py`
Run: 2026-11-02T13:21Z
```text
{"model": "quantum 2q x 2 layers (5 params)", "train_acc": 0.975, "test_acc": 0.9}
{"model": "logistic regression (3 params)", "train_acc": 0.975, "test_acc": 0.85}
test accuracy over 5 dataset seeds (quantum, classical): [(1.0, 1.0), (0.95, 0.95), (0.95, 0.95), (0.9, 0.85), (0.85, 0.8)]
shot-noise floor for one gradient at 1000 shots: 0.0224
{"n": 2, "layers": 2, "readout": "local", "median_abs_grad": 0.7171, "below_shot_floor": 0.0}
{"n": 6, "layers": 12, "readout": "local", "median_abs_grad": 0.1121, "below_shot_floor": 0.1}
{"n": 10, "layers": 20, "readout": "local", "median_abs_grad": 0.0208, "below_shot_floor": 0.55}
[exit 0]
```

### `cd labs/L300/16-quantum-classifier && sed -n '1p;60p' logs/train_2q_2l.jsonl`
Run: 2026-11-02T13:21Z
```text
{"epoch": 0, "loss": 2.0398, "train_acc": 0.425, "grad_norm": 0.5546}
{"epoch": 59, "loss": 0.2661, "train_acc": 0.975, "grad_norm": 0.0116}
[exit 0]
```

### `cd labs/L300/16-quantum-classifier && python try_it.py`
Run: 2026-11-02T13:21Z
```text
global_readout_with_good_init {'local': 0.8742, 'global': 0.0303}
shot_noise_at_prediction      {'exact': 0.9, '100_shots': 0.85}
[exit 0]
```

### `cd labs/L300/16-quantum-classifier && python solution_init.py`
Run: 2026-11-02T13:22Z
```text
{"n": 2, "layers": 2, "readout": "local", "median_abs_grad": 0.844, "below_shot_floor": 0.0}
{"n": 6, "layers": 12, "readout": "local", "median_abs_grad": 0.8312, "below_shot_floor": 0.0}
{"n": 10, "layers": 20, "readout": "local", "median_abs_grad": 0.863, "below_shot_floor": 0.0}
{"model": "quantum 2q x 2 layers, near-identity init", "train_acc": 0.95, "test_acc": 0.9}
[exit 0]
```

### `cd labs/L300/16-quantum-classifier && BUILD_TASK_MODULE=classifier_lab python -m unittest test_build_task 2>&1 | grep -E FAIL\|Error\|Ran\|OK`
Run: 2026-11-02T13:22Z
```text
FAIL: test_wide_deep_model_has_usable_gradients (test_build_task.NearIdentityInit.test_wide_deep_model_has_usable_gradients)
AssertionError: 0.0163 not greater than np.float64(0.224)
Ran 2 tests in 5.129s
FAILED (failures=1)
[exit 0]
```

### `cd labs/L300/16-quantum-classifier && python -m unittest test_build_task 2>&1 | tail -3`
Run: 2026-11-02T13:22Z
```text
Ran 2 tests in 3.101s

OK
[exit 0]
```

### `cd labs/L400/17-hybrid-architecture && python orchestrator.py`
Run: 2026-11-02T13:25Z
```text
{"mode": "sync", "wall_s": 606.3, "billed_s": 4.8, "jobs": 240, "circuits": 240, "transpiles": 240, "cache_hits": 0, "retries": 0, "best_ratio": 0.6922, "local_cpu_s": 0.19}
{"mode": "batched", "wall_s": 186.3, "billed_s": 4.8, "jobs": 30, "circuits": 240, "transpiles": 240, "cache_hits": 0, "retries": 0, "best_ratio": 0.6922, "local_cpu_s": 0.37}
{"mode": "session", "wall_s": 131.2, "billed_s": 131.2, "jobs": 30, "circuits": 240, "transpiles": 240, "cache_hits": 0, "retries": 0, "best_ratio": 0.6922, "local_cpu_s": 0.42}
{"mode": "batched", "wall_s": 196.3, "billed_s": 4.8, "jobs": 30, "circuits": 240, "transpiles": 240, "cache_hits": 0, "retries": 3, "best_ratio": 0.6922, "local_cpu_s": 0.5, "note": "seeded transient failures on attempts 3, 4, 17"}
[exit 0]
```

### `cd labs/L400/17-hybrid-architecture && python solution_cache_key.py`
Run: 2026-11-02T13:27Z
```text
{"mode": "sync", "wall_s": 486.8, "billed_s": 4.8, "jobs": 240, "circuits": 240, "transpiles": 1, "cache_hits": 239, "retries": 0, "best_ratio": 0.6922, "local_cpu_s": 0.11}
{"mode": "batched", "wall_s": 66.8, "billed_s": 4.8, "jobs": 30, "circuits": 240, "transpiles": 1, "cache_hits": 239, "retries": 0, "best_ratio": 0.6922, "local_cpu_s": 0.17}
{"mode": "session", "wall_s": 11.7, "billed_s": 11.7, "jobs": 30, "circuits": 240, "transpiles": 1, "cache_hits": 239, "retries": 0, "best_ratio": 0.6922, "local_cpu_s": 0.19}
[exit 0]
```

### `cd labs/L400/17-hybrid-architecture && python try_it.py`
Run: 2026-11-02T13:29Z
```text
busy_queue (wall_s, billed_s)         {'sync': (7206.8, 4.8), 'batched': (906.8, 4.8), 'session': (39.7, 39.7)}
slow_classical_step (wall_s, billed_s) {'sync': (2585.3, 4.8), 'batched': (2165.3, 4.8), 'session': (2165.3, 2165.3)}
[exit 0]
```

### `cd labs/L400/17-hybrid-architecture && BUILD_TASK_MODULE=orchestrator python -m unittest test_build_task test_fitness 2>&1 | grep -E FAIL\|Error\|Ran\|OK`
Run: 2026-11-02T13:30Z
```text
FAIL: test_one_transpile_per_structure (test_build_task.CacheKey.test_one_transpile_per_structure)
AssertionError: 240 != 1
FAIL: test_same_structure_new_angles_same_key (test_build_task.CacheKey.test_same_structure_new_angles_same_key)
AssertionError: Tuples differ: (Temp[125 chars](6, 7)), p=1), (np.float64(0.1), np.float64(0.2)), 'line-8', 1) != (Temp[125 chars](6, 7)), p=1), (np.float64(0.7), np.float64(1.1)), 'line-8', 1)
FAIL: test_compile_once (test_fitness.ExecutionDesignFitness.test_compile_once)
AssertionError: 240 != 1
FAIL: test_wall_and_billing_budget (test_fitness.ExecutionDesignFitness.test_wall_and_billing_budget)
AssertionError: 186.3 not less than or equal to 90.0
Ran 7 tests in 2.616s
FAILED (failures=4)
[exit 0]
```

### `cd labs/L400/17-hybrid-architecture && python -m unittest test_build_task test_fitness 2>&1 | tail -3`
Run: 2026-11-02T13:31Z
```text
Ran 7 tests in 2.109s

OK
[exit 0]
```

### `cd labs/L400/18-benchmark-vs-classical && python bench_lab.py`
Run: 2026-11-02T13:33Z
```text
{"n": 8, "solver": "greedy", "budget": 200, "runs": 1, "median_ratio": 1.0, "success": 1.0, "median_first_best": 32, "tts99_samples": 200, "local_s": 0.059}
{"n": 8, "solver": "annealing", "budget": 200, "runs": 1, "median_ratio": 0.8, "success": 0.0, "median_first_best": 3, "tts99_samples": null, "local_s": 0.001}
{"n": 8, "solver": "qaoa", "budget": 200, "runs": 1, "median_ratio": 1.0, "success": 1.0, "median_first_best": 412, "tts99_samples": 200, "local_s": 0.053}
{"n": 8, "winner": "greedy", "method": "naive (unequal budget, best seed)"}
{"n": 12, "solver": "greedy", "budget": 200, "runs": 1, "median_ratio": 0.8, "success": 0.0, "median_first_best": 48, "tts99_samples": null, "local_s": 0.048}
{"n": 12, "solver": "annealing", "budget": 200, "runs": 1, "median_ratio": 0.8667, "success": 0.0, "median_first_best": 25, "tts99_samples": null, "local_s": 0.003}
{"n": 12, "solver": "qaoa", "budget": 200, "runs": 1, "median_ratio": 1.0, "success": 1.0, "median_first_best": 426, "tts99_samples": 200, "local_s": 0.126}
{"n": 12, "winner": "qaoa", "method": "naive (unequal budget, best seed)"}
{"n": 16, "solver": "greedy", "budget": 200, "runs": 1, "median_ratio": 0.9545, "success": 0.0, "median_first_best": 48, "tts99_samples": null, "local_s": 0.001}
{"n": 16, "solver": "annealing", "budget": 200, "runs": 1, "median_ratio": 1.0, "success": 1.0, "median_first_best": 24, "tts99_samples": 200, "local_s": 0.001}
{"n": 16, "solver": "qaoa", "budget": 200, "runs": 1, "median_ratio": 1.0, "success": 1.0, "median_first_best": 450, "tts99_samples": 200, "local_s": 1.201}
{"n": 16, "winner": "annealing", "method": "naive (unequal budget, best seed)"}
[exit 0]
```

### `cd labs/L400/18-benchmark-vs-classical && python solution_fair.py`
Run: 2026-11-02T13:34Z
```text
{"n": 8, "solver": "greedy", "budget": 200, "runs": 10, "median_ratio": 1.0, "success": 1.0, "median_first_best": 36, "tts99_samples": 200, "local_s": 0.006}
{"n": 8, "solver": "annealing", "budget": 200, "runs": 10, "median_ratio": 1.0, "success": 1.0, "median_first_best": 33, "tts99_samples": 200, "local_s": 0.013}
{"n": 8, "solver": "qaoa", "budget": 200, "runs": 10, "median_ratio": 1.0, "success": 1.0, "median_first_best": 111, "tts99_samples": 200, "local_s": 0.025}
{"n": 8, "winner": "annealing", "method": "fair (same budget, same 10 seeds, medians)"}
{"n": 12, "solver": "greedy", "budget": 200, "runs": 10, "median_ratio": 0.9333, "success": 0.4, "median_first_best": 66, "tts99_samples": 1803, "local_s": 0.003}
{"n": 12, "solver": "annealing", "budget": 200, "runs": 10, "median_ratio": 0.9333, "success": 0.3, "median_first_best": 62, "tts99_samples": 2582, "local_s": 0.01}
{"n": 12, "solver": "qaoa", "budget": 200, "runs": 10, "median_ratio": 0.9667, "success": 0.5, "median_first_best": 115, "tts99_samples": 1329, "local_s": 0.04}
{"n": 12, "winner": "qaoa", "method": "fair (same budget, same 10 seeds, medians)"}
{"n": 16, "solver": "greedy", "budget": 200, "runs": 10, "median_ratio": 1.0, "success": 0.9, "median_first_best": 136, "tts99_samples": 400, "local_s": 0.001}
{"n": 16, "solver": "annealing", "budget": 200, "runs": 10, "median_ratio": 1.0, "success": 0.8, "median_first_best": 85, "tts99_samples": 572, "local_s": 0.003}
{"n": 16, "solver": "qaoa", "budget": 200, "runs": 10, "median_ratio": 1.0, "success": 0.6, "median_first_best": 141, "tts99_samples": 1005, "local_s": 0.78}
{"n": 16, "winner": "greedy", "method": "fair (same budget, same 10 seeds, medians)"}
[exit 0]
```

### `cd labs/L400/18-benchmark-vs-classical && python try_it.py`
Run: 2026-11-02T13:34Z
```text
other_instances {1: 'annealing', 2: 'greedy', 3: 'qaoa', 4: 'annealing', 5: 'annealing'}
exact_in_budget ({'greedy': 1.0, 'annealing': 1.0, 'qaoa': 1.0, 'exact': 1.0}, 'greedy')
[exit 0]
```

### `cd labs/L400/18-benchmark-vs-classical && BUILD_TASK_MODULE=bench_lab python -m unittest test_build_task test_fitness 2>&1 | grep -E FAIL\|Error\|Ran\|OK`
Run: 2026-11-02T13:35Z
```text
FAIL: test_over_budget_solver_is_rejected (test_build_task.FairHarness.test_over_budget_solver_is_rejected)
    with self.assertRaises(RuntimeError):
AssertionError: RuntimeError not raised
FAIL: test_rows_summarise_every_run (test_build_task.FairHarness.test_rows_summarise_every_run)
AssertionError: Lists differ: [1, 1] != [4, 4]
FAIL: test_same_budget_and_seeds_for_every_solver (test_build_task.FairHarness.test_same_budget_and_seeds_for_every_solver)
AssertionError: Lists differ: [(25, 1)] != [(100, 1), (100, 2), (100, 3)]
FAIL: test_reference_config (test_fitness.ComparisonMethodFitness.test_reference_config)
AssertionError: Items in the first set but not the second:
Ran 6 tests in 13.129s
FAILED (failures=4)
[exit 0]
```

### `cd labs/L400/18-benchmark-vs-classical && python -m unittest test_build_task test_fitness 2>&1 | tail -3`
Run: 2026-11-02T13:35Z
```text
Ran 6 tests in 4.665s

OK
[exit 0]
```

### `cd labs/L400/19-resource-estimation && python estimate_lab.py`
Run: 2026-11-02T13:37Z
```text
{"workload": "qaoa n=20 p=1", "logical_qubits": 20, "cx": 60, "rotations": 50, "depth": 14, "t_count": 2350, "logical_cycles": 249, "distance": 3, "physical_qubits": 360, "runtime_s": 0.000747, "p_fail": 1.0, "class": "simulate"}
{"workload": "qaoa n=100 p=1", "logical_qubits": 100, "cx": 300, "rotations": 250, "depth": 14, "t_count": 13500, "logical_cycles": 284, "distance": 3, "physical_qubits": 1800, "runtime_s": 0.000852, "p_fail": 1.0, "class": "nisq-candidate"}
{"workload": "qaoa n=100 p=4", "logical_qubits": 100, "cx": 1200, "rotations": 1000, "depth": 53, "t_count": 60000, "logical_cycles": 1253, "distance": 3, "physical_qubits": 1800, "runtime_s": 0.003759, "p_fail": 1.0, "class": "fault-tolerant-feasible"}
{"workload": "qaoa n=1000 p=10", "logical_qubits": 1000, "cx": 30000, "rotations": 25000, "depth": 131, "t_count": 1850000, "logical_cycles": 3831, "distance": 3, "physical_qubits": 18000, "runtime_s": 0.01149, "p_fail": 1.0, "class": "fault-tolerant-feasible"}
{"workload": "rsa-1024", "logical_qubits": 3093, "toffoli": 327491256, "t_count": 2292438792, "depth": 534773760, "logical_cycles": 534773760, "distance": 3, "physical_qubits": 55674, "runtime_s": 1604.0, "p_fail": 1.0, "class": "fault-tolerant-feasible"}
{"workload": "rsa-2048", "logical_qubits": 6190, "toffoli": 2624225018, "t_count": 18369575126, "depth": 2143289344, "logical_cycles": 2143289344, "distance": 3, "physical_qubits": 111420, "runtime_s": 6430.0, "p_fail": 1.0, "class": "fault-tolerant-feasible"}
[exit 0]
```

### `cd labs/L400/19-resource-estimation && python solution_distance.py`
Run: 2026-11-02T13:38Z
```text
{"workload": "qaoa n=20 p=1", "logical_qubits": 20, "t_count": 2350, "logical_cycles": 249, "distance": 9, "physical_qubits": 3240, "runtime_s": 0.002241, "p_fail": 0.00149, "class": "simulate"}
{"workload": "qaoa n=100 p=1", "logical_qubits": 100, "t_count": 13500, "logical_cycles": 284, "distance": 9, "physical_qubits": 16200, "runtime_s": 0.002556, "p_fail": 0.00852, "class": "nisq-candidate"}
{"workload": "qaoa n=100 p=4", "logical_qubits": 100, "t_count": 60000, "logical_cycles": 1253, "distance": 11, "physical_qubits": 24200, "runtime_s": 0.01378, "p_fail": 0.00376, "class": "fault-tolerant-feasible"}
{"workload": "qaoa n=1000 p=10", "logical_qubits": 1000, "t_count": 1850000, "logical_cycles": 3831, "distance": 15, "physical_qubits": 450000, "runtime_s": 0.05746, "p_fail": 0.00115, "class": "fault-tolerant-feasible"}
{"workload": "rsa-1024", "logical_qubits": 3093, "t_count": 2292438792, "logical_cycles": 534773760, "distance": 25, "physical_qubits": 3866250, "runtime_s": 13370.0, "p_fail": 0.00496, "class": "infeasible (assumptions above)"}
{"workload": "rsa-2048", "logical_qubits": 6190, "t_count": 18369575126, "logical_cycles": 2143289344, "distance": 27, "physical_qubits": 9025020, "runtime_s": 57870.0, "p_fail": 0.00398, "class": "infeasible (assumptions above)"}
[exit 0]
```

### `cd labs/L400/19-resource-estimation && python try_it.py`
Run: 2026-11-02T13:39Z
```text
better_hardware {'distance': 13, 'physical_qubits': 2092220, 'runtime_s': 27860.0}
near_threshold  {0.001: (11, 24200), 0.005: (37, 273800), 0.009: 'no distance <= 101 meets budget 0.01', 0.011: 'physical error 0.011 is not below the threshold 0.01'}
[exit 0]
```

### `cd labs/L400/19-resource-estimation && BUILD_TASK_MODULE=estimate_lab python -m unittest test_build_task test_fitness 2>&1 | grep -E ^FAIL\|Error\|^Ran\|OK`
Run: 2026-11-02T13:39Z
```text
FAIL: test_meets_the_budget_and_is_minimal (test_build_task.Distance.test_meets_the_budget_and_is_minimal)
AssertionError: 37.59 not less than or equal to 0.01
FAIL: test_refuses_above_threshold (test_build_task.Distance.test_refuses_above_threshold)
    with self.assertRaises(ValueError):
AssertionError: ValueError not raised
FAIL: test_rsa_2048_needs_distance_27 (test_build_task.Distance.test_rsa_2048_needs_distance_27)
AssertionError: 3 != 27
FAIL: test_decision_table (test_fitness.FeasibilityFitness.test_decision_table)
AssertionError: Lists differ: ['sim[76 chars]e', 'fault-tolerant-feasible', 'fault-tolerant-feasible'] != ['sim[76 chars]e', 'infeasible (assumptions above)', 'infeasi[20 chars]ve)']
FAIL: test_every_estimate_meets_the_error_budget (test_fitness.FeasibilityFitness.test_every_estimate_meets_the_error_budget)
AssertionError: False is not true : [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
Ran 7 tests in 0.695s
FAILED (failures=5)
[exit 0]
```

### `cd labs/L400/19-resource-estimation && python -m unittest test_build_task test_fitness 2>&1 | tail -3`
Run: 2026-11-02T13:40Z
```text
Ran 7 tests in 0.001s

OK
[exit 0]
```

### `cd labs/L400/19-resource-estimation && python -m unittest test_estimate 2>&1 | tail -3`
Run: 2026-11-02T13:40Z
```text
Ran 8 tests in 0.444s

OK (skipped=2)
[exit 0]
```

### `cd labs/L400/20-error-aware-compilation && python compile_lab.py`
Run: 2026-11-02T13:42Z
```text
{"device": "calibrated", "option": "A trivial + hop routing", "layout": [0, 1, 2, 3, 4], "esp": 0.5763, "cx": 27, "depth": 32, "within_depth_budget": false}
{"device": "calibrated", "option": "B dense + hop routing + cancel", "layout": [1, 5, 2, 6, 3], "esp": 0.7315, "cx": 19, "depth": 24, "within_depth_budget": false}
{"device": "drifted (1,2) = 15%", "option": "A trivial + hop routing", "layout": [0, 1, 2, 3, 4], "esp": 0.2084, "cx": 27, "depth": 32, "within_depth_budget": false}
{"device": "drifted (1,2) = 15%", "option": "B dense + hop routing + cancel", "layout": [1, 5, 2, 6, 3], "esp": 0.3059, "cx": 19, "depth": 24, "within_depth_budget": false}
logical circuit: {'esp': 1.0, 'cx': 12, 'depth': 17}
[exit 0]
```

### `cd labs/L400/20-error-aware-compilation && python solution_layout.py`
Run: 2026-11-02T13:43Z
```text
{"device": "calibrated", "option": "C noise-aware layout + reliable routing + cancel", "layout": [2, 3, 6, 1, 5], "esp": 0.7925, "cx": 13, "depth": 18, "within_depth_budget": true}
{"device": "drifted (1,2) = 15%", "option": "C noise-aware layout + reliable routing + cancel", "layout": [5, 1, 6, 2, 3], "esp": 0.7835, "cx": 19, "depth": 21, "within_depth_budget": true}
[exit 0]
```

### `cd labs/L400/20-error-aware-compilation && python noisy_check.py`
Run: 2026-11-02T13:43Z
```text
[exit 0]
```

### `cd labs/L400/20-error-aware-compilation && python try_it.py`
Run: 2026-11-02T13:44Z
```text
other_drift  {'layout': [1, 2, 5, 0, 4], 'esp': 0.7503, 'cx': 13, 'depth': 18, 'uses_drifted_edge': False, 'noisy_fidelity': 0.9855}
tight_budget {'esp': 0.7835, 'cx': 19, 'depth': 21, 'within_budget': False}
[exit 0]
```

### `cd labs/L400/20-error-aware-compilation && BUILD_TASK_MODULE=compile_lab python -m unittest test_build_task test_fitness 2>&1 | grep -E ^FAIL\|Error\|^Ran\|OK`
Run: 2026-11-02T13:45Z
```text
FAIL: test_beats_the_trivial_layout_by_far (test_build_task.NoiseAwareLayout.test_beats_the_trivial_layout_by_far)
AssertionError: 0.5943 not greater than or equal to 0.75
FAIL: test_calibrated_device (test_fitness.CompiledCircuitFitness.test_calibrated_device)
AssertionError: 38 not less than or equal to 22
FAIL: test_drifted_device (test_fitness.CompiledCircuitFitness.test_drifted_device)
AssertionError: 50 not less than or equal to 22
Ran 5 tests in 14.984s
FAILED (failures=3)
[exit 0]
```

### `cd labs/L400/20-error-aware-compilation && python -m unittest test_build_task test_fitness 2>&1 | tail -3`
Run: 2026-11-02T13:46Z
```text
Ran 5 tests in 28.778s

OK
[exit 0]
```

### `cd labs/L400/20-error-aware-compilation && python -c "import compile_lab as lab, device as D, noisy_check as nc
dev = D.make_device(drift=D.DRIFT)
for layout, w, o in ((lab.choose_layout(dev), False, False), ([5, 1, 6, 2, 3], True, True)):
    ops, final, m = lab.compile_circuit(dev, layout, w, o); print(layout, 'esp', m['esp'], 'simulated fidelity', nc.noisy_fidelity(ops, final, dev))"`
Run: 2026-11-02T13:47Z
```text
[0, 1, 2, 3, 4] esp 0.2084 simulated fidelity 0.8959
[5, 1, 6, 2, 3] esp 0.7835 simulated fidelity 0.9878
[exit 0]
```

### `cd labs/L400/20-error-aware-compilation && python -m unittest test_compile 2>&1 | tail -3`
Run: 2026-11-02T13:48Z
```text
Ran 6 tests in 0.415s

OK (skipped=1)
[exit 0]
```

### `cd labs/L400/21-post-quantum-migration && python pqc_lab.py`
Run: 2026-11-02T13:50Z
```text
{"shor_model": {"workload": "rsa-2048", "logical_qubits": 6190, "distance": 27, "physical_qubits": 9025020, "runtime_s": 57870.0}, "ecc": {"workload": "ecc-p256", "logical_qubits": 2330, "toffoli": 128748355584}}
{"source": "Gidney & Ekera 2019/2021", "target": "RSA-2048", "physical_qubits": 20000000, "runtime": "8 hours"}
{"source": "Gidney 2025", "target": "RSA-2048", "physical_qubits": 1000000, "runtime": "under a week", "note": "'less than a million'"}
{"scanner": "grep", "findings": 5}
{"file": "toy_app/auth.py", "line": 1, "algorithm": "RSA", "usage": "unknown", "secrecy_years": 0, "priority": "P2 before 2030 (deprecated after 2030, disallowed after 2035)", "replacement": "review manually"}
{"file": "toy_app/billing.py", "line": 1, "algorithm": "RSA", "usage": "unknown", "secrecy_years": 10, "priority": "P2 before 2030 (deprecated after 2030, disallowed after 2035)", "replacement": "review manually"}
{"file": "toy_app/billing.py", "line": 3, "algorithm": "RSA", "usage": "unknown", "secrecy_years": 10, "priority": "P2 before 2030 (deprecated after 2030, disallowed after 2035)", "replacement": "review manually"}
{"file": "toy_app/billing.py", "line": 7, "algorithm": "RSA", "usage": "unknown", "secrecy_years": 10, "priority": "P2 before 2030 (deprecated after 2030, disallowed after 2035)", "replacement": "review manually"}
{"file": "toy_app/config/tls.toml", "line": 3, "algorithm": "RSA-2048", "usage": "unknown", "secrecy_years": 5, "priority": "P2 before 2030 (deprecated after 2030, disallowed after 2035)", "replacement": "review manually"}
{"kem": "x25519", "public_key_bytes": 32, "ciphertext_bytes": 32, "ms_per_exchange": 1.941}
{"kem": "ml-kem-768", "public_key_bytes": 1184, "ciphertext_bytes": 1088, "ms_per_exchange": 3.846}
{"kem": "x25519+ml-kem-768", "public_key_bytes": 1216, "ciphertext_bytes": 1120, "ms_per_exchange": 5.597}
[exit 0]
```

### `cd labs/L400/21-post-quantum-migration && python solution_scanner.py`
Run: 2026-11-02T13:51Z
```text
{"scanner": "ast", "findings": 8}
{"file": "toy_app/billing.py", "line": 7, "algorithm": "RSA-3072", "usage": "key-establishment", "secrecy_years": 10, "priority": "P1 now (harvest now, decrypt later)", "replacement": "ML-KEM-768 (FIPS 203); hybrid X25519+ML-KEM-768 during transition"}
{"file": "toy_app/sync.py", "line": 7, "algorithm": "ECDH P-384", "usage": "key-establishment", "secrecy_years": 7, "priority": "P1 now (harvest now, decrypt later)", "replacement": "ML-KEM-768 (FIPS 203); hybrid X25519+ML-KEM-768 during transition"}
{"file": "toy_app/api_client.py", "line": 11, "algorithm": "X25519", "usage": "key-establishment", "secrecy_years": 2, "priority": "P2 before 2030 (deprecated after 2030, disallowed after 2035)", "replacement": "ML-KEM-768 (FIPS 203); hybrid X25519+ML-KEM-768 during transition"}
{"file": "toy_app/auth.py", "line": 11, "algorithm": "ECDSA P-256", "usage": "signature", "secrecy_years": 0, "priority": "P2 before 2030 (deprecated after 2030, disallowed after 2035)", "replacement": "ML-DSA-65 (FIPS 204)"}
{"file": "toy_app/config/tls.toml", "line": 3, "algorithm": "RSA-2048", "usage": "signature", "secrecy_years": 5, "priority": "P2 before 2030 (deprecated after 2030, disallowed after 2035)", "replacement": "ML-DSA-65 (FIPS 204)"}
{"file": "toy_app/config/tls.toml", "line": 4, "algorithm": "ECDHE X25519/P-256", "usage": "key-establishment", "secrecy_years": 5, "priority": "P2 before 2030 (deprecated after 2030, disallowed after 2035)", "replacement": "ML-KEM-768 (FIPS 203); hybrid X25519+ML-KEM-768 during transition"}
{"file": "toy_app/api_client.py", "line": 19, "algorithm": "AES-GCM", "usage": "symmetric", "secrecy_years": 2, "priority": "none", "replacement": "keep (AES-256 / SHA-256 not broken by Shor)"}
{"file": "toy_app/storage.py", "line": 10, "algorithm": "AES-GCM", "usage": "symmetric", "secrecy_years": 10, "priority": "none", "replacement": "keep (AES-256 / SHA-256 not broken by Shor)"}
[exit 0]
```

### `cd labs/L400/21-post-quantum-migration && python try_it.py`
Run: 2026-11-02T13:52Z
```text
longer_secrecy ['toy_app/api_client.py:11', 'toy_app/billing.py:7', 'toy_app/sync.py:7']
old_receiver   receiver rejects envelope: unknown kem 'x25519+ml-kem-768'
[exit 0]
```

### `cd labs/L400/21-post-quantum-migration && python agent_assist.py --fake`
Run: 2026-11-02T13:52Z
```text
draft     ACCEPT  
summarise REJECT  toy_app/storage.py:10 is symmetric (AES-GCM): keep it, do not replace; P1 item missing: toy_app/sync.py:7
creative  REJECT  toy_app/payments.py:12 is not in the inventory; toy_app/auth.py:11 replacement 'ML-KEM-768' != 'ML-DSA-65'; year 2029 is not a NIST IR 8547 date
[exit 0]
```

### `cd labs/L400/21-post-quantum-migration && BUILD_TASK_MODULE=pqc_lab python -m unittest test_build_task test_fitness 2>&1 | grep -E ^FAIL\|Error\|^Ran\|OK`
Run: 2026-11-02T13:52Z
```text
FAIL: test_aliased_and_from_imports_resolve (test_build_task.Inventory.test_aliased_and_from_imports_resolve)
AssertionError: None != 'ECDSA P-256'
FAIL: test_docstrings_are_not_findings (test_build_task.Inventory.test_docstrings_are_not_findings)
AssertionError: ('toy_app/auth.py', 1) unexpectedly found in {('toy_app/auth.py', 1): {'file': 'toy_app/auth.py', 'line': 1, 'algorithm': 'RSA', 'usage': 'unknown'}, ('toy_app/billing.py', 1): {'file': 'toy_app/billing.py', 'line': 1, 'algorithm': 'RSA', 'usage': 'unknown'}, ('toy_app/billing.py', 3): {'file': 'toy_app/billing.py', 'line': 3, 'algorithm': 'RSA', 'usage': 'unknown'}, ('toy_app/billing.py', 7): {'file': 'toy_app/billing.py', 'line': 7, 'algorithm': 'RSA', 'usage': 'unknown'}, ('toy_app/config/tls.toml', 3): {'file': 'toy_app/config/tls.toml', 'line': 3, 'algorithm': 'RSA-2048', 'usage': 'unknown'}}
FAIL: test_matches_ground_truth (test_build_task.Inventory.test_matches_ground_truth)
AssertionError: Lists differ: [{'file': 'toy_app/auth.py', 'line': 1, 'algorithm': 'RSA', '[356 chars]wn'}] != [{'file': 'toy_app/api_client.py', 'line': 11, 'algorithm': '[711 chars]nt'}]
FAIL: test_purpose_is_classified (test_build_task.Inventory.test_purpose_is_classified)
AssertionError: 'unknown' != 'key-establishment'
FAIL: test_ratchet_blocks_new_quantum_vulnerable_code (test_fitness.MigrationFitness.test_ratchet_blocks_new_quantum_vulnerable_code)
AssertionError: Lists differ: [{'file': 'toy_app/auth.py', 'line': 1, 'a[282 chars]wn'}] != []
FAIL: test_recall_and_precision (test_fitness.MigrationFitness.test_recall_and_precision)
AssertionError: Tuples differ: (0.0, 0.0) != (1.0, 1.0)
Ran 7 tests in 1.558s
FAILED (failures=6)
[exit 0]
```

### `cd labs/L400/21-post-quantum-migration && python -m unittest test_build_task test_fitness 2>&1 | tail -3`
Run: 2026-11-02T13:53Z
```text
Ran 7 tests in 37.434s

OK
[exit 0]
```

### `cd labs/L400/22-capstone && python run_capstone.py`
Run: 2026-11-02T13:56Z
```text
{"milestone": "M1 API and validation", "pass": true, "measure": {"health": 200, "solve": 200, "bad_request": 400, "bad_reason": "n must be an integer in [4, 16]"}}
{"milestone": "M2 orchestrated quantum path (batched, cached, retried)", "pass": true, "measure": {"jobs": 10, "retries": 2, "transpiles": 1, "wall_s": 28.8, "mode": "batched"}}
{"milestone": "M3 compile + noise model", "pass": true, "measure": {"esp": 0.5072, "cx": 52, "depth": 42, "gate_fidelity": 0.6224, "tvd_model": 0.0213, "tvd_ideal": 0.073}}
{"milestone": "M4 readout mitigation", "pass": true, "measure": {"ideal": 7.3525, "gate_noise_only": 6.8418, "raw": 6.774, "mitigated": 6.8549, "calibration_shots": 32000}}
{"milestone": "M5 fair benchmark + code decides", "pass": true, "measure": {"winner": "annealing", "n12_winner": "annealing", "n12_reason": "needs 12 qubits > 8 on the device"}}
{"milestone": "M6 agent explains, code checks", "pass": true, "measure": {"explain": ["ACCEPT", []], "pitch": ["REJECT", ["claims qaoa-noisy wins; code decided annealing", "claims a quantum advantage the benchmark cannot show", "number 99.9 is not in the report"]], "brief": ["REJECT", ["no winner stated"]]}}
{"rubric": "correctness", "measure": "winner median ratio 1.0", "pass": true}
{"rubric": "fairness", "measure": "one budget and one seed list for every solver", "pass": true}
{"rubric": "reliability", "measure": "2 injected job failures retried; results identical to a fault-free run", "pass": true}
{"rubric": "cost", "measure": "modelled wall 28.8 s, 10 jobs (budget 60 s)", "pass": true}
{"rubric": "honesty", "measure": "n = 12 refused for the 8-qubit device; classical answer returned", "pass": true}
{"rubric": "safety", "measure": "agent cannot change the winner; server binds 127.0.0.1", "pass": true}
{"scorecard": "6/6 milestones, 6/6 rubric", "winner": "annealing", "decided_by": "code"}
[exit 0]
```

### `cd labs/L400/22-capstone && python try_it.py`
Run: 2026-11-02T13:57Z
```text
small_budget      ('annealing', {'greedy': 1.0, 'annealing': 1.0, 'qaoa-noisy': 1.0})
calibrated_device {'esp': 0.5103, 'gate_fidelity': 0.6262, 'cx': 47, 'depth': 48}
[exit 0]
```

### `cd labs/L400/22-capstone && python pipeline.py | head -c 1500`
Run: 2026-11-02T13:58Z
```text
{
 "request": {
  "n": 8,
  "graph_seed": 3,
  "budget": 2000,
  "seeds": 5,
  "faults": [
   3,
   4
  ],
  "drift": true
 },
 "optimum": 10,
 "feasibility": {
  "class": "simulate",
  "device_qubits": 8,
  "quantum_path": true,
  "reason": "fits the device and the simulator"
 },
 "benchmark": [
  {
   "n": 8,
   "solver": "greedy",
   "budget": 2000,
   "runs": 5,
   "median_ratio": 1.0,
   "success": 1.0,
   "median_first_best": 32,
   "tts99_samples": 2000,
   "local_s": 0.025
  },
  {
   "n": 8,
   "solver": "annealing",
   "budget": 2000,
   "runs": 5,
   "median_ratio": 1.0,
   "success": 1.0,
   "median_first_best": 13,
   "tts99_samples": 2000,
   "local_s": 0.054
  },
  {
   "n": 8,
   "solver": "qaoa-noisy",
   "budget": 2000,
   "runs": 5,
   "median_ratio": 1.0,
   "success": 1.0,
   "median_first_best": 1013,
   "tts99_samples": 2000,
   "local_s": 0.415
  }
 ],
 "winner": "annealing",
 "decided_by": "code: median ratio > success > samples to best; ties -> classical",
 "execution": {
  "jobs": 10,
  "retries": 2,
  "transpiles": 1,
  "wall_s": 28.8,
  "mode": "batched"
 },
 "compile": {
  "layout": [
   6,
   4,
   7,
   1,
   3,
   5,
   2,
   0
  ],
  "esp": 0.5072,
  "cx": 52,
  "depth": 42,
  "within_depth_budget": true,
  "gate_fidelity": 0.6224
 },
 "mitigation": {
  "ideal": 7.3525,
  "gate_noise_only": 6.8418,
  "raw": 6.774,
  "mitigated": 6.8549,
  "calibration_shots": 32000
 }
}
[exit 0]
```

### `cd labs/L400/22-capstone && python -m unittest 2>&1 | tail -3`
Run: 2026-11-02T14:00Z
```text
Ran 13 tests in 22.173s

OK
[exit 0]
```

### `cd labs/L500/23-linear-algebra-for-qubits && python theorems.py`
Run: 2026-11-02T14:02Z
```text
[T23.1] Unitaries preserve inner products, norms and total probability
  1000 random unitaries (dims 2,4,8,16): max |<Ua|Ub> - <a|b>| < 1e-12: True
  max | ||Ua|| - 1 | < 1e-12: True
  qsim circuit H, CX, RY(0.7), CP(0.3) on 3 qubits: U^dagger U = I within 1e-12: True
  probabilities after the circuit sum to 1.000000
  non-unitary [[1,1],[0,1]] maps |1> to a vector of norm 1.4142 (probabilities would sum to 2.0)
[T23.2] Tensor products: (A x B)(C x D) = AC x BD, <a x b|c x d> = <a|c><b|d>, U x V is unitary
  mixed-product rule on 200 random 2x2 pairs: max error < 1e-10: True
  inner product of product states factorises (200 cases): max error < 1e-12: True
  U (x) V for random 2x2 and 4x4 unitaries is an 8x8 unitary: True
  |+> (x) |1> = [0.0, 0.7071, 0.0, 0.7071] (basis 00,01,10,11) = qsim H on q1, X on q0: True
[T23.3] Born rule in any orthonormal basis; global phase unobservable, relative phase observable
  300 random states and bases (dims 2,4,8): sum_k |<b_k|psi>|^2 = 1 within 1e-12: True
  multiplying by a random global phase changes no probability (within 1e-12): True
  Z basis: |+> gives {'0': 0.5, '1': 0.5}, |-> gives {'0': 0.5, '1': 0.5} (identical)
  X basis (H then measure): |+> gives {'0': 1.0}, |-> gives {'1': 1.0} (relative phase is visible)
[T23.4] Bell state statistics: P(same outcome) = cos^2(a - b), E = cos 2(a - b)
  computational basis: {'00': 0.5, '11': 0.5}
  a = 0.0000, b = 0.0000: P(same) = 1.0000, cos^2(a-b) = 1.0000, E = 1.0000; 20000 sampled shots within 4 sigma: True
  a = 0.0000, b = 0.3927: P(same) = 0.8536, cos^2(a-b) = 0.8536, E = 0.7071; 20000 sampled shots within 4 sigma: True
  a = 0.0000, b = 0.7854: P(same) = 0.5000, cos^2(a-b) = 0.5000, E = 0.0000; 20000 sampled shots within 4 sigma: True
  a = 0.3927, b = -0.3927: P(same) = 0.5000, cos^2(a-b) = 0.5000, E = 0.0000; 20000 sampled shots within 4 sigma: True
  a = 0.3000, b = 1.1000: P(same) = 0.4854, cos^2(a-b) = 0.4854, E = -0.0292; 20000 sampled shots within 4 sigma: True
  the four Bell states are orthonormal (Gram matrix = I): True
  CX then H maps them to 00, 01, 10, 11 with probability 1 (Bell measurement)
[exit 0]
```

### `cd . && python research/l500_checks.py 2>&1 | tail -5`
Run: 2026-11-02T14:02Z
```text
5 lessons; 12 theorem checks re-run; 40 problems, 26 recomputed (64 values); 16 exam values recomputed
OK
[exit 0]
```

### `cd labs/L500/24-quantum-information-basics && python theorems.py`
Run: 2026-11-02T14:05Z
```text
[T24.1] No-cloning: no unitary U and blank |e> give U|psi>|e> = |psi>|psi> for all psi
  CNOT copier clones |0> and |1> exactly (fidelity 1)
  theta = 0.0000: joint fidelity 1.0000 = (c^3 + s^3)^2 = 1.0000; copy alone 1.0000 = c^4 + s^4
  theta = 1.0472: joint fidelity 0.5999 = (c^3 + s^3)^2 = 0.5999; copy alone 0.6250 = c^4 + s^4
  theta = 1.5708: joint fidelity 0.5000 = (c^3 + s^3)^2 = 0.5000; copy alone 0.5000 = c^4 + s^4
  theta = 2.0944: joint fidelity 0.5999 = (c^3 + s^3)^2 = 0.5999; copy alone 0.6250 = c^4 + s^4
  theta = 3.1416: joint fidelity 1.0000 = (c^3 + s^3)^2 = 1.0000; copy alone 1.0000 = c^4 + s^4
  minimum fidelity 0.5000 at theta = pi/2 (|+> becomes a Bell state, not |+>|+>)
  500 random unitaries keep <0,e|+,e> = 0.7071; perfect clones would need <0|+>^2 = 0.5000: impossible
[T24.2] Teleportation and superdense coding are exact for every input
  200 random states x 4 outcomes: each outcome has probability 0.25 (within 1e-12) and Bob's corrected qubit has fidelity 1 (within 1e-12): True
  psi = cos(pi/8)|0> + sin(pi/8)|1>: outcome probabilities [0.25, 0.25, 0.25, 0.25]
  superdense coding, message ab -> Bob decodes (q0 q1): 00 -> 00, 01 -> 01, 10 -> 10, 11 -> 11 with probability 1
[T24.3] Deutsch-Jozsa: P(0^n) = 1 if f is constant and 0 if f is balanced, with one query
  n = 3: both constant functions give P(000) = 1.0000, 1.0000
  all 70 balanced functions give P(000) = 0.0000 (max)
  ancilla circuit for f = x0 XOR x2 (|-> ancilla, phase kickback): P(inputs 000) = 0.0000
  a deterministic classical algorithm needs 2^(n-1) + 1 = 5 queries in the worst case
[T24.4] Density matrices: trace 1, PSD, purity; partial trace of a Bell pair is I/2; no signalling
  Bell pair: global purity Tr(rho^2) = 1.0000; rho_A = rho_B = I/2: True; Tr(rho_B^2) = 0.5000
  200 random 2-qubit pure states: Hermitian, eigenvalues >= 0, trace 1: True
  no signalling: Alice's random unitary or unread measurement changes rho_B by < 1e-12: True
  mixture 1/2|0><0| + 1/2|+><+|: eigenvalues [0.8536, 0.1464], purity 0.7500
[exit 0]
```

### `cd labs/L500/25-algorithms-and-complexity && python theorems.py`
Run: 2026-11-02T14:06Z
```text
[T25.1] Grover: P_k = sin^2((2k+1) theta), sin theta = sqrt(M/N); best k ~ (pi/4) sqrt(N/M)
  N =     4, M = 1: best k =   1 (floor(pi/(4 theta)) =   1, (pi/4) sqrt(N/M) =    1.57), P = 1.0000
  N =    16, M = 1: best k =   3 (floor(pi/(4 theta)) =   3, (pi/4) sqrt(N/M) =    3.14), P = 0.9613
  N =    64, M = 1: best k =   6 (floor(pi/(4 theta)) =   6, (pi/4) sqrt(N/M) =    6.28), P = 0.9966
  N =   256, M = 1: best k =  12 (floor(pi/(4 theta)) =  12, (pi/4) sqrt(N/M) =   12.57), P = 0.9999
  N =  1024, M = 1: best k =  25 (floor(pi/(4 theta)) =  25, (pi/4) sqrt(N/M) =   25.13), P = 0.9995
  N =  1024, M = 4: best k =  12 (floor(pi/(4 theta)) =  12, (pi/4) sqrt(N/M) =   12.57), P = 0.9999
  N =  4096, M = 1: best k =  50 (floor(pi/(4 theta)) =  50, (pi/4) sqrt(N/M) =   50.27), P = 0.9999
  statevector simulation matches sin^2((2k+1) theta) for every k tested (max error < 1e-9): True
  overshoot, N = 64: P at k = 6 is 0.9966, at k = 12 it is 0.0001 (rotation keeps turning)
[T25.2] The QFT matrix F_jk = e^{2 pi i jk/N}/sqrt(N) is unitary and is built by O(n^2) gates
  F^dagger F = I for N = 2 .. 256 (max error < 1e-10): True
  qsim circuit (H, CP, SWAP) equals F for n = 1 .. 5 (max error < 1e-10): True
  n = 1: 1 H + 0 controlled phases + 0 swaps = 1 gates (n(n+1)/2 + floor(n/2)); FFT on 2^n entries ~ n 2^n = 2
  n = 2: 2 H + 1 controlled phases + 1 swaps = 4 gates (n(n+1)/2 + floor(n/2)); FFT on 2^n entries ~ n 2^n = 8
  n = 3: 3 H + 3 controlled phases + 1 swaps = 7 gates (n(n+1)/2 + floor(n/2)); FFT on 2^n entries ~ n 2^n = 24
  n = 4: 4 H + 6 controlled phases + 2 swaps = 12 gates (n(n+1)/2 + floor(n/2)); FFT on 2^n entries ~ n 2^n = 64
  n = 5: 5 H + 10 controlled phases + 2 swaps = 17 gates (n(n+1)/2 + floor(n/2)); FFT on 2^n entries ~ n 2^n = 160
[T25.3] Phase estimation: exact when phi = m/2^t; otherwise the nearest m has P >= 4/pi^2
  t = 3, phi = 0.1250: most likely m = 1 (m/8 = 0.1250), P = 1.0000
  t = 3, phi = 0.3333: most likely m = 3 (m/8 = 0.3750), P = 0.6878
  t = 3, phi = 0.3000: most likely m = 2 (m/8 = 0.2500), P = 0.5775
  t = 3, phi = 0.7071: most likely m = 6 (m/8 = 0.7500), P = 0.6719
  t = 3, phi = 0.5625 (halfway between 4/8 and 5/8): P(4) = P(5) = 0.4105
  simulated distribution equals |(1/T) sum_k e^{2 pi i k (phi - m/T)}|^2 for t = 3..6 (max error < 1e-10): True
  smallest P(most likely m) over all cases = 0.4054 >= 4/pi^2 = 0.4053: True
[T25.4] Shor's reduction: an even order r with a^(r/2) != -1 (mod N) yields gcd(a^(r/2) - 1, N)
  N = 15: 6/7 = 0.8571 of the coprime a in [2, N-1] succeed; e.g. a = 2, r = 4, gcd(2^2 - 1, 15) = 3, 15 = 3 x 5
  N = 21: 6/11 = 0.5455 of the coprime a in [2, N-1] succeed; e.g. a = 2, r = 6, gcd(2^3 - 1, 21) = 7, 21 = 7 x 3
  N = 33: 10/19 = 0.5263 of the coprime a in [2, N-1] succeed; e.g. a = 5, r = 10, gcd(5^5 - 1, 33) = 11, 33 = 11 x 3
  N = 35: 18/23 = 0.7826 of the coprime a in [2, N-1] succeed; e.g. a = 2, r = 12, gcd(2^6 - 1, 35) = 7, 35 = 7 x 5
  N = 91: 54/71 = 0.7606 of the coprime a in [2, N-1] succeed; e.g. a = 2, r = 12, gcd(2^6 - 1, 91) = 7, 91 = 7 x 13
  order finding, N = 15, a = 7, t = 8: outcomes {0: 0.25, 64: 0.25, 128: 0.25, 192: 0.25}; one run recovers r = 4 with P = 0.5000
  N = 21, a = 2, t = 9: a likely outcome m = 427, 427/512 -> continued fraction 5/6 -> r = 6; one run recovers r = 6 with P = 0.3084
[exit 0]
```

