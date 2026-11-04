"""Fleet simulation (plumbing, not lesson code): 20 stub micro:bits -> lossy radio -> 2 gateways -> gossip with
3 backend replicas. Simulated time, one seeded run; every fault below is part of the scenario, not random.

Scenario (minutes of simulated time; 12 h run, then a drain until every device log is empty):
  radio  30 % loss + 5 % duplicates + 5 % reordering per delivery (microbit L300 #12 Air faults)
         d15-d19 out of radio range 120-300 (offline-first: they keep sampling into flash)
  clocks d07 reboots at 300 (running_time restarts at 0); d05's crystal runs 1 % fast;
         g2's clock is 300 s slow and its acks carry that time to the devices that hear it
  net    g2 cut off from every other node 240-480; g1 down 360-420 (its store is durable)
  fleet  d17-d20 still run firmware schema 1 (temperature only)
"""
import math
import random
from pathlib import Path

import _kb
from gateway import FleetAir, Gateway
from store import make_store, REC_BYTES

HERE = Path(__file__).resolve().parent
FIRMWARE = HERE / "firmware"
N_DEV, V1 = 20, (17, 18, 19, 20)
EPOCH0 = 1_790_000_000                       # provisioning time (s); any fixed value
NODES = ("g1", "g2", "b1", "b2", "b3")
GOSSIP_EVERY_MIN = 5
FAULTS = dict(loss=0.3, dup=0.05, reorder=0.05)
INJECTS = ("wallclock-lww", "oversize-frame", "schema-drift")


def patch(src, old, new):
    if src.count(old) != 1:
        raise ValueError("firmware patch %r does not match exactly once" % old)
    return src.replace(old, new)


def firmware_sources(firmware="node.py", sync_every=None, inject=None):
    src = (FIRMWARE / firmware).read_text(encoding="utf-8")
    if sync_every is not None:
        src = patch(src, "SYNC_EVERY = 10 ", "SYNC_EVERY = %d " % sync_every)
    if inject == "oversize-frame":           # frames sized for length=251, radio left at the default 32
        src = patch(src, "RECORDS_PER_FRAME = 3 ", "RECORDS_PER_FRAME = 27 ")
    out = {}
    for dev in range(1, N_DEV + 1):
        out["d%02d" % dev] = patch(src, "SCHEMA = 2 ", "SCHEMA = 1 ") if dev in V1 else src
    return out


def sensors(dev, minute):
    temp = round(20 + 4 * math.sin(2 * math.pi * (minute / 720 + dev / N_DEV))) + dev % 3
    return temp, 40 + (minute * 7 + dev * 13) % 180


def life_hours(awake_ms, total_ms, fig):
    """Battery model of microbit L300 #14 (budget.FIGURES): awake at BOARD_ON_MA, else the sleep floor."""
    avg_ma = (awake_ms * fig["BOARD_ON_MA"] + (total_ms - awake_ms) * fig["SLEEP_MA"]) / total_ms
    return round(fig["BATTERY_MAH"] / avg_ma, 1), round(avg_ma, 4)


def gossip_round(rng, stores, up, reach, stats):
    """Push-pull anti-entropy (Demers et al.): each live node picks one reachable peer and swaps deltas."""
    for a in rng.sample(sorted(up), len(up)):
        peers = [b for b in sorted(up) if b != a and reach(a, b)]
        if not peers:
            continue
        b = rng.choice(peers)
        for x, y in ((a, b), (b, a)):
            delta = stores[x].delta_for(stores[y].digest())
            stats["records"] += len(delta.get("seen", delta)) if isinstance(delta, dict) else 0
            stores[y].merge_delta(delta)


def converged(stores):
    return len({repr(s.rows()) for s in stores.values()}) == 1


