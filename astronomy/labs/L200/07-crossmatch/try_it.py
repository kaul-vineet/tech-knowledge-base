"""tryIt experiments for lesson 7 (run: python try_it.py)."""
import numpy as np

import crossmatch as cm
from kdtree import KDTree

a, b, truth = cm.make_catalogues()

# 1. Change the match radius. Predict: more matches with 3 arcsec - are they better?
for r in (0.5, 1.0, 3.0):
    idx, sep, _ = cm.match(a, b, r)
    print(f"radius {r} arcsec: matched {np.sum(idx >= 0)}, correct {int(np.sum(idx[:len(truth)] == truth))}/{len(truth)}")

# 2. Change the leaf size of the tree. Predict: fewer or more distance evaluations?
q = cm.unit_vectors(*b)
for leaf in (4, 16, 256):
    tree = KDTree(cm.unit_vectors(*a), leaf_size=leaf)
    for v in q:
        tree.nearest(v)
    print(f"leaf size {leaf:>3}: {tree.evaluations:,} distance evaluations")
