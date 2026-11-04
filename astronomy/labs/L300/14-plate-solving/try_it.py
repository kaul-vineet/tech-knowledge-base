"""tryIt for lesson 14.
1. How much does the shipped flat RA/Dec projection distort a triangle at Dec -5 vs Dec +62?
2. Fixed solver: loosen the invariant tolerance TOL from 0.008 to 0.05 - more votes, or more wrong votes?
"""
import importlib.util
from pathlib import Path

import numpy as np

import fields
import triangles

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("platesolve_fixed", HERE / "solution" / "platesolve.py")
fixed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixed)

if __name__ == "__main__":
    for name in fields.FIELDS:
        ra0, dec0 = fields.FIELDS[name]["center"]
        tri_ra, tri_dec = ra0 + np.array([0.0, 0.2, 0.05]), dec0 + np.array([0.0, 0.03, 0.18])
        flat = triangles.triangles(np.column_stack([tri_ra - ra0, tri_dec - dec0]), 3)[0][0]
        tan = triangles.triangles(np.column_stack(fields.tan_project(tri_ra, tri_dec, ra0, dec0)), 3)[0][0]
        print(f"1. {name:10s} Dec {dec0:+.1f}: invariants flat {flat.round(3)} vs TAN {tan.round(3)} "
              f"(max relative difference {np.max(np.abs(flat - tan) / tan):.3f}; match tolerance {triangles.TOL})")
    triangles.TOL = 0.05
    f = fields.FIELDS["cassiopeia"]
    hint = (f["center"][0] + fields.HINT_ERROR_DEG[0], f["center"][1] + fields.HINT_ERROR_DEG[1])
    det, cat = fields.detections("cassiopeia"), fields.catalogue("cassiopeia")
    near = np.hypot((cat["ra"] - hint[0]) * np.cos(np.radians(hint[1])), cat["dec"] - hint[1]) < fixed.SEARCH_DEG
    order = np.argsort(cat["mag"][near])
    cat_xy = np.column_stack(fields.tan_project(cat["ra"][near][order], cat["dec"][near][order], *hint))
    img_xy = np.column_stack([det["x"], det["y"]])[np.argsort(det["mag"])]
    for tol in (0.008, 0.05):
        triangles.TOL = tol
        pairs = triangles.vote(img_xy, cat_xy)
        i_idx, c_idx = triangles.consensus(img_xy, cat_xy, np.array(list(pairs)), np.array(list(pairs.values())))
        print(f"2. TOL {tol}: {len(pairs)} voted pairs, {len(i_idx)} agree with the best geometry")
