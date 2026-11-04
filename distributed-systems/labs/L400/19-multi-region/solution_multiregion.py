"""L400 lesson 19 BUILD-TASK REFERENCE (python solution_multiregion.py): multiregion.py + measured leader placement
and majority-sync replication. Original header: multi-region design under a latency budget, measured in a simulation.
Three regions (us, eu, ap; latencies in helpers.py), 100 writes/s for 20 s, seeded. Designs: single leader with
async or majority-sync replication, multi-leader, leaderless W=2. For each we measure write p99 per user region,
follower lag, write conflicts, and what a region failure at t=10 s costs: RPO (acknowledged writes lost) and RTO
(time until writes succeed again). The deployed design is checked against the constraints in the design brief."""
from helpers import REGIONS, TRAFFIC, Net, conflicts, pct, write_stream

T_FAIL, ELECTION_MS = 10000.0, (1000.0, 2000.0)  # failure time; election timeout range (WAN heartbeats)
DESIGN = {"replication": "sync-majority", "leader": "eu"}  # ADR-019: = place_leader("sync-majority")
CONSTRAINTS = {"write_p99_ms": {"us": 350.0, "eu": 350.0}, "rpo_writes": 0, "rto_ms": 5000.0, "conflicts": 0}


def leader_write(net, mode, leader, followers, t, origin):
    """Single leader: one round trip to the leader; majority-sync also waits for the FIRST follower ack."""
    t_arr = net.send(origin, leader, t)
    arrive = {leader: t_arr, **{f: net.send(leader, f, t_arr, fifo=True) for f in followers}}  # the log stream
    commit = t_arr if mode == "async" else min(net.send(f, leader, arrive[f]) for f in followers)
    return t_arr, commit, net.send(leader, origin, commit), arrive


def simulate(design, seed=19, fail=False):
    net, mode, leader = Net(seed), design["replication"], design.get("leader")
    down = (leader or "us") if fail else None  # leader designs lose the leader's region; others the busiest one
    writes, rejected, log, new_leader, t_elect = [], 0, [], None, None
    for seq, (t, origin, key) in enumerate(write_stream(seed)):
        after = fail and t >= T_FAIL
        if after and origin == down:
            continue  # those users are down with their region
        w = {"t": t, "origin": origin, "key": key, "seq": seq}
        if mode in ("async", "sync-majority"):
            if after and new_leader is None:  # failover: promote the most up-to-date survivor (Raft 5.4.1)
                survivors = [r for r in REGIONS if r != down]
                has = {r: sum(x["arrive"][r] < T_FAIL for x in log) for r in survivors}  # FIFO -> log prefix
                new_leader = max(survivors, key=lambda r: has[r])
                t_elect = T_FAIL + net.rng.uniform(*ELECTION_MS) + 2 * max(net.d(*survivors), 1.0)
                lost = [x for x in log if x["commit"] < T_FAIL and x["arrive"][new_leader] >= T_FAIL]
            lead = new_leader if after else leader
            followers = [r for r in REGIONS if r != lead and not (after and r == down)]
            t_arr, w["commit"], w["ack"], w["arrive"] = leader_write(net, mode, lead, followers, t, origin)
            if (after and t_arr < t_elect) or (fail and not after and t_arr >= T_FAIL):
                rejected += 1  # no leader yet (or the request died with the old one): the write fails
                continue
            w["accepted"] = t_arr
            log.append(w)
        elif mode == "multi-leader":  # every region accepts locally, replicates asynchronously
            w["accepted"] = w["commit"] = net.send(origin, origin, t)
            w["ack"] = net.send(origin, origin, w["commit"])
            w["arrive"] = {r: w["commit"] if r == origin else net.send(origin, r, w["commit"], fifo=True) for r in REGIONS}
        else:  # leaderless: the client's region coordinates, W=2 of the 3 regions must ack
            live = [r for r in REGIONS if not (after and r == down)]
            w["arrive"] = {r: net.send(origin, r, t) for r in live}
            backs = sorted(net.send(r, origin, w["arrive"][r]) for r in live)
            w["accepted"], w["commit"] = t, backs[1]
            w["ack"] = backs[1]
            w["arrive"].update({r: float("inf") for r in REGIONS if r not in live})
        writes.append(w)
    if mode not in ("async", "sync-majority"):  # no failover needed; data only on the dead region is gone
        lost = [w for w in writes if fail and w["commit"] < T_FAIL and all(
            w["arrive"][r] >= T_FAIL for r in REGIONS if r != down)]
    before = [w for w in writes if w["t"] < T_FAIL or not fail]
    lag = [w["arrive"][r] - w["commit"] for w in before for r in REGIONS if w["arrive"][r] != float("inf")]
    first_ok = min((w["t"] for w in writes if fail and w["t"] >= T_FAIL), default=T_FAIL)  # first write that works
    return {"p99": {o: pct([w["ack"] - w["t"] for w in before if w["origin"] == o], 99) for o in REGIONS},
            "lag_p99": pct(lag, 99), "lag_p99_at": {r: pct([w["arrive"][r] - w["commit"] for w in before
                                                          if w["arrive"][r] != float("inf")], 99) for r in REGIONS},
            "conflicts": conflicts(before) if mode in ("multi-leader", "leaderless") else 0,
            "rpo_writes": len(lost) if fail else 0, "rto_ms": round(first_ok - T_FAIL) if fail else 0,
            "rejected": rejected}


def evaluate(design, seed=19):
    calm, failed = simulate(design, seed), simulate(design, seed, fail=True)
    return {**calm, "rpo_writes": failed["rpo_writes"], "rto_ms": failed["rto_ms"], "rejected": failed["rejected"]}


def violations(m):
    c = CONSTRAINTS
    out = [f"{o} write p99 {m['p99'][o]} > {lim} ms" for o, lim in c["write_p99_ms"].items() if m["p99"][o] > lim]
    out += [f"RPO: {m['rpo_writes']} acknowledged writes lost"] if m["rpo_writes"] > c["rpo_writes"] else []
    out += [f"RTO {m['rto_ms']} ms > {c['rto_ms']:.0f} ms"] if m["rto_ms"] > c["rto_ms"] else []
    return out + ([f"{m['conflicts']} write conflicts"] if m["conflicts"] > c["conflicts"] else [])


def place_leader(replication, seed=19):
    """Choose the leader region by measurement: the lowest traffic-weighted write p99 (users far away pay)."""
    score = {r: sum(TRAFFIC[o] * simulate({"replication": replication, "leader": r}, seed)["p99"][o] for o in REGIONS)
             for r in REGIONS}
    return min(score, key=score.get)


OPTIONS = [("async", "ap"), ("async", "us"), ("sync-majority", "us"), ("sync-majority", "eu"),
           ("sync-majority", "ap"), ("multi-leader", None), ("leaderless", None)]

if __name__ == "__main__":
    print("design               write p99 us / eu / ap ms   lag p99  conflicts  RPO lost  RTO ms  rejected")
    for mode, leader in OPTIONS:
        m = evaluate({"replication": mode, "leader": leader})
        print(f"{mode + ('@' + leader if leader else ''):20} {m['p99']['us']:>8} / {m['p99']['eu']:>6} / {m['p99']['ap']:>6}"
              f" {m['lag_p99']:>9} {m['conflicts']:>10} {m['rpo_writes']:>9} {m['rto_ms']:>7} {m['rejected']:>9}")
    print(f"deployed {DESIGN}: violations {violations(evaluate(DESIGN)) or 'none'}")
    print(f"place_leader('sync-majority') -> {place_leader('sync-majority')}")
