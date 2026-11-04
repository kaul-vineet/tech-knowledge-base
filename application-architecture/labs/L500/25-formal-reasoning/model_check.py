"""Lesson 25 - explicit-state model checking of a tiny loan workflow (one book, N members), stdlib only.

A state is (pcs, loans): pcs[i] is member i's step, loans the set of members holding an active loan of the book.
Each member:  idle --read: book looks free--> checked --borrow--> holding --return--> idle
  buggy  : 'borrow' inserts a loan row unconditionally (check-then-act on a stale read)
  fixed  : 'borrow' is one atomic conditional insert (unique constraint / compare-and-set); if the book is
           taken meanwhile the member goes back to idle.
Safety property: at most one active loan of the book (len(loans) <= 1).
"""
from collections import deque

MEMBERS = ("A", "B")


def initial(members=MEMBERS):
    return tuple("idle" for _ in members), frozenset()


def successors(state, fixed, members=MEMBERS):
    pcs, loans = state
    for i, m in enumerate(members):
        pc = pcs[i]
        if pc == "idle" and not loans:
            yield f"{m} reads: book free", (_set(pcs, i, "checked"), loans)
        elif pc == "checked":
            if not fixed or not loans:
                yield f"{m} borrows", (_set(pcs, i, "holding"), loans | {m})
            else:
                yield f"{m} borrow rejected (book taken)", (_set(pcs, i, "idle"), loans)
        elif pc == "holding":
            yield f"{m} returns", (_set(pcs, i, "idle"), loans - {m})


def _set(pcs, i, pc):
    return pcs[:i] + (pc,) + pcs[i + 1:]


def safe(state):
    return len(state[1]) <= 1


def bfs(fixed, prop=safe, members=MEMBERS):
    """Breadth-first search of every reachable state. Returns (states explored, shortest counterexample or None,
    deadlocked states, parent map)."""
    start = initial(members)
    parent, queue, deadlocks = {start: None}, deque([start]), []
    while queue:
        state = queue.popleft()
        if not prop(state):
            return len(parent), trace(parent, state), deadlocks, parent
        moves = list(successors(state, fixed, members))
        if not moves:
            deadlocks.append(state)
        for label, nxt in moves:
            if nxt not in parent:
                parent[nxt] = (state, label)
                queue.append(nxt)
    return len(parent), None, deadlocks, parent


def reachable_states(fixed, members=MEMBERS):
    return bfs(fixed, prop=lambda s: True, members=members)[0]


def trace(parent, state):
    steps = []
    while parent[state] is not None:
        state, label = parent[state]
        steps.append(label)
    return list(reversed(steps))


def shortest_by_enumeration(fixed, max_depth=8, members=MEMBERS):
    """Brute force: try every path up to max_depth; return the minimum length that reaches an unsafe state."""
    frontier = [initial(members)]
    for depth in range(max_depth + 1):
        if any(not safe(s) for s in frontier):
            return depth
        frontier = [nxt for s in frontier for _, nxt in successors(s, fixed, members)]
    return None


def can_always_free_book(fixed, members=MEMBERS):
    """AG EF (no active loan): from every reachable state some path leads back to 'book available'."""
    _, _, _, parent = bfs(fixed, prop=lambda s: True, members=members)
    reachable = set(parent)
    good = {s for s in reachable if not s[1]}
    changed = True
    while changed:
        changed = False
        for s in reachable - good:
            if any(nxt in good for _, nxt in successors(s, fixed, members)):
                good.add(s)
                changed = True
    return good == reachable, len(reachable)
