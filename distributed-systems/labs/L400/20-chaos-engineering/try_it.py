"""tryIt experiments for lesson 20 (python try_it.py). Prints what actually happens."""
import solution_chaos as sc

# tryIt 1: how much do the blast radius and the abort rule each protect? (shipping outage vs the L300 lesson saga)
for blast, abort in ((10.0, 1), (10.0, 10**6), (50.0, 10**6)):
    sc.BLAST_PCT, sc.ABORT_AFTER = blast, abort
    r = sc.run_saga_experiment("L300 lesson", "shipping-outage", 14)
    print(f"tryIt 1: blast {blast:.0f}%, abort after {'1 harmed order' if abort == 1 else 'never'}:"
          f" customers hurt {r['customers_hurt']}, hypothesis held {r['held']}")
sc.BLAST_PCT, sc.ABORT_AFTER = 10.0, 1

# tryIt 2: a patient rollout waits 20-30 ticks for each restarted node to catch up before touching the next one
for settle in ((0, 4), (20, 30)):
    lost = sum(not sc.run_raft_experiment("L300 lesson", "rolling-restart", s, settle=settle)["held"] for s in range(1, 21))
    print(f"tryIt 2: rolling restart, wait {settle[0]}-{settle[1]} ticks between nodes: L300 lesson Raft refuted in {lost}/20 seeds")
