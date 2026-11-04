"""L300 plate solving (astrometry-lite): match star triangles to a catalogue, fit a TAN WCS, report residuals.

1. Project catalogue stars near the rough pointing (the hint) onto a plane around the hint.
2. Triangles of the brightest stars on both sides; invariants (L2/L1, L1/L0) do not change with shift, rotation
   or scale, so matching invariants proposes star pairs (astroalign / Groth); pairs vote.
3. Least-squares affine fit pixel -> plane (a CD matrix + reference point), refined on all stars with clipping.
python solution/platesolve.py    (solves the 'orion' and 'cassiopeia' fields)
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # fields.py lives in the lab folder
import fields  # noqa: E402
import triangles  # noqa: E402

SEARCH_DEG = 0.6  # catalogue stars used: within 0.6 deg of the hint


def to_plane(ra, dec, ra0, dec0):
    """Catalogue -> plane: the gnomonic (TAN) projection a camera makes. A degree of RA spans cos(Dec) degrees
    on the sky (0.47 at Dec +62), so raw RA/Dec offsets distort every triangle away from the equator."""
    return fields.tan_project(ra, dec, ra0, dec0)


def from_plane(xi, eta, ra0, dec0):
    return fields.tan_deproject(xi, eta, ra0, dec0)


def solve(det, cat, hint):
    """Returns a WCS dict (crval, cd), residuals in arcsec, and the number of matched stars - or None."""
    ra0, dec0 = hint
    near = np.hypot((cat["ra"] - ra0) * np.cos(np.radians(dec0)), cat["dec"] - dec0) < SEARCH_DEG
    order_c = np.argsort(cat["mag"][near])
    c_ra, c_dec = cat["ra"][near][order_c], cat["dec"][near][order_c]
    cat_xy = np.column_stack(to_plane(c_ra, c_dec, ra0, dec0))
    order_i = np.argsort(det["mag"])
    img_xy = np.column_stack([det["x"], det["y"]])[order_i]
    pairs = triangles.vote(img_xy, cat_xy)
    if len(pairs) < 4:
        return None
    i_idx, c_idx = triangles.consensus(img_xy, cat_xy, np.array(list(pairs)), np.array(list(pairs.values())))
    for _ in range(5):  # refine: transform ALL detections, re-match by nearest neighbour, clip, refit
        A, _ = triangles.fit_affine(img_xy[i_idx], cat_xy[c_idx])
        M = np.column_stack([img_xy[:, 0] - fields.CRPIX, img_xy[:, 1] - fields.CRPIX, np.ones(len(img_xy))])
        pred = M @ A.T
        d = np.hypot(*(pred[:, None, :] - cat_xy[None, :, :]).transpose(2, 0, 1)) * 3600
        nearest, dist = d.argmin(axis=1), d.min(axis=1)
        ok = dist < triangles.MATCH_ARCSEC
        if ok.sum() < 4:
            return None
        i_idx, c_idx = np.flatnonzero(ok), nearest[ok]
    A, M = triangles.fit_affine(img_xy[i_idx], cat_xy[c_idx])
    res = (M @ A.T - cat_xy[c_idx]) * 3600
    crval = from_plane(A[0, 2], A[1, 2], ra0, dec0)  # sky position of the reference pixel CRPIX
    return {"crval": (float(crval[0]), float(crval[1])), "cd": A[:, :2], "n_matched": int(len(i_idx)),
            "rms_arcsec": float(np.sqrt((res ** 2).sum(axis=1).mean())), "residuals": res}


def check(name, sol):
    """Compare a solution with the field's truth: pointing error (arcsec), scale (arcsec/px), rotation (deg)."""
    f = fields.FIELDS[name]
    if sol is None:
        return {"field": name, "solved": False}
    ra, dec = sol["crval"]
    err = np.hypot((ra - f["center"][0]) * np.cos(np.radians(dec)), dec - f["center"][1]) * 3600
    cd = sol["cd"]
    scale = np.sqrt(abs(np.linalg.det(cd))) * 3600
    rot = np.degrees(np.arctan2(cd[1, 0], cd[1, 1]))
    return {"field": name, "solved": True, "n_matched": sol["n_matched"], "rms_arcsec": round(sol["rms_arcsec"], 3),
            "pointing_error_arcsec": round(float(err), 2), "scale_arcsec_px": round(float(scale), 4),
            "rotation_deg": round(float(rot), 3)}


def run(name):
    f = fields.FIELDS[name]
    hint = (f["center"][0] + fields.HINT_ERROR_DEG[0], f["center"][1] + fields.HINT_ERROR_DEG[1])
    det, cat = fields.detections(name), fields.catalogue(name)
    sol = solve(det, cat, hint)
    if sol is not None:  # second pass with the tangent point at the solved center: CD then refers to north THERE
        sol = solve(det, cat, sol["crval"])
    return check(name, sol)


if __name__ == "__main__":
    import json
    for field in fields.FIELDS:
        print(json.dumps(run(field)))
