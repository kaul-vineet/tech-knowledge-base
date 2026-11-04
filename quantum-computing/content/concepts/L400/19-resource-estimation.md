# Concept: Resource estimation and feasibility

## Why it matters
"How many qubits?" has two answers that differ by orders of magnitude. An algorithm needs logical qubits. A
fault-tolerant machine builds each logical qubit from many physical ones and runs many error-correction cycles per
logical step. Product decisions such as "should we prototype this on hardware?" or "when is RSA-2048 at risk?" depend
on carrying the estimate through to physical qubits and wall time, with an error budget, before anything runs.

## Mental model
An estimate is a pipeline of counts and models.

```
problem size ─▶ logical counts ─▶ code distance d ─▶ physical qubits, runtime ─▶ feasibility class
 (n, p, bits)   qubits, CX, depth,   from error budget    ≈ 2d² per logical qubit    simulate | NISQ |
                T-count, cycles      p_L(d) per cycle     cycles × d × 1 µs          FT | infeasible
```

The surface-code model is p_L(d) = 0.03 · (p / 0.01)^((d+1)/2) per logical qubit per logical cycle. This is Fowler
et al. (2012) Eq. 11, and the default crossing prefactor and threshold of the QDK's `SurfaceCode` model. The rotated
code uses d² data qubits plus d² − 1 measurement qubits. Arbitrary rotations cost about 3·log2(1/ε) T gates (Ross &
Selinger). A Toffoli costs 7 T gates, which the lab verifies against its unitary.

## Design space
- **Count a built circuit.** Exact, but only for sizes you can construct. The lab's counted CX and rotation numbers
  equal the formulas for n = 6 to 12. The formula's depth is an upper bound that is tight with 4 edge colours.
- **Analytic formulas.** Scale to any n: CX = 2·|E|·p, rotations = p(|E| + n), depth = 1 + p(3c + 1). For Shor, use
  Gidney & Ekerå's 3n + 0.002 n lg n logical qubits and 0.3n³ + 0.0005 n³ lg n Toffolis.
- **A full estimator** such as the Microsoft QDK's `qdk.qre`. It models factories, layouts and Pareto trade-offs,
  costs a separate environment, and runs here only in CI.

## How to decide
Choose d as the smallest odd distance with logical qubits × cycles × p_L(d) ≤ budget. Refuse when p is at or above
the 1 % threshold, because a larger code is then worse. Then classify:
- simulate if ≤ 30 qubits (16 GiB statevector),
- NISQ candidate if (1 − 10⁻³)^CX ≥ 0.5,
- fault-tolerant-feasible if ≤ 10⁶ physical qubits and ≤ 1 day,
- otherwise infeasible.

Worked example (p = 10⁻³, 1 µs cycles, 1 % budget, data blocks only):
- QAOA n = 100, p = 4: 60,000 T gates, 1253 logical cycles, d = 11, 24,200 physical qubits, 13.8 ms.
  Fault-tolerant-feasible.
- RSA-2048: 6190 logical qubits, 1.84 × 10¹⁰ T gates, d = 27, 9,025,020 physical qubits, 16.1 h. Infeasible
  under this threshold.

Gidney & Ekerå's whole-machine estimate (20 million qubits, 8 h) and Gidney's 2025 estimate (under a million qubits,
under a week) bracket it. Better hardware moves the number fast: at p = 10⁻⁴, RSA-2048 needs d = 13 and 2,092,220
physical qubits (try it 1).

## Failure modes at scale
- **Fixed distance.** "17 physical qubits per logical qubit" (d = 3) reported RSA-2048 as feasible with 111,420
  qubits, while its own failure probability was 1.0. The signal: p_fail is greater than the budget.
- **Near threshold.** At p = 0.005 the distance jumps to 37 (273,800 qubits for QAOA n = 100, p = 4). At 0.009 no
  d ≤ 101 fits. Estimates explode before they fail.
- **Missing overheads.** Factories, routing and decoding are excluded here. Expect QDK's numbers to be higher; a gap
  of more than about 30× means a model is wrong.

## Common mistakes
- Quoting logical qubits as if they were physical qubits.
- Using circuit depth instead of T-limited logical cycles for the runtime.
- Treating a planning bound as a forecast. Say which overheads are included.
