"""L600 #04 An offline-first micro:bit sensor fleet: run it end to end and print a JSON-lines scorecard.

20 stub micro:bits (microbit topic) sample into flash and sync deltas over a 30 %-loss radio to 2 gateways;
gateways and 3 backend replicas merge a dot-keyed delta-state CRDT by gossip (distributed-systems); a versioned
API is verified by consumer-driven contracts (application-architecture). Deterministic: seed 4, simulated time.
Run:     python run_project.py                      (Windows: py run_project.py)
Faults:  python run_project.py --inject wallclock-lww | oversize-frame | schema-drift   -> FAIL, exit 1
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _kb  # noqa: E402
import api  # noqa: E402
import contracts  # noqa: E402
import fleet_sim  # noqa: E402
import gateway  # noqa: E402
import laws  # noqa: E402

TARGET_LIFE_H = 2000         # one school term on 2 x AAA (model, not a measurement)
MAX_ROUNDS = 4               # gossip rounds for 5 replicas to agree
RADIO_LENGTH = 32


def get(url):
    with urllib.request.urlopen(url, timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8")), dict(resp.headers)


def api_walk(url, store):
    """Page every device/boot through /v2 readings; the sum must equal the store (no gaps, no repeats)."""
    total = 0
    for dev, boot in sorted({(d[0], d[1]) for d in store.dots()}):
        after = 0
        while True:
            page, _ = get("%s/v2/devices/d%02d/readings?boot=%d&after=%d&limit=500" % (url, dev, boot, after))
            total += len(page["items"])
            if page["next"] is None:
                break
            after = page["next"]
    return total


def api_and_contracts(store):
    paths, tiles = contracts.consumer_side()
    with api.serve(store) as url:
        problems = contracts.verify(url)
        try:
            _, headers = get(url + "/v1/devices/d01/latest")
        except OSError:
            headers = {}
        return problems, tiles, headers.get("Deprecation"), api_walk(url, store)


def scorecard(r, law, conv, problems, deprecation, walked):
    fw = r["boards"][0].lab
    v1_rows = [d for d, v in r["stores"]["b1"].rows() if v[3] == 1]
    n_bad = sum(len(p) for p in problems.values())
    full_state_frames = -(-720 * fw.REC_LEN[2] // (RADIO_LENGTH - fw.HEADER))
    budget = _kb.budget()
    return [
        ("milestone", "M1 offline-first devices", {"sampled": r["sampled"], "dropped": r["dropped_flash_full"],
         "peak_log": r["peak_log"]}, "14400 sampled, 0 dropped, peak <= %d" % fw.MAX_LOG,
         r["sampled"] == 14400 and r["dropped_flash_full"] == 0 and r["peak_log"] <= fw.MAX_LOG),
        ("milestone", "M2 delta sync over a lossy radio", {"reached_gateway": r["reached_gateway"], "tries":
         r["tries"], "frames": r["frames"], "logs_empty": r["logs_empty"]}, "every reading at a gateway; logs empty",
         r["reached_gateway"] == r["sampled"] and r["logs_empty"]),
        ("milestone", "M3 CRDT merge + gossip", {"laws": "%d/%d" % (law["passed"], law["trials"]),
         "replicas_equal": r["replicas_equal"], "wrong_values": r["wrong_values"]}, "laws all pass; 5 replicas equal",
         law["passed"] == law["trials"] and r["replicas_equal"] and r["wrong_values"] == 0),
        ("milestone", "M4 versioned API + contracts", {"contract_problems": n_bad, "v1_deprecation": deprecation,
         "api_rows": walked}, "0 problems; v1 deprecated; API rows == stored", n_bad == 0 and bool(deprecation)
         and walked == r["stored_b1"]),
        ("seam", "S1 radio length <-> CRDT delta size", {"max_frame_bytes": r["max_frame_bytes"], "rejected":
         r["rejected"], "full_state_frames_per_device": full_state_frames}, "frames <= %d B, 0 rejected" %
         RADIO_LENGTH, r["max_frame_bytes"] <= RADIO_LENGTH and sum(r["rejected"].values()) == 0),
        ("seam", "S2 device clock <-> identity/order", {"wall_key_repeats": r["wall_key_repeats"], "lost":
         r["lost"]}, "repeats exist, 0 lost", r["wall_key_repeats"] > 0 and r["lost"] == 0),
        ("seam", "S3 battery <-> sync interval", {"firmware_active_ms": fw.ACTIVE_MS, "model_active_ms":
         budget.FIGURES["ACTIVE_MS"], "life_h_min": r["life_h_min"]}, "same ACTIVE_MS; life >= %d h" %
         TARGET_LIFE_H, fw.ACTIVE_MS == budget.FIGURES["ACTIVE_MS"] and r["life_h_min"] >= TARGET_LIFE_H),
        ("seam", "S4 firmware schema <-> backend contract", {"schema1_rows": len(v1_rows), "rec_len_equal":
         fw.REC_LEN == gateway.REC_LEN}, "2880 schema-1 rows; layouts equal", len(v1_rows) == 2880 and
         fw.REC_LEN == gateway.REC_LEN),
        ("seam", "S5 CRDT state <-> API paging", {"api_rows": walked, "stored": r["stored_b1"]},
         "paged rows == stored", walked == r["stored_b1"]),
        ("fitness", "F1 zero lost readings (30% loss + partitions)", {"lost": r["lost"], "sampled": r["sampled"]},
         "lost == 0", r["lost"] == 0 and r["wrong_values"] == 0),
        ("fitness", "F2 convergence within N gossip rounds", {"end_of_run": r["convergence_rounds"],
         "experiment_max": conv["max"], "experiment_mean": conv["mean"]}, "<= %d rounds" % MAX_ROUNDS,
         r["convergence_rounds"] <= MAX_ROUNDS and conv["max"] <= MAX_ROUNDS),
        ("fitness", "F3 battery life at the chosen sync interval", {"sync_every_min": fw.SYNC_EVERY,
         "life_h_min": r["life_h_min"]}, ">= %d h" % TARGET_LIFE_H, r["life_h_min"] >= TARGET_LIFE_H),
    ]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--inject", choices=fleet_sim.INJECTS)
    ap.add_argument("--seed", type=int, default=4)
    args = ap.parse_args(argv)
    r = fleet_sim.run(seed=args.seed, inject=args.inject)
    problems, tiles, deprecation, walked = api_and_contracts(r["stores"]["b1"])
    rows = scorecard(r, laws.check(args.seed), fleet_sim.convergence_experiment(seed=args.seed), problems,
                     deprecation, walked)
    for kind, name, value, threshold, ok in rows:
        print(json.dumps({"kind": kind, "check": name, "value": value, "threshold": threshold, "pass": bool(ok)}))
    passed = sum(bool(row[-1]) for row in rows)
    print(json.dumps({"scorecard": "PASS" if passed == len(rows) else "FAIL", "passed": passed, "total": len(rows),
                      "seed": args.seed, "inject": args.inject, "dashboard": tiles[:3]}))
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
