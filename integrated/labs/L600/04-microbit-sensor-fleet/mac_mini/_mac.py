"""Paths for this project's Mac mini scripts: puts the lab folder on sys.path and loads the track's mac_profile.py
(integrated/mac-mini/scripts, owned by the Mac mini track) by file path, so RAM maths is computed there, never copied."""
import importlib.util
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
INTEGRATED = HERE.parents[3]
PROFILE = INTEGRATED / "mac-mini" / "scripts" / "mac_profile.py"
if str(LAB) not in sys.path:
    sys.path.insert(0, str(LAB))


def mac_profile():
    if "kb_mac_profile" not in sys.modules:
        spec = importlib.util.spec_from_file_location("kb_mac_profile", PROFILE)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["kb_mac_profile"] = mod
        spec.loader.exec_module(mod)
    return sys.modules["kb_mac_profile"]


def profile(ram_gib=None):
    """mac_profile.profile(): detected machine, or a simulated RAM size (GiB, as Apple sells it)."""
    return mac_profile().profile(ram_gib)


def emit(row, out=None):
    """Print one JSON line; with out= also append it to a JSONL file (the nightly runner collects these)."""
    line = json.dumps(row)
    print(line, flush=True)
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def stamp():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")
