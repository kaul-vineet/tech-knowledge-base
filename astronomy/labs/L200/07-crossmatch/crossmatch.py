"""L200 Catalogues and cross-matching: angular separation, nearest neighbour with a k-d tree.

Synthetic, seeded catalogues (not real stars): A = 2000 sources around RA 0.5 deg, Dec +28 deg (the field
straddles RA 0/360); B = 90% of A re-measured with 0.2 arcsec scatter + 200 unrelated + 30 blended sources.
python crossmatch.py            # add --export to write cat_a.csv / cat_b.csv (for TOPCAT)
"""
import sys

import numpy as np

from kdtree import KDTree

ARCSEC = np.pi / 180 / 3600


def unit_vectors(ra_deg, dec_deg):
    ra, dec = np.radians(ra_deg), np.radians(dec_deg)
    return np.column_stack([np.cos(dec) * np.cos(ra), np.cos(dec) * np.sin(ra), np.sin(dec)])


def angular_sep(ra1, dec1, ra2, dec2):
    """Vincenty formula (degrees in, degrees out): accurate for tiny and large angles."""
    r1, d1, r2, d2 = map(np.radians, (ra1, dec1, ra2, dec2))
    dra = r2 - r1
    num = np.hypot(np.cos(d2) * np.sin(dra), np.cos(d1) * np.sin(d2) - np.sin(d1) * np.cos(d2) * np.cos(dra))
    return np.degrees(np.arctan2(num, np.sin(d1) * np.sin(d2) + np.cos(d1) * np.cos(d2) * np.cos(dra)))


def make_catalogues(seed=7, n=2000):
    rng = np.random.default_rng(seed)
    ra_a = (0.5 + rng.uniform(-1, 1, n) / np.cos(np.radians(28))) % 360  # wraps: some RA near 359.x
    dec_a = 28 + rng.uniform(-1, 1, n)
    keep = rng.random(n) < 0.9
    jitter = rng.normal(0, 0.2, (2, keep.sum())) / 3600  # 0.2 arcsec per axis
    ra_b = (ra_a[keep] + jitter[0] / np.cos(np.radians(dec_a[keep]))) % 360
    dec_b = dec_a[keep] + jitter[1]
    truth = np.flatnonzero(keep)  # B row i is A row truth[i]
    blend = rng.choice(n, 30, replace=False)  # unrelated faint neighbours 0.3-0.7 arcsec from an A star
    off = rng.uniform(0.3, 0.7, 30) / 3600
    ra_x = np.concatenate([(0.5 + rng.uniform(-1, 1, 200) / np.cos(np.radians(28))) % 360, (ra_a[blend] + off) % 360])
    dec_x = np.concatenate([28 + rng.uniform(-1, 1, 200), dec_a[blend]])
    return (ra_a, dec_a), (np.concatenate([ra_b, ra_x]), np.concatenate([dec_b, dec_x])), truth


def match(cat_a, cat_b, radius_arcsec=1.0):
    """For every B source: index of the nearest A source within the radius (-1 if none) and separation."""
    tree = KDTree(unit_vectors(*cat_a))
    chord_max = 2 * np.sin(radius_arcsec * ARCSEC / 2)  # angle -> straight-line (chord) distance on the unit sphere
    idx, sep = np.full(len(cat_b[0]), -1), np.full(len(cat_b[0]), np.nan)
    for i, q in enumerate(unit_vectors(*cat_b)):
        j, chord = tree.nearest(q)
        if chord <= chord_max:
            idx[i], sep[i] = j, np.degrees(2 * np.arcsin(chord / 2)) * 3600
    return idx, sep, tree.evaluations


def match_one_to_one(cat_a, cat_b, radius_arcsec=1.0):
    # build task: an A source may be claimed by several B sources (blends); keep only the closest claim
    idx, sep, _ = match(cat_a, cat_b, radius_arcsec)
    return idx, sep


def main():
    a, b, truth = make_catalogues()
    idx, sep, evals = match(a, b)
    n_true = len(truth)
    correct = int(np.sum(idx[:n_true] == truth))
    print(f"A {len(a[0])} sources, B {len(b[0])} sources ({n_true} true counterparts); the field wraps: "
          f"{np.sum(a[0] > 180)} sources at RA 359.x deg")
    print(f"matched {np.sum(idx >= 0)} within 1 arcsec; correct {correct}/{n_true}; median sep {np.nanmedian(sep):.3f} arcsec")
    print(f"k-d tree distance evaluations: {evals:,} vs brute force {len(a[0]) * len(b[0]):,}")
    claimed = np.bincount(idx[idx >= 0], minlength=len(a[0]))
    print(f"A sources claimed by more than one B source (blends): {np.sum(claimed > 1)}")
    print(f"RA 359.9999 vs 0.0001 at Dec 28: naive |dRA| = {abs(359.9999 - 0.0001):.4f} deg, "
          f"true separation = {angular_sep(359.9999, 28, 0.0001, 28) * 3600:.4f} arcsec")
    if "--export" in sys.argv:
        for name, (ra, dec) in (("cat_a.csv", a), ("cat_b.csv", b)):
            np.savetxt(name, np.column_stack([ra, dec]), delimiter=",", header="ra,dec", comments="", fmt="%.7f")
        print("wrote cat_a.csv, cat_b.csv")


if __name__ == "__main__":
    main()
