"""Plumbing for lab 18 (not the lesson's concept): a tiny property-based tester. It generates seeded random
histories (local updates on 3 replicas + random, possibly duplicated, syncs), replays them, checks the merge laws
and convergence, and shrinks a failing history to a short counterexample (like Hypothesis/QuickCheck, stdlib only)."""
import json, random


KINDS = ("GCounter", "PNCounter", "ORSet", "LWWRegister")


def kind(cls):
    """The CRDT family of a class (subclasses used in tryIt keep their parent's operations)."""
    return next(c.__name__ for c in cls.__mro__ if c.__name__ in KINDS)


def random_op(name, rng, replica, k):
    """One random local update for a CRDT type: (method, args). Tags and values are unique per (replica, k)."""
    if name == "GCounter":
        return "inc", (replica, rng.randint(1, 3))
    if name == "PNCounter":
        return "add", (replica, rng.choice((-2, -1, 1, 2)))
    if name == "ORSet":
        e = rng.choice("abc")
        return ("add", (e, (replica, k))) if rng.random() < 0.6 else ("remove", (e,))
    return "assign", (replica, f"{replica}.{k}", 0)  # LWWRegister


def gen_history(name, rng, steps=12, n=3):
    hist = []
    for k in range(steps):
        if rng.random() < 0.6:
            i = rng.randrange(n)
            hist.append(("op", i, *random_op(name, rng, f"r{i}", k)))
        else:
            i, j = rng.sample(range(n), 2)
            hist += [("sync", i, j)] * (2 if rng.random() < 0.2 else 1)  # 20% of syncs arrive twice
    return hist


def replay(cls, hist, n=3):
    reps = [cls() for _ in range(n)]
    for step in hist:
        if step[0] == "op":
            getattr(reps[step[1]], step[2])(*step[3])
        else:
            reps[step[2]] = reps[step[2]].merge(reps[step[1]])  # j learns i's state
    return reps


def shrink(hist, fails):
    """Greedy: drop one step at a time while the property still fails -> a short, readable counterexample."""
    changed = True
    while changed:
        changed = False
        for k in range(len(hist)):
            smaller = hist[:k] + hist[k + 1:]
            if fails(smaller):
                hist, changed = smaller, True
                break
    return hist


def describe(hist):
    return "; ".join(f"r{s[1]}.{s[2]}{s[3]}" if s[0] == "op" else f"sync r{s[1]}->r{s[2]}" for s in hist)


def law_failures(cls, hist):
    x, y, z = replay(cls, hist)
    return [law for law, ok in (
        ("commutative", x.merge(y).state() == y.merge(x).state()),
        ("associative", x.merge(y).merge(z).state() == x.merge(y.merge(z)).state()),
        ("idempotent", x.merge(x).state() == x.state())) if not ok]


def check_laws(cls, seed=18, trials=500):
    rng, counts, example = random.Random(f"{seed}-{kind(cls)}-laws"), {}, None
    for law in ("commutative", "associative", "idempotent"):
        counts[law] = 0
    for _ in range(trials):
        hist = gen_history(kind(cls), rng)
        bad = law_failures(cls, hist)
        for law in counts:
            counts[law] += law not in bad
        if bad and example is None:
            small = shrink(hist, lambda h: bad[0] in law_failures(cls, h))
            example = f"{bad[0]} fails after: {describe(small)}"
    return {"counts": {law: f"{ok}/{trials}" for law, ok in counts.items()}, "counterexample": example}


def anti_entropy(reps, rng):
    for _ in range(2):  # every replica merges every other one, in a random order, twice
        pairs = [(i, j) for i in range(len(reps)) for j in range(len(reps)) if i != j]
        rng.shuffle(pairs)
        for i, j in pairs:
            reps[j] = reps[j].merge(reps[i])
    return reps


def diverged(cls, hist, seed):
    reps = anti_entropy(replay(cls, hist), random.Random(seed))
    states = {json.dumps(r.state(), default=list) for r in reps}
    expected = sum(s[3][1] for s in hist if s[0] == "op" and s[2] in ("inc", "add") and isinstance(s[3][1], int))
    wrong_value = kind(cls) in ("GCounter", "PNCounter") and reps[0].value() != expected
    return len(states) > 1 or wrong_value


def converge(cls, seed=18, trials=500):
    rng, ok, example = random.Random(f"{seed}-{kind(cls)}-conv"), 0, None
    for t in range(trials):
        hist = gen_history(kind(cls), rng)
        if not diverged(cls, hist, t):
            ok += 1
        elif example is None:
            example = f"replicas diverge after: {describe(shrink(hist, lambda h: diverged(cls, h, t)))}"
    return {"converged": f"{ok}/{trials}", "counterexample": example}


def size(obj):
    """Bytes of state a sync would ship (JSON), the metadata cost of a CRDT."""
    return len(json.dumps(obj.state(), default=list))
