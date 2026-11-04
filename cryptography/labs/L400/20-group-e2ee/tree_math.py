"""Perfect binary tree in heap order (root = 1, children of x are 2x and 2x+1, leaf i of n is node n + i).
RFC 9420 uses a different array layout (Appendix C); the relations - direct path, copath, resolution - are the same."""


def leaf(n: int, i: int) -> int:
    return n + i


def direct_path(x: int) -> list:
    out = []
    while x > 1:
        x //= 2
        out.append(x)  # parent, grandparent, ..., root
    return out


def copath(x: int) -> list:
    out = []
    while x > 1:
        out.append(x ^ 1)  # sibling of x, then sibling of each ancestor below the root
        x //= 2
    return out


def resolution(nodes: dict, x: int, n: int) -> list:
    """Smallest set of non-blank nodes that covers every non-blank leaf under x (RFC 9420 section 4.1.1)."""
    if nodes.get(x) is not None:
        return [x]
    if x >= n:  # a blank leaf covers nobody
        return []
    return resolution(nodes, 2 * x, n) + resolution(nodes, 2 * x + 1, n)
