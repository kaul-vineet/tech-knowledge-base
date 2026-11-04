# Concept: the quantum toolchain and the simulator

## Why it matters
Nobody on your team has quantum hardware, yet you must build, run and test circuits offline, identically on every laptop and in CI.

## Mental model
A **compiler toolchain plus an emulator**. The SDK builds circuits, the transpiler compiles them for a target, the simulator runs them on your CPU, and pinned versions are the lockfile.

```
requirements.txt ─▶ venv: qiskit 2.6.1 · cirq 1.7.0
circuit ─transpile─▶ StatevectorSampler.run(shots) ─▶ counts {'1': 100}
```

## How it works
1. **Isolate and pin.** A venv holds the exact SDK versions, so every machine runs the same APIs → see lab step 2.
2. **Predict independently.** A qubit is two amplitudes; X turns (1, 0) into (0, 1), so P(1) = 1. Plain numpy gives the answer before any SDK runs → see lab step 4.
3. **Build, transpile, execute.** `QuantumCircuit(1)` starts in |0⟩ and `qc.x(0)` flips it. `transpile` rewrites the circuit into instructions the target supports. Qiskit's reference `StatevectorSampler` applies each gate as matrix arithmetic and samples once per shot: `{'1': 100}` (Aer is an optional, faster equivalent) → see lab step 5.

## Common mistakes
- Installing into the system Python, so versions drift between machines.
- Skipping `transpile`. Simulators forgive it for simple gates; hardware rejects instructions outside its supported set.
- Asking a statevector simulator for "just 40 qubits". Each amplitude is 16 bytes and there are 2ⁿ of them: 30 qubits need 16 GiB, 40 need 16384 GiB (computed by `research/concepts_worked_examples.py`).
