"""Experiment 2 / overnight - a 7-simulated-day soak of the whole fleet at 100-500 boards (seeded, simulated time).

python mac_mini/soak.py --here                      20 boards x 12 simulated hours (about a minute here)
python mac_mini/soak.py --boards 250 --days 7       one site: the overnight run on the Mac mini
python mac_mini/soak.py --boards 500 --days 7       two sites of 250 boards, one process each (parallel)

Each site is fleet_sim.run() unchanged (stub micro:bits running firmware/node.py, 30 % radio loss + duplicates +
reordering ALL WEEK, two gateways, gossip between 5 replicas, battery model) with fleet_sim.N_DEV set to the site
size; the scenario's one-off faults (partition, reboot, gateway outage, fast crystal, schema-1 boards) happen on day 1.
Why sites: the frame header carries the device id in ONE byte (firmware pack()/frames(): bytes([schema, kind, dev])),
so one radio group holds at most 255 devices - the script proves that limit by packing dev 256 and refuses larger
sites. 500 boards = 2 sites (2 radio groups, 2 gateway pairs, separate stores).
Per site: loss, convergence, battery (min life), flash pressure, p95 time-to-gateway, gossip volume, wall time and
peak memory -> memory per board-day -> the largest site that fits this Mac's RAM budget (mac_profile.py).
Soak passes when every site lost 0 readings, stored no wrong value, emptied every device log and converged.
"""
import argparse
import math
import multiprocessing as mp
import resource
import sys
import time

import _mac

DEV_ID_MAX = 255


def dev_id_limit():
    """Prove the 1-byte device id: the firmware's own frame header refuses dev 256."""
    import fleet_sim
    import importlib.util
    spec = importlib.util.spec_from_file_location("kb04_node_probe", fleet_sim.FIRMWARE / "node.py")
    lt = fleet_sim._kb.labtest()   # puts the stub `microbit` / `radio` on sys.path first
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    del lt
    ok = []
    for dev in (255, 256):
        st = {"dev": dev, "flash": {"log": [(1, 1, 0, 20, 100)]}}
        try:
            mod.frames(st)
            ok.append(dev)
        except ValueError:
            pass
    return max(ok)


def peak_rss():
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r if sys.platform == "darwin" else r * 1024


def site(args):
    boards, hours, seed = args
    import fleet_sim
    fleet_sim.N_DEV = boards                       # names d01..dNN, sensors and firmware sources follow N_DEV
    t0 = time.perf_counter()
    r = fleet_sim.run(seed=seed, hours=hours)
    wall = time.perf_counter() - t0
    keep = ("sampled", "stored_b1", "lost", "wrong_values", "logs_empty", "replicas_equal", "convergence_rounds",
            "drain_min", "dropped_flash_full", "peak_log", "frames", "tries", "p95_to_gateway_s", "gossip_bytes",
            "life_h_min", "conflicts")
    out = {"boards": boards, "hours": hours, "seed": seed, **{k: r[k] for k in keep}, "wall_s": round(wall, 1),
           "peak_rss_B": peak_rss(), "radio_frames_sent": r["air"]["sent"]}
    out["pass"] = r["lost"] == 0 and r["wrong_values"] == 0 and r["logs_empty"] and r["replicas_equal"]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--here", action="store_true", help="20 boards x 12 h")
    ap.add_argument("--boards", type=int, default=250)
    ap.add_argument("--days", type=float, default=7)
    ap.add_argument("--seed", type=int, default=4)
    ap.add_argument("--workers", type=int)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    boards, hours = (20, 12) if a.here else (a.boards, int(round(a.days * 24)))
    limit = dev_id_limit()
    sites = math.ceil(boards / limit)
    per_site = math.ceil(boards / sites)
    if per_site < 20:
        raise SystemExit("fleet_sim's scenario names devices d01-d20: use at least 20 boards per site")
    workers = 1 if a.here else min(sites, a.workers or _mac.profile(None)["workers"])
    _mac.emit({"experiment": "04 fleet soak", "boards": boards, "hours": hours, "device_id_max_per_radio_group": limit,
               "sites": sites, "boards_per_site": per_site, "workers": workers, "mode": "here" if a.here else "mac",
               "at": _mac.stamp()}, a.out)
    tasks = [(per_site, hours, a.seed + s) for s in range(sites)]
    if workers == 1:
        rows = [site(t) for t in tasks]
    else:
        with mp.get_context("spawn").Pool(workers) as pool:
            rows = pool.map(site, tasks)
    for i, r in enumerate(rows):
        _mac.emit({"site": i + 1, **r}, a.out)
    worst = max(rows, key=lambda r: r["peak_rss_B"])
    per_board_hour = worst["peak_rss_B"] / (worst["boards"] * worst["hours"])
    prof = _mac.mac_profile()
    fit = {g: min(limit, int(prof.recommend(prof.ram_from_gib(g))["budget_gb"] * 1e9 / (per_board_hour * 7 * 24)))
           for g in (16, 24, 32, 64)}
    _mac.emit({"memory": "peak RSS per board-hour (whole process, includes start-up)", "B_per_board_hour": round(per_board_hour),
               "max_boards_per_site_for_7_days_by_ram_GB": fit, "reliable": not a.here,
               "seq_wrap_days": round(0xFFFF / (24 * 60), 1),   # SAMPLE_MS = 60 s
               "reading": "the stored dot uses a 16-bit seq per boot: at one sample a minute a board that never reboots "
                          "wraps seq after seq_wrap_days - a soak longer than that must show duplicate dots"}, a.out)
    ok = all(r["pass"] for r in rows)
    _mac.emit({"scorecard": "04 mac soak", "sites": sites, "pass": ok, "decided_by": "code"}, a.out)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
