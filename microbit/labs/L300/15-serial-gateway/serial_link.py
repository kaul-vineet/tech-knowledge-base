"""Seeded serial-link faults between the stub device and the gateway (CPython only).

device_bytes(n): what main.py prints for n readings (stub, temperature/light from a
fixed pattern), as bytes with "\\r\\n" line ends like the board's USB serial.
noisy(data, seed): the failureLab fault. Adds boot garbage before the first frame,
then per frame (seeded): drop one byte (2%), flip one bit (2%), cut the line short
and lose its line end (1%, a cable pulled mid-line). Returns the bytes in random-sized
chunks, as a serial port read() would.
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_lab, serial  # noqa: E402
import microbit  # noqa: E402

BOOT = b"\x00\xff\xfeMicroPython v2 boot\r\n"
FAULTS = dict(drop=0.02, flip=0.02, cut=0.01, seed=15)


def device_bytes(n=200):
    lab = load_lab(HERE)
    state = lab.new_state()
    with serial() as out:
        for i in range(n):
            microbit._inject_temperature(20 + (i // 50))       # 20, 21, 22, 23
            microbit.display.inject_light_level(100 + (i % 10))
            lab.step(state)
            microbit.sleep(lab.PERIOD_MS)
    return out.getvalue().replace("\n", "\r\n").encode("ascii")


def noisy(data, drop=0.02, flip=0.02, cut=0.01, seed=15):
    rng = random.Random(seed)
    lines = data.split(b"\r\n")
    out = bytearray(BOOT)
    stats = {"dropped": 0, "flipped": 0, "cut": 0}
    for line in lines:
        if not line:
            continue
        line = bytearray(line)
        if rng.random() < drop:
            del line[rng.randrange(len(line))]
            stats["dropped"] += 1
        if rng.random() < flip:
            i = rng.randrange(1, len(line))
            line[i] ^= 1 << rng.randrange(7)
            stats["flipped"] += 1
        if rng.random() < cut:
            out += line[: rng.randrange(2, len(line))]       # no line end: merges with the next
            stats["cut"] += 1
            continue
        out += line + b"\r\n"
    chunks, i = [], 0
    while i < len(out):
        n = rng.randrange(1, 40)
        chunks.append(bytes(out[i:i + n]))
        i += n
    return chunks, stats


def as_text_lines(chunks):
    """What the naive gateway sees when it reads the port as text lines."""
    text = b"".join(chunks).decode("utf-8", errors="replace")
    return text.splitlines(keepends=True)


if __name__ == "__main__":
    # Write sample transcripts next to this file: samples/clean.txt and samples/noisy.bin
    from pathlib import Path
    out = Path(HERE) / "samples"
    out.mkdir(exist_ok=True)
    clean = device_bytes()
    (out / "clean.txt").write_bytes(clean)
    chunks, stats = noisy(clean, **FAULTS)
    (out / "noisy.bin").write_bytes(b"".join(chunks))
    print("wrote samples/clean.txt (%d bytes) and samples/noisy.bin (%d bytes); faults %s"
          % (len(clean), sum(map(len, chunks)), stats))
