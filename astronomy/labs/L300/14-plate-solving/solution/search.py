"""Stretch solution (lesson 14): when the hint is too far off, search around it instead of giving up.

Try the hint, then hints on rings of 0.4 deg ON THE SKY (RA steps divided by cos Dec) until a solution with at
least 10 matched stars appears. python solution/search.py
"""
import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("platesolve_fixed", HERE / "platesolve.py")
ps = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ps)
fields = ps.fields


def solve_with_search(name, hint, step=0.4, rings=3):
    det, cat = fields.detections(name), fields.catalogue(name)
    tried = 0
    for ring in range(rings + 1):
        n = 1 if ring == 0 else 6 * ring
        for k in range(n):
            ang = 2 * np.pi * k / n
            h = (hint[0] + ring * step * np.cos(ang) / np.cos(np.radians(hint[1])), hint[1] + ring * step * np.sin(ang))
            tried += 1
            sol = ps.solve(det, cat, h)
            if sol is not None and sol["n_matched"] >= 10:
                return ps.check(name, ps.solve(det, cat, sol["crval"])), tried
    return {"field": name, "solved": False}, tried


if __name__ == "__main__":
    f = fields.FIELDS["orion"]
    bad_hint = (f["center"][0] + 0.8, f["center"][1])
    print("plain solve, hint 0.8 deg off:", json.dumps(ps.check("orion", ps.solve(fields.detections("orion"),
                                                                                  fields.catalogue("orion"), bad_hint))))
    result, tried = solve_with_search("orion", bad_hint)
    print(f"search ({tried} hints tried):", json.dumps(result))
