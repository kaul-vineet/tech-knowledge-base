"""Measures the numbers quoted in documentation/HARDWARE.md (peak Python/numpy memory via tracemalloc, wall time).

python research/hardware_measure.py      (stdlib + numpy; same command on macOS and Windows)
"""
import contextlib
import io
import platform
import sys
import time
import tracemalloc
from pathlib import Path

LABS = Path(__file__).resolve().parents[1] / "labs" / "L100"
MAINS = {"02-monte-carlo": "monte_carlo", "03-discrete-event-queue": "des_queue",
         "04-time-stepped-physics": "falling", "05-agent-based-schelling": "schelling",
         "06-verification-validation": "vv"}


def measure(fn):
    tracemalloc.start()
    t0 = time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()):
        fn()
    seconds = time.perf_counter() - t0
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return peak / 2 ** 20, seconds


def main():
    print(f"{platform.system()} {platform.machine()}, Python {platform.python_version()}")
    for folder, module in MAINS.items():
        sys.path.insert(0, str(LABS / folder))
        mod = __import__(module)
        mb, s = measure(mod.main)
        print(f"{folder:<28} peak {mb:7.1f} MiB  wall {s:5.1f} s")
    import numpy as np
    import schelling
    for size in (30, 300, 1000):  # memory of one Schelling 'similarity' pass on a size x size grid
        schelling.SIZE = size
        rng = np.random.default_rng(1)
        mb, s = measure(lambda: schelling.similarity(schelling.make_grid(rng)))
        print(f"Schelling grid {size:>4}x{size:<4} ({size * size:>9,} cells) similarity pass: peak {mb:7.1f} MiB")


if __name__ == "__main__":
    main()
