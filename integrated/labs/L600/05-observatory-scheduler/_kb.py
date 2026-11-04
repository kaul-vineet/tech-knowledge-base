"""Puts the source topics' labs on sys.path (pathlib, relative to this file) and loads the reused modules.

Reused, never copied or edited:
  astronomy L300 #12  labs/L300/12-observation-planning/ephem.py          USNO Sun + GMST, Schlyter Moon, altaz, separation
  astronomy L300 #12  labs/L300/12-observation-planning/solution/plan.py  airmass(): Kasten & Young 1989, horizon-safe
  astronomy L100 #3   labs/L100/03-time-systems/timescales.py             JD, TT-UTC, GAST (checked vs Wallace & Capitaine 2006)
  simulation L200 #10 labs/L200/10-warmup-replications/warmup.py          ci(): t-interval over independent replications
  shared              kb/shared/local_agent/                              chat() client + deterministic fake model server
"""
import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # never leave __pycache__ inside the other topics' folders
KB = Path(__file__).resolve().parents[4]
ASTRO_12 = KB / "astronomy" / "labs" / "L300" / "12-observation-planning"
ASTRO_03 = KB / "astronomy" / "labs" / "L100" / "03-time-systems"
SIM_10 = KB / "simulation" / "labs" / "L200" / "10-warmup-replications"
SHARED = KB / "shared"

for p in (ASTRO_12, ASTRO_03, SIM_10, SHARED):
    if str(p) not in sys.path:
        sys.path.append(str(p))

import ephem  # noqa: E402  (astronomy's ephem.py, not the PyPI package of the same name)
import timescales  # noqa: E402
import warmup  # noqa: E402
from local_agent import client as agent_client  # noqa: E402
from local_agent import fake_model_server  # noqa: E402


def _load(name, path):
    """Load a file under a unique module name so 'plan' never clashes with anything of ours."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


astro_plan = _load("astro12_solution_plan", ASTRO_12 / "solution" / "plan.py")
