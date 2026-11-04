"""Numbers quoted in the L400 concept notes (content/concepts/L400/*.md) - re-run them here.

Runs each lab's measuring script from its own folder and prints its output unchanged.
Run from the domain root:  python3 research/concept_examples_l400.py > research/concept_examples_l400.out.txt
(about 5 minutes; Windows: py research\\concept_examples_l400.py)
"""
import subprocess
import sys
from pathlib import Path

L400 = Path(__file__).resolve().parent.parent / "labs" / "L400"
RUNS = [("17-edge-to-cloud", ["options.py"]), ("17-edge-to-cloud", ["try_it.py"]),
        ("18-fleet-config", ["fleet_sim.py"]), ("18-fleet-config", ["try_it.py"]),
        ("19-radio-auth", ["attacks.py"]), ("19-radio-auth", ["try_it.py"]),
        ("20-digital-twin", ["drift_eval.py"]), ("20-digital-twin", ["try_it.py"]),
        ("21-edge-ai-explain", ["options.py"]), ("21-edge-ai-explain", ["try_it.py"]),
        ("22-capstone", ["run_capstone.py"])]

if __name__ == "__main__":
    for lab, args in RUNS:
        print("== %s: %s" % (lab, " ".join(args)), flush=True)
        r = subprocess.run([sys.executable] + args, cwd=L400 / lab, capture_output=True, text=True, encoding="utf-8")
        print(r.stdout.rstrip(), flush=True)
