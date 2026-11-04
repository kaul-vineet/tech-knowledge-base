"""tryIt experiments for lesson 18 (python try_it.py). Prints what actually happens."""
from crdts import GCounter, ORSet
from helpers import check_laws, converge, size


class SumGCounter(GCounter):  # tryIt 1: merge adds the slots instead of taking the max
    def merge(self, other):
        keys = self.slots.keys() | other.slots.keys()
        return SumGCounter({k: self.slots.get(k, 0) + other.slots.get(k, 0) for k in keys})


laws, conv = check_laws(SumGCounter), converge(SumGCounter)
print(f"tryIt 1: G-Counter with sum-merge: {laws['counts']}, converged {conv['converged']}")
print(f"         {laws['counterexample']}")

# tryIt 2: OR-Set metadata: one live element, re-added and removed N times (tombstones are never collected here)
for cycles in (10, 100, 1000):
    s = ORSet()
    for k in range(cycles):
        s.add("milk", ("phone", k))
        s.remove("milk")
    s.add("milk", ("phone", cycles))
    print(f"tryIt 2: {cycles:>4} add/remove cycles -> value {sorted(s.value())}, tombstones {len(s.tombs)}, state {size(s)} bytes")
