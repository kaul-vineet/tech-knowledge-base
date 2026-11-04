"""L300 lesson 12 (python raft.py): a simplified Raft replicated log on 3 in-process nodes over a deterministic
simulated network (helpers.Network, driven by helpers.Cluster). Terms, leader election, log replication, commit index, leader crash and
re-election, then the failure lab: a follower with a stale log wins an election. Simplified: no disk, no
snapshots, no membership changes, no PreVote. Seeded: identical output on every run."""
import random

from helpers import Cluster, demo, fmt

HEARTBEAT, TIMEOUT = 3, (10, 20)  # ticks; each node draws its election timeout from a seeded RNG


class Node:
    def __init__(self, name, peers, net, seed):
        self.name, self.peers, self.net, self.rng = name, peers, net, random.Random(f"{seed}-{name}")
        self.term, self.voted_for, self.log = 0, None, []  # persistent state; log[i-1] = (term, command)
        self.commit, self.role, self.votes = 0, "follower", set()  # volatile state
        self.reset_timer()

    def reset_timer(self):
        self.deadline = self.net.now + self.rng.randint(*TIMEOUT)  # randomized timeout: split votes stay rare

    def last(self):
        return (self.log[-1][0] if self.log else 0), len(self.log)  # (last log term, last log index)

    def tick(self):
        if self.role == "leader":
            if self.net.now % HEARTBEAT == 0:
                for p in self.peers:
                    self.send_append(p)  # heartbeat = AppendEntries, carries new entries if any
        elif self.net.now >= self.deadline:  # heard no leader for a whole timeout: new term, vote for me
            self.term, self.role, self.voted_for, self.votes = self.term + 1, "candidate", self.name, {self.name}
            self.reset_timer()
            last_term, last_index = self.last()
            self.net.log(f"{self.name} starts election for term {self.term} (log {fmt(self.log)})")
            for p in self.peers:
                self.net.send(self.name, p, {"type": "vote", "term": self.term, "last_term": last_term, "last_index": last_index})

    def send_append(self, p):
        prev = self.next[p] - 1  # consistency check: the follower must hold my entry at prev
        self.net.send(self.name, p, {"type": "append", "term": self.term, "prev_index": prev,
                                     "prev_term": self.log[prev - 1][0] if prev else 0,
                                     "entries": self.log[prev:], "commit": self.commit})

    def propose(self, command):  # client request; only the leader appends (Leader Append-Only)
        self.log.append((self.term, command))
        for p in self.peers:
            self.send_append(p)

    def receive(self, src, m):
        if m["term"] > self.term:  # terms are a logical clock: a newer term turns anyone into a follower
            self.term, self.role, self.voted_for = m["term"], "follower", None
        kind, reply = m["type"], {"term": self.term}
        if kind == "vote":
            # RequestVote: one vote per term, first come first served. (Raft also checks the candidate's log.)
            granted = m["term"] == self.term and self.voted_for in (None, src)
            if granted:
                self.voted_for = src
                self.reset_timer()
            self.net.send(self.name, src, {**reply, "type": "vote_reply", "granted": granted})
        elif kind == "vote_reply" and self.role == "candidate" and m["term"] == self.term and m["granted"]:
            self.votes.add(src)
            if 2 * len(self.votes) > len(self.peers) + 1:  # majority of the FULL cluster (2 of 3)
                self.role, self.next, self.match = "leader", {p: len(self.log) + 1 for p in self.peers}, {p: 0 for p in self.peers}
                self.net.log(f"{self.name} becomes leader for term {self.term} with votes {sorted(self.votes)}")
                for p in self.peers:
                    self.send_append(p)
        elif kind == "append":
            ok = m["term"] == self.term
            if ok:
                self.role = "follower"
                self.reset_timer()  # a live leader for my term: no election
                prev = m["prev_index"]
                ok = prev <= len(self.log) and (prev == 0 or self.log[prev - 1][0] == m["prev_term"])
            if ok:
                for i, entry in enumerate(m["entries"], start=prev + 1):
                    if i <= len(self.log) and self.log[i - 1][0] != entry[0]:
                        del self.log[i - 1:]  # conflict: drop my entry and everything after it
                    if i > len(self.log):
                        self.log.append(entry)
                reply["match"] = prev + len(m["entries"])
                self.commit = max(self.commit, min(m["commit"], reply["match"]))  # learn the commit index
            self.net.send(self.name, src, {**reply, "type": "append_reply", "ok": ok})
        elif kind == "append_reply" and self.role == "leader" and m["term"] == self.term:
            if m["ok"]:
                self.match[src], self.next[src] = m["match"], m["match"] + 1
                for n in range(len(self.log), self.commit, -1):  # commit index: highest N on a majority ...
                    if self.log[n - 1][0] == self.term and 2 * (1 + sum(v >= n for v in self.match.values())) > len(self.peers) + 1:
                        self.commit = n  # ... from MY term only (paper section 5.4.2)
                        break
            else:
                self.next[src] = max(1, self.next[src] - 1)  # walk back until the logs match
                self.send_append(src)


def stale_leader_scenario(node_class=Node, seed=7):
    """Failure lab: a follower misses committed entries, the leader crashes, the stale follower's timer fires first."""
    c = Cluster(node_class, seed)
    leader = c.run_until_leader()
    follower, stale = [n for n in c.nodes if n != leader.name]
    c.crash(stale)  # stale is down (or partitioned) while the others commit
    leader.propose("x=1")
    leader.propose("x=2")
    c.run(6)
    c.crash(leader.name)
    c.restart(stale)
    c.nodes[stale].deadline = c.net.now + 1  # fault: stale's randomized timer happens to fire first
    c.run_until_leader().propose("x=9")
    c.run(12)
    return c


if __name__ == "__main__":
    demo(Node, stale_leader_scenario)  # helpers.demo: happy path, crash + re-election, restart, failure lab
