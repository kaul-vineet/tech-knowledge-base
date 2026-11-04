"""tryIt experiments for lesson 9 (python try_it.py). Prints what actually happens."""
import random
from collections import Counter

import ring as r

KEYS = [f"user:{i}" for i in range(10_000)]

# tryIt 1: add node E with 1 vnode vs 100 vnodes per node: which nodes give up keys?
for v in (1, 100):
    before, after = r.HashRing(list("ABCD"), v), r.HashRing(list("ABCDE"), v)
    donors = Counter(before.node_for(k) for k in KEYS if before.node_for(k) != after.node_for(k))
    print(f"tryIt 1: vnodes={v:<3} add E -> moves {r.moved(before.node_for, after.node_for, KEYS):.1%}, taken from {dict(sorted(donors.items()))}")

# tryIt 2: split the hot key user:42 into 8 sub-keys user:42#0..7 (each read picks one at random)
ring, rng = r.HashRing(list("ABCD")), random.Random(42)
traffic = Counter(ring.node_for(f"user:42#{rng.randrange(8)}" if rng.random() < 0.2 else rng.choice(KEYS))
                  for _ in range(100_000))
print(f"tryIt 2: hot key split 8 ways -> requests per node {dict(sorted(traffic.items()))} imbalance {r.imbalance(traffic):.2f}")
