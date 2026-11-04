"""L400 lesson 21 (python modelcheck.py): find a protocol bug automatically by exhaustive model checking.
A toy leader election (Raft's voting rule, 3 nodes, terms up to 2) is written as a state machine: a state is an
immutable tuple, actions produce successor states. bfs() visits EVERY reachable state, checks the invariants in
each and returns the SHORTEST trace to a violation - what TLC does for a TLA+ spec (Election.tla is the same model).
The lesson protocol keeps votedFor only in memory, so a restart forgets the vote."""
import random, time
from collections import deque

NODES, MAX_TERM = (0, 1, 2), 2
PERSIST_VOTE = False  # the bug: a restarted node forgets whom it voted for in its current term


def init():
    # per node: (term, voted_for, role, votes received); plus a ghost log of every vote ever cast (term, voter, cand)
    return tuple((0, None, "follower", frozenset()) for _ in NODES), frozenset()


def replace(nodes, i, node):
    return nodes[:i] + (node,) + nodes[i + 1:]


def actions(state):
    """Every enabled step: (label, next_state). Messages are delivered atomically (request + reply in one step)."""
    nodes, cast = state
    for i, (term, voted, role, votes) in enumerate(nodes):
        if role != "leader" and term < MAX_TERM:  # election timeout: new term, vote for myself
            yield f"n{i} times out -> candidate, term {term + 1}", (
                replace(nodes, i, (term + 1, i, "candidate", frozenset({i}))), cast | {(term + 1, i, i)})
        if role == "candidate" and 2 * len(votes) > len(NODES):
            yield f"n{i} becomes leader of term {term}", (replace(nodes, i, (term, voted, "leader", votes)), cast)
        if role == "candidate":
            for j in NODES:
                if j in votes or j == i:
                    continue
                jt, jv, jr, jvotes = nodes[j]
                if jt > term:
                    continue  # j is in a newer term: it refuses (and i would step down later)
                if jt < term:  # newer term seen: j becomes a follower with no vote in that term yet
                    jt, jv, jr, jvotes = term, None, "follower", frozenset()
                if jv in (None, i):  # one vote per term, first come first served
                    nxt = replace(replace(nodes, j, (jt, i, jr, jvotes)), i, (term, voted, role, votes | {j}))
                    yield f"n{j} votes for n{i} in term {term}", (nxt, cast | {(term, j, i)})
    for j, (term, voted, role, votes) in enumerate(nodes):  # crash + restart: volatile state is lost
        kept = voted if PERSIST_VOTE else None
        restarted = (term, kept, "follower", frozenset())
        if restarted != nodes[j]:
            yield f"n{j} restarts (votedFor {'kept' if PERSIST_VOTE else 'forgotten'})", (replace(nodes, j, restarted), cast)


def election_safety(state):
    """At most one leader per term (Raft, Figure 3)."""
    leaders = [(t, i) for i, (t, _, role, _) in enumerate(state[0]) if role == "leader"]
    return len({t for t, _ in leaders}) == len(leaders)


INVARIANTS = {"ElectionSafety": election_safety}


def bfs(invariants=None):
    """Explicit-state breadth-first search. Returns (violated invariant or None, shortest trace, states, ms)."""
    invariants, start = invariants or INVARIANTS, time.perf_counter()
    first = init()
    parent, queue = {first: None}, deque([first])
    while queue:
        state = queue.popleft()
        for name, ok in invariants.items():
            if not ok(state):
                trace = []
                while parent[state]:
                    state, label = parent[state]
                    trace.append(label)
                return name, trace[::-1], len(parent), round(1000 * (time.perf_counter() - start))
        for label, nxt in actions(state):
            if nxt not in parent:
                parent[nxt] = (state, label)
                queue.append(nxt)
    return None, [], len(parent), round(1000 * (time.perf_counter() - start))


def random_walks(walks=1000, depth=30, seed=21):
    """The cheaper alternative: random simulation. How many walks hit the bug, and how long is the first trace?"""
    rng, hits, shortest = random.Random(seed), 0, None
    for _ in range(walks):
        state = init()
        for step in range(1, depth + 1):
            options = list(actions(state))
            if not options:
                break
            state = rng.choice(options)[1]
            if not all(ok(state) for ok in INVARIANTS.values()):
                hits, shortest = hits + 1, min(shortest or step, step)
                break
    return hits, shortest


if __name__ == "__main__":
    violated, trace, states, ms = bfs()
    print(f"BFS: {states} distinct states explored, invariant {violated or 'none'} violated")
    for k, label in enumerate(trace, start=1):
        print(f"  {k}. {label}")
    hits, shortest = random_walks()
    print(f"random simulation: bug hit in {hits}/1000 walks of <= 30 steps (shortest {shortest or '-'} steps)")
