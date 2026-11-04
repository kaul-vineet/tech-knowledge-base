# 1. Run the survey pipeline as vectorised batches of 16 frames in one process, with a mesh background

## Status
Accepted (2026-10-29)

## Context
A small survey camera delivers 48 raw 128 × 128 frames per night as float32 bytes. The pipeline must ingest, calibrate (bias, flat), detect and catalogue them. The sky has a moonlight gradient (300 → 900 e⁻ across the frame). Constraints:
- completeness ≥ 0.95 for stars with peak SNR ≥ 10;
- purity ≥ 0.98;
- an identical catalogue however the work is split;
- at least 50 frames/s on one core (the sandbox has 1 CPU), numpy + stdlib only.

`survey.py` (solution) measured three execution options. Throughput is best of 3 runs, which varies between runs:
- A, sequential, one frame per unit: 166–241 frames/s.
- B, spawn process pool (2 workers), one frame per task: 10–19 frames/s. Process start-up and pickling dominate at this frame size.
- C, batches of 16 frames vectorised in one process: about 259 frames/s in three runs.

All three gave the same catalogue (SHA-256 prefix `b51fb7f42583`, 1808 detections), completeness 0.9729 and purity 0.984. The shipped single-level background found only 172 stars (completeness 0.1745). The gradient inflated the robust rms and pushed the 5σ threshold up.

## Decision
Use option C with a SExtractor-style mesh background: 32 × 32 px box medians, bilinear interpolation, and one linearly extrapolated virtual box beyond each edge. Keep `detect()` written for a stack (B, H, W), so the same code runs one frame per unit (A) or inside workers (B) without change. Do not use a process pool until a multi-core measurement shows a speed-up for batch-sized tasks.

## Consequences
- One code path and a deterministic, sorted catalogue. `pipeline_metrics.jsonl` records ingest, calibrate and detect seconds per unit, so a slow stage is visible.
- Memory grows with batch size: 16 frames × 128² × 8 B ≈ 2.1 MB per float64 array. At 4k × 4k the same batch is about 2.1 GB per array, so the batch size must come from a memory budget (scaling limit).
- B stays as the scale-out path: a pool of **batches** on a multi-core host (Mac mini or Windows PC) is pending a CI and manual measurement.
- A linear mesh follows a linear gradient (tryIt 2: 64 px boxes still reach 0.98 purity). A real moon halo or a bright galaxy needs smaller boxes or masking.
- Fitness function: `test_fitness.py` checks completeness ≥ 0.95, purity ≥ 0.98, identical A/B/C catalogues, and C ≥ 50 frames/s (best of 3).
