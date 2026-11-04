"""Setup check for the simulation workbench: what is installed, and is randomness reproducible?

python check_env.py
"""
import importlib.metadata as md
import os
import platform
import sys
from pathlib import Path


def parse_pins(text):
    # splitlines + strip: the file may have Windows CRLF line endings after a git checkout
    return dict(line.strip().split("==") for line in text.splitlines() if line.strip() and not line.startswith("#"))


PINS = parse_pins(Path(__file__).with_name("requirements.txt").read_text(encoding="utf-8"))


def installed(pkg):
    try:
        return md.version(pkg)
    except md.PackageNotFoundError:
        return None


def seeded_draws(seed):
    import numpy as np
    return np.random.default_rng(seed).random(3).round(6).tolist()  # same seed -> same numbers, every run


def main():
    # machine: arm64 = Apple-silicon Mac, AMD64 = x64 Windows, x86_64 = Intel/AMD Linux or Mac
    print(f"Python {platform.python_version()} on {platform.system()} {platform.machine()} | CPU cores: {os.cpu_count()}")
    ok = sys.version_info >= (3, 12)
    for pkg, pin in PINS.items():
        have = installed(pkg)
        where = "local" if pkg == "numpy" else "CI"
        status = f"installed {have}" + ("" if have == pin else f" (pin {pin})") if have else f"not installed -> runs in {where}"
        print(f"  {pkg:<6} pin {pin:<7} {status}")
        ok &= bool(have) or pkg != "numpy"  # numpy is the only package the local labs need
    print("seed 42 ->", seeded_draws(42))
    print("seed 42 ->", seeded_draws(42), "(identical = reproducible)")
    print("READY for local labs" if ok else "NOT READY: need Python 3.12+ and numpy")


if __name__ == "__main__":
    main()
