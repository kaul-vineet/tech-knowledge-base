"""Try it 2: tighten the airmass limit from 2.0 to 1.5 (sharper images, shorter windows).
Predict first: which targets drop out, and does the optimiser's margin over greedy grow or shrink?
python try_it/t2_tighter_airmass.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scheduler  # noqa: E402
import sky  # noqa: E402
import validator  # noqa: E402

for limit in (2.0, 1.5):
    sky.MAX_AIRMASS = limit  # feasibility() and validate() read the module constant at call time
    r = scheduler.build()
    bad = validator.validate(validator.rows_from_blocks(r["local"], r["reqs"], r["slots"]))
    print(f"2. airmass <= {limit}: feasible {sum(bool(row.any()) for row in r['ok'])} | "
          f"greedy {[x['target'] for x in r['greedy_rows']]} {r['greedy_value']:.3f} | "
          f"local {[x['target'] for x in r['local_rows']]} {r['local_value']:.3f} | violations {len(bad)}")
