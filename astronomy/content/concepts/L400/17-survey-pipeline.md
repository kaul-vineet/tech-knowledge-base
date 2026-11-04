**Concept: survey pipeline architecture - stages, units of work, and measuring before you parallelise**

## Why it matters
A survey camera never stops. ZTF reads out 64 CCD quadrants per exposure, runs nine pipelines, and has a 20-minute requirement from shutter to alert (Masci et al. 2019). Your own small survey, a robotic telescope on a roof in Gurgaon or a shared instrument, has the same shape at a smaller scale. Frames arrive as bytes, they must be calibrated, sources found and catalogued, and the night must finish before the next one starts. Two decisions dominate: how to cut the work into units, and how to make every stage correct on every frame, not just on the easy ones.

## Mental model
A pipeline is a conveyor belt of pure stages. Correctness lives inside the stages; throughput lives in how you feed the belt.

```
bytes --> ingest --> calibrate (bias, flat) --> background --> detect --> catalogue (sorted, hashed)
           |                                                                    |
   unit of work: 1 frame (A) | 1 frame per process (B) | 16-frame batch (C)    +--> pipeline_metrics.jsonl
```

If every stage is a function of its input only, then A, B and C must produce the **same catalogue**. That property can be tested, and it is the first fitness check.

## Design space
- **Unit of work.** One frame per call is simple and has low memory, but per-call overhead is paid on every frame. A batch per call amortises overhead and suits numpy vectorisation, but memory grows with the batch. A process per unit uses many cores, but pays process start-up and pickles every frame.
- **Background model.** One level per frame is cheap and fails with any gradient (moonlight, twilight, scattered light). A mesh of box medians with interpolation (SExtractor, photutils `Background2D`) follows the sky; the box size trades fidelity against stars biasing the median.
- **Determinism.** A catalogue sorted by (frame, x, y) with a content hash lets you compare runs, options and machines.
- **Observability.** Per-unit stage timings as JSON lines tell you which stage to optimise before you buy cores.

## How to decide
Write the constraints first, then measure every option on the same seeded night. The constraints here: completeness ≥ 0.95 for stars with peak SNR ≥ 10, purity ≥ 0.98, an identical catalogue regardless of split, and at least 50 frames/s on one core.

**Worked example (lab run, 48 frames of 128 × 128, 1 CPU):**
- With one background level per frame, the moonlight gradient (300 → 900 e⁻) inflates the robust rms. Only 172 stars are found (completeness 0.1745), and purity is a perfect 1.0, which hides the failure.
- The 32 px mesh with bilinear interpolation and an extrapolated edge box finds 1808 detections, with completeness 0.9729 and purity 0.984. The catalogue hash `b51fb7f42583` is the same for A, B and C.
- Throughput, best of 3: A 166–241 frames/s, B 10–19 (spawn start-up and pickling dominate at this frame size), C about 259.

The ADR chooses C and keeps `detect()` written for a stack, so B remains a later scale-out path. `test_fitness.py` guards all four constraints.

## Failure modes at scale
- **Memory per batch:** 16 frames × 128² × 8 B ≈ 2 MB here, but about 2 GB per array at 4k × 4k. Derive the batch size from a memory budget, and watch the resident set size.
- **Pool overhead and order:** spawn workers re-import modules (macOS and Windows default). Without a sort, completion order changes the catalogue. A changing catalogue hash between runs is the signal.
- **Background structure finer than the mesh:** a moon halo or a bright galaxy biases the boxes. Completeness drops near bright sources first, so monitor completeness in radial bins.
- **Thresholds versus noise peaks:** a 3σ threshold finds no more bright stars but adds about 800 noise peaks (purity 0.7624). Purity per night is the alarm.

## Common mistakes
- Parallelising before measuring. On one core the process pool here is about 13–25 times slower than batched C.
- Judging detection by purity alone. A threshold that is too high has perfect purity and terrible completeness.
- Letting the work split change the output: unsorted results, per-worker random seeds, or float order effects.
