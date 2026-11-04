"""Re-runs every L300 demo, tryIt, buildTask solution and stretch solution and compares with the README code blocks.
Timing lines (lesson 16) are machine-dependent and are skipped. python research/verify_readmes_L300.py
"""
import re
import subprocess
import sys
from pathlib import Path

LABS = Path(__file__).resolve().parents[1] / "labs" / "L300"
RUNS = {"12-variance-reduction": ["variance_reduction.py", "try_it.py", "solution/variance_reduction.py",
                                  "solution/pick_estimator.py"],
        "13-calibration": ["calibrate.py", "try_it.py", "solution/calibrate.py", "solution/param_report.py"],
        "14-global-sensitivity": ["sensitivity.py", "try_it.py", "solution/sensitivity.py", "solution/robust_ranking.py",
                                  "agent_assist.py --fake"],
        "15-cosimulation-fmi": ["cosim.py", "cosim.py 60", "try_it.py", "solution/cosim.py", "solution/guarded_master.py"],
        "16-performance-scale": ["perf.py", "try_it.py", "solution/perf.py", "solution/chunked.py"]}
TIMING = re.compile(r"^\s+(python loop|numpy vectorised|\d+ spawn workers)\s+[\d.]+ s")
strip = lambda text: "\n".join(line for line in text.splitlines() if not TIMING.match(line))
ok = True
for lab, scripts in RUNS.items():
    blocks = [strip(b) for b in re.findall(r"```[a-z]*\n(.*?)\n```", (LABS / lab / "README.md").read_text(encoding="utf-8"), re.S)]
    for script in scripts:
        out = subprocess.run([sys.executable, *script.split()], cwd=LABS / lab, capture_output=True, text=True,
                             encoding="utf-8").stdout.rstrip("\n")
        found = strip(out) in blocks
        ok &= found
        print(f"{lab}/{script}: {'README matches' if found else 'MISMATCH'}")
        if not found:
            print(out)
sys.exit(0 if ok else 1)
