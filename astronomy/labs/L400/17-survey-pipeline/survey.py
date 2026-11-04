"""L400 survey pipeline: ingest -> calibrate -> detect -> catalogue, three ways to run it, measured.

A sequential per frame | B process pool per frame (spawn, picklable worker) | C vectorised batches of 16 frames.
All three must produce the SAME catalogue; the ADR picks one by throughput and simplicity.
python survey.py   ->  options table, completeness/purity, pipeline_metrics.jsonl (one JSON line per stage/batch)
"""
import hashlib
import json
import multiprocessing as mp
import time
from pathlib import Path

import numpy as np

import pool_worker
import survey_sim as sim

HERE = Path(__file__).resolve().parent
BOX, NSIGMA, BATCH = 32, 5.0, 16


def background(cal):
    """Sky level per pixel for a stack (B, H, W)."""
    return np.broadcast_to(np.median(cal, axis=(1, 2), keepdims=True), cal.shape)  # one level per frame


def detect(cal, bkg):
    """Local maxima above bkg + NSIGMA x robust rms; returns (frame, x, y, flux) sorted - deterministic."""
    resid = cal - bkg
    rms = 1.4826 * np.median(np.abs(resid - np.median(resid, axis=(1, 2), keepdims=True)), axis=(1, 2), keepdims=True)
    p = np.pad(resid, ((0, 0), (1, 1), (1, 1)), constant_values=-np.inf)
    peak = resid > NSIGMA * rms
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy or dx:
                peak &= resid >= p[:, 1 + dy:1 + dy + resid.shape[1], 1 + dx:1 + dx + resid.shape[2]]
    f, y, x = np.nonzero(peak[:, 3:-3, 3:-3])
    y, x = y + 3, x + 3
    win = np.stack([resid[f, y + dy, x + dx] for dy in range(-3, 4) for dx in range(-3, 4)], axis=1)
    offs = np.array([(dy, dx) for dy in range(-3, 4) for dx in range(-3, 4)], float)
    flux = win.sum(axis=1)
    cy, cx = y + (win @ offs[:, 0]) / flux, x + (win @ offs[:, 1]) / flux
    return [(int(a), round(float(b), 2), round(float(c), 2), round(float(d), 1)) for a, b, c, d in zip(f, cx, cy, flux)]


def process(raws, first_frame, bias, flat):
    """One unit of work: a list of raw frames -> catalogue rows (frame index offset by first_frame)."""
    t0 = time.perf_counter()
    stack = np.stack([np.frombuffer(r, dtype="<f4").reshape(sim.SIZE, sim.SIZE) for r in raws]).astype(float)
    t1 = time.perf_counter()
    cal = (stack - bias) / flat  # calibrate: bias, then flat
    t2 = time.perf_counter()
    rows = [(f + first_frame, x, y, fl) for f, x, y, fl in detect(cal, background(cal))]
    t3 = time.perf_counter()
    return rows, {"frames": len(raws), "ingest_s": t1 - t0, "calibrate_s": t2 - t1, "detect_s": t3 - t2}


def run(option, raws, bias, flat, workers=2):
    if option == "A":
        units = [([r], i) for i, r in enumerate(raws)]
    else:
        units = [(raws[i:i + BATCH], i) for i in range(0, len(raws), BATCH)] if option == "C" else \
            [([r], i) for i, r in enumerate(raws)]
    t0 = time.perf_counter()
    if option == "B":
        with mp.get_context("spawn").Pool(workers, initializer=pool_worker.load, initargs=(__file__,)) as pool:
            out = pool.map(pool_worker.work, [(u, i, bias, flat) for u, i in units])
    else:
        out = [process(u, i, bias, flat) for u, i in units]
    wall = time.perf_counter() - t0
    rows = sorted(r for rows, _ in out for r in rows)
    return rows, [m for _, m in out], wall


def score(rows, truth, min_snr=10.0, tol=1.5):
    """Completeness on stars with peak SNR >= min_snr; purity = detections matching ANY true star."""
    by_frame = {}
    for f, x, y, fl in truth:
        by_frame.setdefault(f, []).append((x, y, fl))
    found, bright, good = 0, 0, 0
    for f, stars in by_frame.items():
        det = np.array([(x, y) for g, x, y, _ in rows if g == f]).reshape(-1, 2)
        for x, y, fl in stars:
            hit = det.size and np.min(np.hypot(det[:, 0] - x, det[:, 1] - y)) < tol
            if sim.snr(fl, x) >= min_snr:
                bright += 1
                found += bool(hit)
        st = np.array([(x, y) for x, y, _ in stars])
        good += sum(np.min(np.hypot(st[:, 0] - x, st[:, 1] - y)) < tol for x, y in det)
    return round(found / bright, 4), round(good / max(len(rows), 1), 4)


def checksum(rows):
    return hashlib.sha256(json.dumps(rows).encode()).hexdigest()[:12]


def main(workers=2, log=HERE / "pipeline_metrics.jsonl"):
    raws, bias, flat, truth = sim.night()
    lines, results = [], {}
    for option in ("A", "B", "C"):
        runs = [run(option, raws, bias, flat, workers) for _ in range(1 if option == "B" else 3)]
        rows, metrics, _ = runs[0]
        wall = min(r[2] for r in runs)  # best of 3 (A, C): timing noise only ever adds time
        comp, pur = score(rows, truth)
        results[option] = {"option": option, "frames_per_s": round(len(raws) / wall, 1), "detections": len(rows),
                           "completeness": comp, "purity": pur, "catalogue_sha": checksum(rows)}
        lines += [json.dumps({"option": option, "unit": k, **{a: round(b, 5) if isinstance(b, float) else b
                                                               for a, b in m.items()}}) for k, m in enumerate(metrics)]
    if log:
        Path(log).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return results


if __name__ == "__main__":  # required for the spawn pool on macOS and Windows
    for r in main().values():
        print(json.dumps(r))
