# Lesson 25 - Foundations III: performance theory

Seeded simulations for T25.1-T25.4: M/M/1 against its closed form, Little's law (exact on a window that ends empty), tail amplification under fan-out, Amdahl and USL (closed-form peak, plus a fitted simulated lock-contention system).

Stdlib only (Python 3.12+); seeded, so the output below is identical on every run and on macOS, Windows and Linux.
The same output is quoted as `checkOutput` in `content/L500.json`; `python research/l500_checks.py` (from the topic folder) fails if they drift apart.

## Run
```bash
python perf_proofs.py              # all checks
python perf_proofs.py <name>       # one check: mm1 | little | tail | usl
python -m unittest -v        # test_perf_proofs.py: smaller runs, same invariants
```

## Expected output (observed on Python 3.12, Linux)
```
T25.1 M/M/1, mu = 1 per ms, 400,000 customers per load (seeded simulation vs closed form)
  rho=0.5: W sim  2.001 theory  2.000 | L sim  1.000 theory  1.000 | P(N=0) sim 0.501 theory 0.500 | P(N=2) sim 0.124 theory 0.125
  rho=0.8: W sim  4.992 theory  5.000 | L sim  3.990 theory  4.000 | P(N=0) sim 0.202 theory 0.200 | P(N=2) sim 0.129 theory 0.128
  rho=0.9: W sim  9.838 theory 10.000 | L sim  8.846 theory  9.000 | P(N=0) sim 0.103 theory 0.100 | P(N=2) sim 0.083 theory 0.081
T25.2 Little's law on a G/G/1 queue (uniform-jitter arrivals, log-normal service), seeded
  window [0, 124,978.064] starts and ends empty, 100,011 customers:
    area under n(t) = 163,913.199728; sum of sojourn times = 163,913.199728; relative difference 1.1e-15
    L = 1.311536; lambda * W = 0.800228 * 1.638952 = 1.311536
  arbitrary window [0, 124,966.47]: L = 1.3113, lambda * W (W truncated at the edge) = 1.3113
T25.3 tail amplification: each leaf log-normal (median 10 ms), 'slow' = above the leaf p99 (64.3 ms); 100,000 root requests per fan-out
  fan-out   1: P(root waits for a slow leaf) sim 0.0095, 1 - 0.99^n = 0.0100
  fan-out  10: P(root waits for a slow leaf) sim 0.0954, 1 - 0.99^n = 0.0956
  fan-out 100: P(root waits for a slow leaf) sim 0.6329, 1 - 0.99^n = 0.6340
  to keep the root's p99 at the leaf-p99 level with fan-out 100, each leaf must meet its 0.999900 quantile (about p99.99)
T25.4 Amdahl and USL
  Amdahl sigma=0.05: S(2)=1.90, S(8)=5.93, S(16)=9.14, S(64)=15.42, S(1024)=19.64; bound 1/sigma = 20
  USL sigma=0.02, kappa=0.0005: p* formula 44.27, integer argmax 44, C(p*)=15.68
  USL sigma=0.1, kappa=0.001: p* formula 30.00, integer argmax 30, C(p*)=6.29
  USL sigma=0.03, kappa=0.0001: p* formula 98.49, integer argmax 98, C(p*)=20.16
  simulated closed system (p workers, think Exp(1), shared FIFO lock held 0.05 + 0.004(p-1)): C(1)=1.00, C(4)=3.99, C(8)=7.49, C(12)=9.97, C(16)=9.54, C(24)=7.40, C(32)=6.04, C(40)=5.10
  USL fit (sigma >= 0): sigma=0.0000, kappa=0.00429 -> predicted peak p*=15.3; measured peak at p=13 (C=10.17); throughput falls after the peak: C(40)/C(peak)=0.50
```

## What to look for
- Each line pairs a theorem's prediction with what the code observed. A proof says *always*; the check says *in every case we tried* - a counterexample would refute the proof, agreement only corroborates it.
- The *broken* variants (Lamport/vector clocks without the max, Paxos ignoring phase-1 values) show the proofs' assumptions are load-bearing.
- Simulation numbers carry sampling error; the lesson's problem set asks you to explain each gap.
