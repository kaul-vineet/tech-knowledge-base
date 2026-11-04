"""L400 lesson 17 (python quorum.py): consistency models in practice with a quorum-replicated register.
N=3 replicas in zones A, B (one region) and C (another region); a single writer and three readers in different
zones, on a seeded simulated network (helpers.Sim; simulated ms, no sleeps). For each (R, W) we measure read and
write latency, stale reads, read-your-writes violations, new-then-old inversions and availability with a
region down - then decide per use case. The lesson file returns the newest of R replies and nothing else."""
import json

from helpers import Sim, anomalies, pct

REPLICAS, TIMEOUT_MS, RUN_MS = ("a", "b", "c"), 300.0, 10000.0
CLIENTS = {"writer": "A", "r1": "A", "r2": "B", "r3": "C", "r4": "A", "r5": "B", "r6": "C"}  # client -> its zone
SETTINGS = [(1, 1, False), (1, 2, False), (2, 2, False), (1, 3, False), (3, 1, False), (2, 2, True)]  # (R, W, write-back)


class Cluster:
    def __init__(self, sim, r, w, write_back=False):
        self.sim, self.r, self.w, self.write_back = sim, r, w, write_back
        self.version = {rep: 0 for rep in REPLICAS}  # each replica keeps the newest version it has seen

    def write(self, zone, version, done):
        """Send to all N replicas, succeed after W acks (Dynamo: latency = the W-th fastest replica)."""
        state = {"acks": 0, "over": False}

        def at_replica(back, rep):
            self.version[rep] = max(self.version[rep], version)  # apply, then ack
            self.sim.at(back, ack)

        def ack():
            state["acks"] += 1
            if state["acks"] == self.w and not state["over"]:
                state["over"] = True
                done(True, version)
        self._fan_out(zone, at_replica, state, done, version)

    def read(self, zone, done):
        """Ask all N replicas, use the first R replies (the R fastest decide the latency)."""
        state, replies = {"over": False}, []

        def at_replica(back, rep):
            self.sim.at(back, reply, self.version[rep])

        def reply(v):
            replies.append(v)
            if len(replies) == self.r and not state["over"]:
                state["over"] = True
                self.finish_read(zone, replies, done)
        self._fan_out(zone, at_replica, state, done, None)

    def finish_read(self, zone, replies, done):
        done(True, max(replies))  # newest of the R replies; write_back is ignored, so later reads may see older

    def _fan_out(self, zone, at_replica, state, done, value):
        for rep in REPLICAS:
            self.sim.send(zone, rep, at_replica, rep)

        def timeout():  # fewer than R (or W) replicas answered: the operation fails (unavailable)
            if not state["over"]:
                state["over"] = True
                done(False, value)
        self.sim.at(self.sim.now + TIMEOUT_MS, timeout)


def run(r, w, seed=17, down=(), cluster_class=Cluster, write_back=False, run_ms=RUN_MS):
    """Closed-loop clients start ops for run_ms, then the run drains: every op ends (ok or timed out).
    The writer writes v+1 then reads it back; readers read and think."""
    sim, history = Sim(seed), []
    sim.down |= set(down)
    cluster, next_version = cluster_class(sim, r, w, write_back), [0]

    def start(proc, f):
        if sim.now > run_ms:
            return
        op = {"process": proc, "f": f, "start": sim.now}

        def done(ok, value):
            op.update(ok=ok, value=value, end=sim.now)
            history.append(op)
            again = "read" if proc == "writer" and f == "write" else ("write" if proc == "writer" else "read")
            sim.at(sim.now + sim.rng.expovariate(1 / (20.0 if again == "write" else 5.0)), start, proc, again)
        if f == "write":
            next_version[0] += 1
            cluster.write(CLIENTS[proc], next_version[0], done)
        else:
            cluster.read(CLIENTS[proc], done)

    for proc in CLIENTS:
        sim.at(sim.rng.uniform(0, 5), start, proc, "write" if proc == "writer" else "read")
    sim.run(float("inf"))
    return history


def measure(r, w, write_back=False, seed=17, cluster_class=Cluster):
    history = run(r, w, seed, cluster_class=cluster_class, write_back=write_back)
    lat = {f: [op["end"] - op["start"] for op in history if op["ok"] and op["f"] == f] for f in ("read", "write")}
    a = anomalies(history)
    region_down = run(r, w, seed, down=("c",), cluster_class=cluster_class, write_back=write_back)
    avail = min(100 * sum(op["ok"] for op in region_down if op["f"] == f) / sum(op["f"] == f for op in region_down)
                for f in ("read", "write"))  # the worse of read and write availability
    return {"R": r, "W": w, "write_back": write_back, "overlap": r + w > len(REPLICAS), "read_p50": pct(lat["read"], 50),
            "read_p99": pct(lat["read"], 99), "write_p99": pct(lat["write"], 99),
            "stale_pct": round(100 * a["stale"] / a["reads"], 2), "stale_age_max": a["age_max"], "ryw": a["ryw"], "inversions": a["inversions"],
            "linearizable": a["stale"] == 0 and a["inversions"] == 0,
            "avail_c_down_pct": round(avail, 1)}


USE_CASES = {  # constraints from the design brief; decide() picks the fastest setting that meets them
    "cart badge (shows a count)": {"max_stale_pct": 20.0, "read_p99_ms": 70.0, "write_p99_ms": 40.0, "min_avail_pct": 99.0},
    "feature flag (writer sees own change)": {"max_stale_pct": 1.0, "ryw": True, "read_p99_ms": 80.0,
                                              "write_p99_ms": 100.0, "min_avail_pct": 99.0},
    "lock owner / config (linearizable)": {"linearizable": True, "read_p99_ms": 150.0, "write_p99_ms": 100.0,
                                           "min_avail_pct": 99.0},
}


def decide(rows, need):
    ok = [m for m in rows if m["stale_pct"] <= need.get("max_stale_pct", 0.0) and m["read_p99"] <= need["read_p99_ms"]
          and m["write_p99"] <= need["write_p99_ms"]
          and m["avail_c_down_pct"] >= need["min_avail_pct"] and (m["linearizable"] or not need.get("linearizable"))
          and (m["ryw"] == 0 or not need.get("ryw"))]
    return min(ok, key=lambda m: (m["read_p99"], m["write_p99"]), default=None)


def main(cluster_class=Cluster):
    rows = [measure(r, w, wb, cluster_class=cluster_class) for r, w, wb in SETTINGS]
    print("N R W wb R+W>N  read p50/p99 ms  write p99  stale% (max age ms)  ryw  inversions  linearizable  avail, C down")
    for m in rows:
        print(f"3 {m['R']} {m['W']} {'+' if m['write_back'] else '-':2} {str(m['overlap']):6} {m['read_p50']:>7}/{m['read_p99']:<6} {m['write_p99']:>9}"
              f" {m['stale_pct']:>6} ({m['stale_age_max']:>5}) {m['ryw']:>9} {m['inversions']:>10}  {str(m['linearizable']):12}"
              f" {m['avail_c_down_pct']:>6}%")
    for name, need in USE_CASES.items():
        best = decide(rows, need)
        choice = f"N=3 R={best['R']} W={best['W']}" + (" + read write-back" if best["write_back"] else "") if best else None
        print(f"decide {name}: {choice or 'NO setting meets the constraints'}")
    return rows


if __name__ == "__main__":
    print(json.dumps({"seed": 17, "run_ms": RUN_MS, "replicas": "a@A b@B c@C (C = other region)"}))
    main()
