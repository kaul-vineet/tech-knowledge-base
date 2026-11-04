"""Small k-d tree on 3-D unit vectors (numpy + recursion), with a counter of distance evaluations."""
import numpy as np


class KDTree:
    def __init__(self, points, leaf_size=16):
        self.p = np.asarray(points, dtype=float)
        self.leaf_size = leaf_size
        self.root = self._build(np.arange(len(self.p)), 0)
        self.evaluations = 0  # how many point-to-point distances queries computed

    def _build(self, idx, depth):
        if len(idx) <= self.leaf_size:
            return ("leaf", idx)
        axis = depth % 3
        order = idx[np.argsort(self.p[idx, axis], kind="stable")]
        mid = len(order) // 2
        split = self.p[order[mid], axis]
        return ("node", axis, split, self._build(order[:mid], depth + 1), self._build(order[mid:], depth + 1))

    def nearest(self, q):
        best = [np.inf, -1]
        self._search(self.root, np.asarray(q, dtype=float), best)
        return best[1], best[0]  # (index, chord distance)

    def _search(self, node, q, best):
        if node[0] == "leaf":
            d = np.sqrt(((self.p[node[1]] - q) ** 2).sum(axis=1))
            self.evaluations += len(d)
            i = int(np.argmin(d))
            if d[i] < best[0]:
                best[0], best[1] = float(d[i]), int(node[1][i])
            return
        _, axis, split, left, right = node
        near, far = (left, right) if q[axis] < split else (right, left)
        self._search(near, q, best)
        if abs(q[axis] - split) < best[0]:  # prune: the far side can only help if the splitting plane is closer
            self._search(far, q, best)
