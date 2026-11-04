"""Run every L100, L200, L300 and L400 lab's unit tests (incl. the capstone) against the stub, one
process per lab, plus the shared L400 helpers, the vendored local-agent tests (fake model server only)
and the L500 theorem checks (labs/L500/*; these need numpy).
L400 labs take about 1 minute each (they load seven stub boards per run).

Usage (from the domain root):  python3 labs/run_tests.py   (Windows: py labs\run_tests.py)
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
suites = [p for level in ("L100", "L200", "L300", "L400", "L500") for p in sorted((ROOT / level).iterdir())
          if p.is_dir() and not p.name.startswith(("_", "."))]
suites += [ROOT / "L400" / "_edge", ROOT / "_shared" / "local_agent"]
failed = []
for lab in suites:
    print("==", lab.name, flush=True)
    r = subprocess.run([sys.executable, "-m", "unittest", "-v"], cwd=lab)  # same interpreter on every OS
    if r.returncode:
        failed.append(lab.name)
print("FAILED: %s" % failed if failed else "ALL LABS PASSED")
sys.exit(1 if failed else 0)
