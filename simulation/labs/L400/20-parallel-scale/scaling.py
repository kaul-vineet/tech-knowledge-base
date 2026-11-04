"""Scaling measurement for the sweep: tasks per second vs worker count and chunk size (machine-dependent).

Fits Amdahl's law S(n) = 1 / (f + (1 - f) / n) to the measured speed-ups to estimate the serial fraction f.
python scaling.py      (sandbox: 1 CPU, so expect speed-ups below 1; run it on the Mac mini / Windows PC)
"""
import os
import tempfile
import time
from pathlib import Path

import numpy as np

import sweep


def measure(workers, chunksize):
    with tempfile.TemporaryDirectory() as tmp:
        start = time.perf_counter()
        sweep.run_sweep(Path(tmp) / "s.db", workers, chunksize=chunksize)
        return len(sweep.all_tasks()) / (time.perf_counter() - start)


def amdahl_serial_fraction(workers, speedups):
    """Least-squares f from 1/S = f + (1 - f)/n  ->  (1/S - 1/n) = f (1 - 1/n)."""
    n, s = np.asarray(workers, float), np.asarray(speedups, float)
    x, y = 1 - 1 / n, 1 / s - 1 / n
    return float(np.clip((x @ y) / (x @ x), 0, 1)) if (x @ x) > 0 else 1.0


if __name__ == "__main__":
    print(f"os.cpu_count() = {os.cpu_count()}")
    workers = [w for w in (1, 2, 4) if w <= max(2, os.cpu_count() or 1) * 2]
    base = None
    speedups = []
    for w in workers:
        for chunk in (1, 8):
            rate = measure(w, chunk)
            base = base or rate
            if chunk == 8:
                speedups.append(rate / base)
            print(f"workers {w} chunksize {chunk}: {rate:6.1f} tasks/s  (speed-up x{rate / base:.2f})")
    print(f"Amdahl serial fraction estimate (chunksize 8): f = {amdahl_serial_fraction(workers, speedups):.2f}")