def convergence_experiment(trials=200, readings=600, seed=4):
    """Rounds of push-pull gossip until 5 replicas agree, each reading starting on ONE random replica."""
    rng, rounds = random.Random(seed), []
    for _ in range(trials):
        stores = {n: make_store("dots") for n in NODES}
        for i in range(readings):
            stores[rng.choice(NODES)].add((1 + i % N_DEV, 1, 1 + i // N_DEV), (EPOCH0 + i, 20, 100, 2))
        r = 0
        while not converged(stores):
            gossip_round(rng, stores, set(NODES), lambda a, b: True, {"records": 0})
            r += 1
        rounds.append(r)
    return {"trials": trials, "max": max(rounds), "mean": round(sum(rounds) / trials, 2),
            "histogram": {k: rounds.count(k) for k in sorted(set(rounds))}}


def run(seed=4, inject=None, hours=12, loss=None, sync_every=None, firmware="node.py", radio_partition=(120, 300),
        selective_ack=True):
    if inject not in (None,) + INJECTS:
        raise ValueError("unknown fault %r; choose from %s" % (inject, INJECTS))
    rng, lt = random.Random(seed), _kb.labtest()
    faults = dict(FAULTS, loss=FAULTS["loss"] if loss is None else loss)
    air = FleetAir(seed=seed, **faults)
    names = ["d%02d" % d for d in range(1, N_DEV + 1)]
    boards = lt.load_boards(str(FIRMWARE), names, filename=firmware, air=air,
                            sources=firmware_sources(firmware, sync_every, inject))
    now = [0]
    stores = {n: make_store("lww" if inject == "wallclock-lww" else "dots") for n in NODES}
    first_seen, truth, t_sample = {}, {}, {}
    on_new = lambda dot, gw: first_seen.setdefault(dot, now[0])       # noqa: E731
    clock = lambda: EPOCH0 * 1000 + now[0]                             # noqa: E731
    trust = inject != "schema-drift"
    gws = [Gateway("g1", air, stores["g1"], clock, 0, trust, on_new, selective_ack),
           Gateway("g2", air, stores["g2"], clock, -300, trust, on_new, selective_ack)]
    air.gateways = gws
    sync_n = boards[0].lab.SYNC_EVERY
    states = {b.name: b.lab.new_state(int(b.name[1:]), {"epoch_s": EPOCH0}, phase=int(b.name[1:]) % sync_n)
              for b in boards}
    boot_t, rate = {n: 0 for n in names}, {n: 1.01 if n == "d05" else 1.0 for n in names}
    carry, peak_log = {n: {} for n in names}, {n: 0 for n in names}
    gstats = {"records": 0, "rounds": 0}

    def up(m):
        return {n for n in NODES if not (n == "g1" and 360 <= m < 420)}

    def reach_at(m):
        return lambda a, b: not (240 <= m < 480 and "g2" in (a, b))

    def set_clock(b, t_ms):
        b.mb._advance_to(int((t_ms - boot_t[b.name]) * rate[b.name]))

    for m in range(hours * 60):
        now[0] = m * 60000
        air.out_of_range = {"d%02d" % d for d in range(15, 20)} if radio_partition[0] <= m < radio_partition[1] else set()
        gws[0].set_online(not (360 <= m < 420))
        for b in boards:
            if b.name == "d07" and m == 300:             # reboot: RAM lost, flash kept, running_time -> 0
                for k, v in states[b.name]["stats"].items():
                    carry[b.name][k] = carry[b.name].get(k, 0) + v
                b.mb._clock_ms, boot_t[b.name] = 0, now[0]
                del b.mb._timeline[:]
                states[b.name] = b.lab.new_state(7, states[b.name]["flash"], phase=7 % sync_n)
            set_clock(b, now[0])
            b.mb._inject_temperature(sensors(int(b.name[1:]), m)[0])
            b.mb.display.inject_light_level(sensors(int(b.name[1:]), m)[1])
            st = states[b.name]
            rec = b.lab.tick(st)
            dot = (st["dev"], rec[0], rec[1])
            truth[dot], t_sample[dot] = (rec[2], rec[3], rec[4], b.lab.SCHEMA), now[0]
            peak_log[b.name] = max(peak_log[b.name], len(st["flash"]["log"]))
        if m % GOSSIP_EVERY_MIN == 0:
            gossip_round(rng, stores, up(m), reach_at(m), gstats)
    awake = {n: carry[n].get("awake_ms", 0) + states[n]["stats"]["awake_ms"] for n in names}
    m = hours * 60
    while any(states[n]["flash"]["log"] for n in names) and m < hours * 60 + 240:   # drain: sync, no sampling
        now[0] = m * 60000
        air.out_of_range = set()
        gws[0].set_online(True)
        for b in boards:
            set_clock(b, now[0])
            if states[b.name]["flash"]["log"]:
                b.lab.sync(states[b.name])
        if m % GOSSIP_EVERY_MIN == 0:
            gossip_round(rng, stores, set(NODES), lambda a, b: True, gstats)
        m += 1
    rounds = 0
    while not converged(stores) and rounds < 50:
        gossip_round(rng, stores, set(NODES), lambda a, b: True, gstats)
        rounds += 1
    stats = {k: sum(carry[n].get(k, 0) + states[n]["stats"][k] for n in names) for k in states["d01"]["stats"]}
    dev_frames = [p for s, _, p in air.log if s.startswith("d")]
    lat = sorted(first_seen[d] - t_sample[d] for d in first_seen if d in t_sample)
    fig = _kb.budget().FIGURES
    life = {n: life_hours(awake[n], hours * 3600000, fig)[0] for n in names}
    final = stores["b1"].rows()
    return {"seed": seed, "inject": inject, "sampled": len(truth), "stored_b1": len(final),
            "lost": len(set(truth) - stores["b1"].dots()), "reached_gateway": len(first_seen),
            "logs_empty": not any(states[n]["flash"]["log"] for n in names),
            "wall_key_repeats": len(truth) - len({(d[0], v[0]) for d, v in truth.items()}),
            "wrong_values": sum(1 for d, v in final if truth.get(d) != v),
            "replicas_equal": converged(stores), "convergence_rounds": rounds, "drain_min": m - hours * 60,
            "dropped_flash_full": stats["dropped"], "peak_log": max(peak_log.values()),
            "frames": stats["frames"], "tries": stats["tries"], "max_frame_bytes": max(map(len, dev_frames)),
            "rejected": {g.name: g.rejected for g in gws}, "air": dict(air.faults),
            "p95_to_gateway_s": lat[int(0.95 * (len(lat) - 1))] // 1000 if lat else None,
            "gossip_records": gstats["records"], "gossip_bytes": gstats["records"] * REC_BYTES,
            "life_h_min": min(life.values()), "life_h": life, "awake_ms": awake,
            "conflicts": sum(getattr(s, "conflicts", 0) for s in stores.values()),
            "stores": stores, "truth": truth, "boards": boards, "states": states}


if __name__ == "__main__":
    import json
    r = run()
    print(json.dumps({k: v for k, v in r.items() if k not in ("stores", "truth", "boards", "states", "life_h",
                                                              "awake_ms")}))
