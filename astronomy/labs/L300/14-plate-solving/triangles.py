"""Triangle matching for lesson 14 (Groth 1986 / astroalign idea): shape invariants, votes, RANSAC, affine fit.

Invariants (L2/L1, L1/L0) with L2 >= L1 >= L0 do not change under shift, rotation, scale or mirror image.
"""
from itertools import combinations

import numpy as np

import fields

N_IMG, N_CAT, TOL, MATCH_ARCSEC = 12, 40, 0.008, 6.0


def triangles(xy, n):
    """All triangles of the n first points: invariants + vertices ordered by the side opposite them."""
    inv, verts = [], []
    for tri in combinations(range(min(n, len(xy))), 3):
        p = xy[list(tri)]
        sides = [np.linalg.norm(p[1] - p[2]), np.linalg.norm(p[0] - p[2]), np.linalg.norm(p[0] - p[1])]
        order = np.argsort(sides)  # vertex opposite the shortest side first
        L0, L1, L2 = np.array(sides)[order]
        inv.append((L2 / L1, L1 / L0))
        verts.append(np.array(tri)[order])
    return np.array(inv), np.array(verts)


def vote(img_xy, cat_xy):
    """Triangle pairs with matching invariants vote for star correspondences (image index -> catalogue index)."""
    if len(img_xy) < 3 or len(cat_xy) < 3:  # nothing to match (hint far off the catalogue)
        return {}
    inv_i, v_i = triangles(img_xy, N_IMG)
    inv_c, v_c = triangles(cat_xy, N_CAT)
    close = np.argwhere(np.max(np.abs(inv_i[:, None, :] - inv_c[None, :, :]) / inv_c[None, :, :], axis=2) < TOL)
    votes = {}
    for a, b in close:
        for i, c in zip(v_i[a], v_c[b]):
            votes[(i, c)] = votes.get((i, c), 0) + 1
    best = {}
    for (i, c), n in sorted(votes.items(), key=lambda kv: -kv[1]):
        if n >= 2 and i not in best and c not in best.values():
            best[i] = c
    return best


def fit_affine(px, plane):
    """plane = A @ [x - CRPIX, y - CRPIX, 1]; A[:, :2] is the CD matrix (deg/px), A[:, 2] the plane offset."""
    M = np.column_stack([px[:, 0] - fields.CRPIX, px[:, 1] - fields.CRPIX, np.ones(len(px))])
    A, *_ = np.linalg.lstsq(M, plane, rcond=None)
    return A.T, M


def consensus(img_xy, cat_xy, i_idx, c_idx):
    """RANSAC, exhaustively: every 3 voted pairs define an affine map; keep the map most voted pairs agree with
    (within MATCH_ARCSEC). Wrong pairs from spurious detections cannot outvote the geometry."""
    best = np.array([], dtype=int)
    for trio in combinations(range(len(i_idx)), 3):
        A, _ = fit_affine(img_xy[i_idx[list(trio)]], cat_xy[c_idx[list(trio)]])
        M = np.column_stack([img_xy[i_idx, 0] - fields.CRPIX, img_xy[i_idx, 1] - fields.CRPIX, np.ones(len(i_idx))])
        inliers = np.flatnonzero(np.hypot(*(M @ A.T - cat_xy[c_idx]).T) * 3600 < MATCH_ARCSEC)
        if len(inliers) > len(best):
            best = inliers
    return i_idx[best], c_idx[best]
