"""SOLUTION for the lesson 9 build task (python solution_ring.py): ring.py + HashRing.nodes_for(key, n).
L200 lesson 9 (python ring.py): shard keys over nodes with a consistent-hash ring + virtual nodes.
Measures how many keys move when a node joins or leaves (ring vs hash % N), how even the load is with
1 / 10 / 100 vnodes per node, and what one hot key does to its shard. Deterministic (md5, seeded traffic)."""
import bisect, hashlib, random
from collections import Counter


def h(text):  # stable 64-bit ring position; Python's hash() is salted per process -> never use it here
    return int.from_bytes(hashlib.md5(text.encode("utf-8")).digest()[:8], "big")


class HashRing:
    def __init__(self, nodes, vnodes=100):
        self.vnodes, self.points, self.owner = vnodes, [], {}
        for node in nodes:
            self.add(node)

    def add(self, node):  # virtual nodes: each physical node takes `vnodes` positions on the ring
        for i in range(self.vnodes):
            point = h(f"{node}#{i}")
            bisect.insort(self.points, point)
            self.owner[point] = node

    def remove(self, node):
        self.points = [p for p in self.points if self.owner[p] != node]
        self.owner = {p: n for p, n in self.owner.items() if n != node}

    def node_for(self, key):  # walk clockwise from the key's position to the next vnode (wrap at the end)
        i = bisect.bisect(self.points, h(key)) % len(self.points)
        return self.owner[self.points[i]]


    def nodes_for(self, key, n=3):  # replicas: keep walking clockwise, skip vnodes of nodes already chosen
        if n > len(set(self.owner.values())):
            raise ValueError(f"need {n} distinct nodes, ring has {len(set(self.owner.values()))}")
        i, chosen = bisect.bisect(self.points, h(key)), []
        while len(chosen) < n:
            node = self.owner[self.points[i % len(self.points)]]
            if node not in chosen:
                chosen.append(node)
            i += 1
        return chosen


def modulo_node(key, nodes):  # the naive way: hash mod N -> almost every key moves when N changes
    return nodes[h(key) % len(nodes)]


def moved(before, after, keys):
    return sum(before(k) != after(k) for k in keys) / len(keys)


def imbalance(counts):  # busiest node / average node; 1.00 = perfectly even
    return max(counts.values()) / (sum(counts.values()) / len(counts))


def main():
    keys, four = [f"user:{i}" for i in range(10_000)], ["A", "B", "C", "D"]
    ring = HashRing(four)
    grown = HashRing(four + ["E"])
    print(f"add E   : hash % N moves {moved(lambda k: modulo_node(k, four), lambda k: modulo_node(k, four + ['E']), keys):.1%}"
          f" of 10,000 keys; ring moves {moved(ring.node_for, grown.node_for, keys):.1%} (ideal 1/5 = 20.0%)")
    shrunk = HashRing(four)
    shrunk.remove("D")
    only_d = all(ring.node_for(k) == "D" for k in keys if ring.node_for(k) != shrunk.node_for(k))
    print(f"remove D: ring moves {moved(ring.node_for, shrunk.node_for, keys):.1%}; only D's keys moved: {only_d}")
    for v in (1, 10, 100):
        sized = HashRing(four, v)
        counts = Counter(sized.node_for(k) for k in keys)
        print(f"vnodes={v:<3}: keys per node {dict(sorted(counts.items()))} imbalance {imbalance(counts):.2f}")
    rng = random.Random(42)  # 100,000 requests: 20% for one celebrity key, the rest spread evenly
    traffic = Counter(ring.node_for("user:42" if rng.random() < 0.2 else rng.choice(keys)) for _ in range(100_000))
    print(f"hot key : user:42 lives on {ring.node_for('user:42')}; requests per node {dict(sorted(traffic.items()))}"
          f" imbalance {imbalance(traffic):.2f}")


if __name__ == "__main__":
    main()
    keys, ring, grown = [f"user:{i}" for i in range(10_000)], HashRing(list("ABCD")), HashRing(list("ABCDE"))
    print("replicas: user:1 ->", ring.nodes_for("user:1"), "| user:42 ->", ring.nodes_for("user:42"))
    share = sum("E" in grown.nodes_for(k) for k in keys) / len(keys)
    print(f"add E   : E now holds a replica of {share:.1%} of keys (fair share 3 of 5 nodes = 60.0%)")
