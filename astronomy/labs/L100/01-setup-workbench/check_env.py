"""Setup check for the astronomy workbench: interpreter, pinned libraries, offline data folders, a seeded sky.

python check_env.py
"""
import importlib.metadata as md
import platform
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data"  # labs/data: raw (never edited), cache (safe to delete), derived (re-creatable)
FOLDERS = ("raw", "cache", "derived")


def parse_pins(text):
    # splitlines + strip: the file may have Windows CRLF line endings after a git checkout
    return dict(line.strip().split("==") for line in text.splitlines() if line.strip() and not line.startswith("#"))


PINS = parse_pins((HERE / "requirements.txt").read_text(encoding="utf-8"))


def installed(pkg):
    try:
        return md.version(pkg)
    except md.PackageNotFoundError:
        return None


def make_folders(root=DATA):
    for name in FOLDERS:
        (root / name).mkdir(parents=True, exist_ok=True)  # offline-first: every lab reads/writes here, no network
    return [str((root / n).relative_to(root.parent)) for n in FOLDERS]


def synthetic_stars(seed, n=3):
    import numpy as np
    rng = np.random.default_rng(seed)  # seeded: the same "random" star field on every machine
    ra = rng.uniform(0, 360, n).round(4)
    mag = rng.uniform(2, 12, n).round(2)
    return list(zip(ra.tolist(), mag.tolist()))


def main():
    print(f"Python {platform.python_version()} on {platform.system()} {platform.machine()}")
    ok = sys.version_info >= (3, 12)
    for pkg, pin in PINS.items():
        have = installed(pkg)
        where = "local" if pkg == "numpy" else "CI"
        status = f"installed {have}" + ("" if have == pin else f" (pin {pin})") if have else f"not installed -> runs in {where}"
        print(f"  {pkg:<9} pin {pin:<7} {status}")
        ok &= bool(have) or pkg != "numpy"  # numpy is the only package the local labs need
    print("data folders:", ", ".join(make_folders()))
    print("seed 42 stars (RA deg, mag):", synthetic_stars(42))
    print("READY for local labs" if ok else "NOT READY: need Python 3.12+ and numpy")


if __name__ == "__main__":
    main()
