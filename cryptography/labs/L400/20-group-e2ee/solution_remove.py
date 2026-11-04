"""Build-task solution: a Remove blanks the removed leaf AND every node on its direct path (RFC 9420 12.1.3).
Resolutions then skip every key the removed member knew, so the Commit's fresh path secrets reach only the members
who stay: the removed member cannot compute the next epoch secret (forward secrecy for the group after removal)."""
import random

import group_keys as gk
import tree_math as tm


class Group(gk.Group):
    def _remove(self, name: str):
        x = tm.leaf(self.n, self.index.pop(name))
        for node in [x] + tm.direct_path(x):  # the commit re-keys the shared part of the path with fresh secrets
            self.nodes[node] = None


if __name__ == "__main__":
    rng = random.Random(gk.SEED)
    names = ["alice", "bob", "carol", "dave", "erin", "frank", "grace", "heidi"]
    g = Group(names)
    g.commit("carol")
    removed, committer = rng.choice(names[1:4]), rng.choice(names[4:])
    sent = g.commit(committer, remove=removed)
    msg = g.send(committer, "new launch date: 1 March")
    print(f"{committer} removes {removed}: commit HPKE encryptions {sent} | can read post-removal message:",
          {name: g.read(name, msg) is not None for name in names})
