# 17 · Survey pipeline architecture: ingest, calibrate, detect, catalogue - throughput measured

A small survey night: 48 raw 128 × 128 frames delivered as float32 bytes, with a master bias and flat, and a moonlight gradient across the sky (300 → 900 e⁻). The data is **synthetic**, with a truth list of every star. `survey.py` runs ingest → calibrate → detect → catalogue three ways:
- **A:** sequential, one frame per unit.
- **B:** a spawn process pool, one frame per task.
- **C:** vectorised batches of 16 frames in one process.

It scores completeness and purity against the truth and checks that all three produce the **same** catalogue. Timings per unit go to `pipeline_metrics.jsonl`.

Read the concept note first: `../../../content/concepts/L400/17-survey-pipeline.md`. Main lab: Python 3.12 + numpy only. Helpers: `survey_sim.py` (seeded night), `pool_worker.py` (spawn-safe worker loader).

## Run
```bash
python survey.py
```
Windows (PowerShell) and macOS (zsh) use the same command from the lab folder (`cd labs\L400\17-survey-pipeline` on Windows, `cd labs/L400/17-survey-pipeline` on macOS). The `if __name__ == "__main__":` guard is required: macOS and Windows start pool workers with *spawn*.

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux, 1 CPU)
Detections, completeness, purity and the catalogue hash are seeded and identical on every run. `frames_per_s` is wall-clock (best of 3 for A and C) and varies from run to run and machine to machine.
```
{"option": "A", "frames_per_s": 431.7, "detections": 172, "completeness": 0.1745, "purity": 1.0, "catalogue_sha": "cb7b9698de2d"}
{"option": "B", "frames_per_s": 17.7, "detections": 172, "completeness": 0.1745, "purity": 1.0, "catalogue_sha": "cb7b9698de2d"}
{"option": "C", "frames_per_s": 913.7, "detections": 172, "completeness": 0.1745, "purity": 1.0, "catalogue_sha": "cb7b9698de2d"}
```
One line of `pipeline_metrics.jsonl` per unit (A: per frame, B: per frame, C: per 16-frame batch):
```
{"option": "A", "unit": 0, "frames": 1, "ingest_s": 7e-05, "calibrate_s": 7e-05, "detect_s": 0.0128}
{"option": "C", "unit": 2, "frames": 16, "ingest_s": 0.00113, "calibrate_s": 0.00146, "detect_s": 0.01245}
```

## Failure lab: break it, see it, fix it
- **Fault (shipped in `survey.py`):** `background()` uses one median per frame. The gradient inflates the robust rms, so the 5σ threshold rises. Only 172 of the night's stars are found (completeness 0.1745), and purity stays at 1.0, so nothing *looks* wrong.
- **Fix (your build task):** a SExtractor-style mesh: 32 × 32 px box medians, bilinear interpolation, and one linearly extrapolated virtual box beyond each edge (`solution/survey.py`). This gives 1808 detections, completeness 0.9729 and purity 0.984.
- **Proof:** `BUILD_TARGET=mine python -m unittest test_build_task test_fitness` on the shipped file gives 3 failures (both build-task tests plus the fitness quality test); the solution passes. `TestFailureLab` in `test_survey.py` keeps the fault reproducible.

## Design decision and fitness function
- ADR: `decisions/0001-survey-pipeline-execution.md` chooses **C** with the mesh background. On 1 CPU, B is 10–19 frames/s because spawn start-up and pickling dominate at this frame size; C is about 259 frames/s.
- Fitness: `test_fitness.py` requires completeness ≥ 0.95, purity ≥ 0.98, identical A/B/C catalogues, and C ≥ 50 frames/s (best of 3; a generous wall-clock bound). Observed: `Ran 3 tests ... OK`; run 3× in a row: OK, OK, OK.

## Test
```bash
python -m unittest -v
```
Observed: `Ran 9 tests ... OK` (about 15 s; the spawn pool starts twice).

## Try it
```bash
python try_it.py
```
Observed:
```
1. 3 sigma, 32 px mesh: 2597 detections, completeness 0.9739, purity 0.7624
2. 5 sigma, 64 px mesh: 1799 detections, completeness 0.9729, purity 0.98
```
A 3σ threshold finds no more bright stars, but it adds about 800 noise peaks. The 64 px mesh still works here only because this moonlight gradient is linear.

## Build it (hardening task)
Replace `background()` in `survey.py` with a mesh background that follows the sky across the frame.

Hints:
- `cal.reshape(b, h // BOX, BOX, w // BOX, BOX)` then `np.median(..., axis=(2, 4))` gives the box medians for the whole stack at once.
- Interpolate between box centres with `np.interp` along rows, then columns. Add one extrapolated virtual box on each side, or the outer 16 px take the edge value.

Check your file: `BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v` (PowerShell: `$env:BUILD_TARGET = "mine"`). Shipped file: `Ran 5 tests ... FAILED (failures=3)`; after the fix: `OK`. Without the variable the tests check `solution/survey.py`.
Reference solution output (`python solution/survey.py`, timings vary):
```
{"option": "A", "frames_per_s": 245.7, "detections": 1808, "completeness": 0.9729, "purity": 0.984, "catalogue_sha": "b51fb7f42583"}
{"option": "B", "frames_per_s": 17.9, "detections": 1808, "completeness": 0.9729, "purity": 0.984, "catalogue_sha": "b51fb7f42583"}
{"option": "C", "frames_per_s": 331.8, "detections": 1808, "completeness": 0.9729, "purity": 0.984, "catalogue_sha": "b51fb7f42583"}
```

## Files
- `survey.py` - main lab code (ships the unfixed `background()`); `solution/survey.py` - the fix
- `survey_sim.py` - seeded night + truth; `pool_worker.py` - spawn-safe pool loader
- `decisions/0001-survey-pipeline-execution.md` - ADR; `test_fitness.py` - fitness function
- `try_it.py`; `test_survey.py` (unit tests + fault reproduction); `test_build_task.py`
- `pipeline_metrics.jsonl` - written by the last run
