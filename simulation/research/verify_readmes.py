"""Re-runs every lab demo + try_it.py and compares with the README code blocks (python research/verify_readmes.py)."""
import re
import subprocess
import sys
from pathlib import Path

LABS = Path(__file__).resolve().parents[1] / "labs" / "L100"
DEMOS = {"01-setup-workbench": "check_env.py", "02-monte-carlo": "monte_carlo.py", "03-discrete-event-queue": "des_queue.py",
         "04-time-stepped-physics": "falling.py", "05-agent-based-schelling": "schelling.py", "06-verification-validation": "vv.py"}
ok = True
for lab, demo in DEMOS.items():
    readme = (LABS / lab / "README.md").read_text(encoding="utf-8")
    blocks = re.findall(r"```[a-z]*\n(.*?)\n```", readme, re.S)
    for script in (demo, "try_it.py") + (("agent_assist.py",) if lab.startswith("06") else ()):
        args = [sys.executable, script] + (["--fake"] if script == "agent_assist.py" else [])
        out = subprocess.run(args, cwd=LABS / lab, capture_output=True, text=True, encoding="utf-8").stdout.rstrip("\n")
        found = out in blocks
        ok &= found
        print(f"{lab}/{script}: {'README matches' if found else 'MISMATCH'}")
        if not found:
            print(out)
sys.exit(0 if ok else 1)
