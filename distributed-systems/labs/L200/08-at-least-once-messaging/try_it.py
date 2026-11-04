"""tryIt experiments for lesson 8 (python try_it.py). Prints what actually happens."""
import broker as b

# tryIt 1: visibility timeout 3 s vs 10 s (same seed): how long until the poison message is dead-lettered?
for vis in (3.0, 10.0):
    b.VISIBILITY = vis
    out = b.run(quiet=True)
    last = out["log"][-1].split()[0]
    print(f"tryIt 1: VISIBILITY {vis:.0f} s -> last delivery at {last}, {len(out['ledger'])} charges, DLQ {out['dlq']}")
b.VISIBILITY = 3.0

# tryIt 2: MAX_RECEIVES 2 vs 3 vs 5 over 30 seeded runs (30% crash rate): how often is a GOOD order dead-lettered?
for limit in (2, 3, 5):
    b.MAX_RECEIVES = limit
    bad = sum(any(x != "poison" for x in b.run(seed=s, quiet=True)["dlq"]) for s in range(30))
    print(f"tryIt 2: MAX_RECEIVES {limit} -> {bad}/30 runs dead-lettered a good order")
b.MAX_RECEIVES = 3
