"""Try it: two experiments on group keys (run: python try_it.py)."""
import copy
import itertools

import group_keys as gk
import solution_remove

NAMES = ["alice", "bob", "carol", "dave", "erin", "frank", "grace", "heidi"]

# 1) Post-compromise security: an attacker copies carol's whole key state, then carol sends an update Commit.
g = solution_remove.Group(NAMES)
g.members["ghost"] = copy.deepcopy(g.members["carol"])  # the stolen state follows the protocol like a member
before = g.read("ghost", g.send("alice", "before the update")) is not None
g.commit("carol")  # fresh entropy from carol's device, sent only to current members
after = g.read("ghost", g.send("alice", "after the update")) is not None
print(f"1) attacker with carol's stolen state reads: before update {before}, after carol's update {after}")

# 2) How often does the UNFIXED remove leak? Try every (committer, removed) pair in a group of 8.
leaks = []
for committer, removed in itertools.permutations(NAMES, 2):
    bad = gk.Group(NAMES)
    bad.commit(committer, remove=removed)
    if bad.read(removed, bad.send(committer, "x")) is not None:
        leaks.append((committer, removed))
siblings = [p for p in itertools.permutations(NAMES, 2) if p not in leaks]
print(f"2) unfixed remove leaks in {len(leaks)} of 56 pairs; safe only when the committer is the removed member's"
      f" sibling: {sorted(siblings)[:4]} ...")
