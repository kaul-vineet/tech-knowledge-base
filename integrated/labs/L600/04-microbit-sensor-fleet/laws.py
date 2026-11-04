"""Property test for ReadingStore (the distributed-systems L400 #18 method, reusing its shrink()):
seeded random histories of adds + (possibly duplicated) syncs on 3 replicas; merge must be commutative,
associative and idempotent, and both sync paths (full-state merge, delta via digest) must agree."""
import random

import _kb
from store import ReadingStore

shrink = _kb.crdt_helpers().shrink


def value(dot):
    return (1_790_000_000 + dot[2] * 60, 20 + dot[0], 100, 2)   # readings are immutable: one value per dot


def gen(rng, steps=14):
    hist = []
    for _ in range(steps):
        if rng.random() < 0.6:
            hist.append(("add", rng.randrange(3), (rng.randint(1, 2), rng.randint(1, 2), rng.randint(1, 5))))
        else:
            i, j = rng.sample(range(3), 2)
            hist += [("sync", i, j, rng.random() < 0.5)] * (2 if rng.random() < 0.2 else 1)
    return hist


def replay(hist):
    reps = [ReadingStore() for _ in range(3)]
    for step in hist:
        if step[0] == "add":
            reps[step[1]].add(step[2], value(step[2]))
        elif step[3]:                                       # full-state join
            reps[step[2]] = reps[step[2]].merge(reps[step[1]])
        else:                                               # delta for the receiver's digest
            reps[step[2]].merge_delta(reps[step[1]].delta_for(reps[step[2]].digest()))
    return reps


def failures(hist):
    x, y, z = replay(hist)
    bad = [law for law, ok in (
        ("commutative", x.merge(y).state() == y.merge(x).state()),
        ("associative", x.merge(y).merge(z).state() == x.merge(y.merge(z)).state()),
        ("idempotent", x.merge(x).state() == x.state())) if not ok]
    d = ReadingStore()
    d.merge_delta(x.delta_for(d.digest()))
    d.merge_delta(y.delta_for(d.digest()))
    return bad + ([] if d.state() == x.merge(y).state() else ["delta==state"])


def check(seed=4, trials=300):
    rng, passed, example = random.Random(seed), 0, None
    for _ in range(trials):
        hist = gen(rng)
        bad = failures(hist)
        passed += not bad
        if bad and example is None:
            example = shrink(hist, lambda h: bool(failures(h)))
    return {"trials": trials, "passed": passed, "counterexample": example}
