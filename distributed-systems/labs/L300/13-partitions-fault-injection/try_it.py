"""tryIt experiments for lesson 13 (python try_it.py). Prints what actually happens."""
import partition as pt
import solution_partition as sol
from checker import check_register

# tryIt 1: no full partition, just a flaky link: the proxy drops 50% of n1's lease requests (seeded)
for seed in (13, 14, 15):
    events, _, leaders = pt.run({}, {1: lambda p: (p.add("n1", "lease", drop=0.5), "drop 0.5 n1->lease")[1]}, seed=seed, ticks=30)
    split = sum(len(l) > 1 for l in leaders)
    took_over = next((t for t, l in enumerate(leaders) if "n2" in l), None)
    print(f"tryIt 1: seed {seed}: n2 takes the lease at t={took_over}, ticks with two leaders: {split}")

# tryIt 2: fencing ON (solution), but c1 READS from n1's local cache instead of writing
reads = {1: ("c1", "n1", "write", 1), 6: ("c2", "n2", "write", 2), 7: ("c1", "n1", "read", None)}
for name, mod in (("without fencing", pt), ("with fencing", sol)):
    _, history, _ = mod.run(reads, pt.FAULTS)
    print(f"tryIt 2: {name}: c1 read via n1 -> {history[-1]['value']}, linearizable: {check_register(history)[0]}")
