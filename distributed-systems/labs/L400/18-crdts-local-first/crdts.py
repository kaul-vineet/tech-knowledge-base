"""L400 lesson 18 (python crdts.py): state-based CRDTs for local-first collaboration.
G-Counter, PN-Counter, OR-Set and LWW-Register (Shapiro et al., 2011): every replica updates locally (offline
is fine) and merge() is a join - commutative, associative, idempotent - so replicas that have seen the same updates
hold the same state, whatever order, duplication or path the sync took. helpers.py generates seeded random
histories and checks those laws; this file shows a two-phone story, the property results and the options."""
import json, random

from helpers import check_laws, converge, size


class GCounter:  # grow-only: one slot per replica, merge = per-slot max (vector-clock shape)
    def __init__(self, slots=None):
        self.slots = dict(slots or {})

    def inc(self, replica, n=1):
        self.slots[replica] = self.slots.get(replica, 0) + n  # a replica only ever touches its own slot

    def value(self):
        return sum(self.slots.values())

    def merge(self, other):
        keys = self.slots.keys() | other.slots.keys()
        return GCounter({k: max(self.slots.get(k, 0), other.slots.get(k, 0)) for k in keys})

    def state(self):
        return sorted(self.slots.items())


class PNCounter:  # increments and decrements = two G-Counters
    def __init__(self, p=None, n=None):
        self.p, self.n = p or GCounter(), n or GCounter()

    def add(self, replica, delta):
        (self.p if delta >= 0 else self.n).inc(replica, abs(delta))

    def value(self):
        return self.p.value() - self.n.value()

    def merge(self, other):
        return PNCounter(self.p.merge(other.p), self.n.merge(other.n))

    def state(self):
        return self.p.state(), self.n.state()


class ORSet:  # observed-remove set: add-wins; every add gets a unique tag, remove tombstones the tags it saw
    def __init__(self, adds=None, tombs=None):
        self.adds, self.tombs = {e: set(t) for e, t in (adds or {}).items()}, set(tombs or ())

    def add(self, element, tag):
        self.adds.setdefault(element, set()).add(tag)  # tag = (replica, counter): unique per add

    def remove(self, element):
        self.tombs |= self.adds.get(element, set())  # only tags observed HERE: a concurrent add survives

    def value(self):
        return {e for e, tags in self.adds.items() if tags - self.tombs}

    def merge(self, other):
        adds = {e: self.adds.get(e, set()) | other.adds.get(e, set()) for e in self.adds.keys() | other.adds.keys()}
        return ORSet(adds, self.tombs | other.tombs)

    def state(self):
        return sorted((e, sorted(t)) for e, t in self.adds.items()), sorted(self.tombs)


class LWWRegister:  # last-writer-wins by Lamport timestamp; the replica id travels with the value
    def __init__(self, value=None, ts=0, replica=""):
        self.val, self.ts, self.replica = value, ts, replica

    def assign(self, replica, value, seen_ts):
        self.val, self.ts, self.replica = value, max(self.ts, seen_ts) + 1, replica

    def value(self):
        return self.val

    def merge(self, other):
        if other.ts > self.ts:  # BUG (failure lab): equal timestamps keep MY value -> merge is not commutative
            return LWWRegister(other.val, other.ts, other.replica)
        return LWWRegister(self.val, self.ts, self.replica)

    def state(self):
        return self.val, self.ts, self.replica


class LWWCounter(LWWRegister):  # option "store the number, last writer wins": concurrent increments get lost
    def add(self, replica, delta):
        self.assign(replica, (self.val or 0) + delta, self.ts)

    def merge(self, other):
        won = LWWRegister.merge(self, other)
        return LWWCounter(won.val, won.ts, won.replica)


TYPES = {"G-Counter": GCounter, "PN-Counter": PNCounter, "OR-Set": ORSet, "LWW-Register": LWWRegister}


def two_phones():
    """Two devices edit a shared shopping list offline, then sync both ways."""
    phone, laptop = ORSet(), ORSet()
    phone.add("milk", ("phone", 1))
    laptop = laptop.merge(phone)
    phone.remove("milk")  # phone removes milk ...
    laptop.add("milk", ("laptop", 1))  # ... while the laptop re-adds it (concurrently): add wins
    laptop.add("eggs", ("laptop", 2))
    return phone.merge(laptop), laptop.merge(phone)


def like_counter(seed=18, steps=300):
    """Options for a shared like-counter: 3 replicas, random sync, 20% of syncs delivered twice."""
    rng, truth = random.Random(seed), 0
    reps = {"lww": [LWWCounter() for _ in range(3)], "pn": [PNCounter() for _ in range(3)]}
    for _ in range(steps):
        i, j, delta = rng.randrange(3), rng.randrange(3), rng.choice((1, 1, 1, -1))
        truth += delta
        for rs in reps.values():
            rs[i].add(f"r{i}", delta)
        if rng.random() < 0.5:
            for _ in range(2 if rng.random() < 0.2 else 1):
                for rs in reps.values():
                    rs[j] = rs[j].merge(rs[i])
    for rs in reps.values():  # final anti-entropy: everyone merges everyone
        for x in range(3):
            for y in range(3):
                rs[y] = rs[y].merge(rs[x])
    return {"truth": truth, **{k: [r.value() for r in rs] for k, rs in reps.items()},
            "bytes": {k: size(rs[0]) for k, rs in reps.items()}}


if __name__ == "__main__":
    a, b = two_phones()
    print(f"1) phone+laptop: {sorted(a.value())} == {sorted(b.value())}: {a.state() == b.state()}")
    print("2) merge laws and convergence over 500 seeded random histories per type:")
    for name, cls in TYPES.items():
        laws, conv = check_laws(cls, seed=18), converge(cls, seed=18)
        print(f"   {name:13} {json.dumps({**laws['counts'], 'converged': conv['converged']})}")
        for example in filter(None, (laws["counterexample"], conv["counterexample"])):
            print(f"   {'':13} shrunk counterexample: {example}")
    c = like_counter()
    print(f"3) like-counter, truth {c['truth']}: LWW number {c['lww']} (concurrent adds lost), PN-Counter {c['pn']};"
          f" sync bytes LWW {c['bytes']['lww']}, PN {c['bytes']['pn']}")
