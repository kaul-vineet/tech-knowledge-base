# Hardware — Simulation L100-L400 (Mac mini + Windows PC)

**What runs where.** Every lab runs on both machines: single-threaded Python + numpy on the CPU; no GPU needed. Optional agent assist (lessons 6, 7, 14): Ollama uses CPU + GPU on Apple M-series (macOS 14+); Windows GPU support not checked. Installs: `../../shared/WORKSTATION-SETUP.md`. GUI tools: `LEARNING-TOOLS.md`. The suggested model `qwen2.5:1.5b` is a 986 MB download.

**Wheels.** SciPy's official builds include macOS arm64 and Windows; numpy lists both. Exact wheel file names could not be retrieved, so CI installs with `--only-binary=:all:` on `macos-latest` (arm64) and `windows-latest` (x64) to prove wheels exist. SimPy and Mesa ship pure-Python wheels. Windows on ARM was not checked.

**RAM** (tracemalloc on Linux; `research/hardware_measure.py`; interpreter not included):
| Workload | Peak |
|---|---|
| Labs 2, 4, 5, 6 | ≤ 3.5 MiB each |
| Lab 3 (stores 200,000 waits) | 28.9 MiB |
| Schelling similarity pass, 300×300 / 1000×1000 grid | 4.8 / 53.4 MiB |

A numpy grid needs about 55 bytes per cell: 8 GB is plenty. Mesa agents are Python objects and cost more per agent (not measured).

**CPU cores.** Lessons 16, 20, 22 use process pools. macOS and Windows start workers with *spawn*, so keep the pool under `if __name__ == "__main__":` and give each replication its own seed.

**Floating point.** Integer work and IEEE-exact operations (+ − × ÷, sqrt) give the same bits on Apple silicon and x64. That covers the generator streams and the Schelling grid. `math.log`, used by `random.expovariate`, wraps the platform C library, and NumPy warns that CPUs differ in edge cases. The last bit of a value may differ between macOS, Windows and Linux. Printed results should still match: `labs/L*/cross_platform` check them in CI, and the lesson 6 hash rounds values to 9 decimals.
