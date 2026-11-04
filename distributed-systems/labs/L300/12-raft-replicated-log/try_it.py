"""tryIt experiments for lesson 12 (python try_it.py). Prints what actually happens."""
import raft
import solution_raft
from helpers import Cluster

# tryIt 1: crash BOTH followers; the leader still accepts x=5 but cannot reach a majority
c = Cluster(raft.Node, seed=7)
leader = c.run_until_leader()
leader.propose("x=1")
c.run(6)
for n in c.nodes:
    if n != leader.name:
        c.crash(n)
leader.propose("x=5")
c.run(30)
print(f"tryIt 1: followers down -> {leader.name} log has {len(leader.log)} entries, commit index stays {leader.commit}"
      f" (x=5 appended, never committed)")

# tryIt 2: the same failure lab with seeds 1..20, without and with the election restriction
for name, mod in (("raft.py (no log check)", raft), ("solution_raft.py (log check)", solution_raft)):
    lost = sum(bool(mod.stale_leader_scenario(mod.Node, seed).checker.violations) for seed in range(1, 21))
    print(f"tryIt 2: {name}: committed entries lost in {lost} of 20 seeds")
