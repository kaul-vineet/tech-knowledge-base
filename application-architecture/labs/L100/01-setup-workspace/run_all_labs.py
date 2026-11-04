"""Run `python -m unittest discover` inside every L100 lab folder; exit 1 if any fails."""
import pathlib
import subprocess
import sys

LABS_DIR = pathlib.Path(__file__).resolve().parent.parent


def main():
    failed = []
    for lab in sorted(p for p in LABS_DIR.iterdir() if p.is_dir() and p.name[:2].isdigit()):
        # Each lab is run from its own folder so its modules import without packaging.
        result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-q"],
                                cwd=lab, capture_output=True, text=True, encoding="utf-8")
        summary = (result.stderr.strip().splitlines() or ["(no output)"])[-1]
        print(f"{lab.name:<30} {summary}")
        if result.returncode != 0:
            failed.append(lab.name)
    print("ALL LABS PASSED" if not failed else f"FAILED: {', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
