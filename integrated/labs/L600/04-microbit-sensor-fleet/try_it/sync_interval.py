"""Try it 1: the battery <-> freshness trade-off. Same seeded scenario, SYNC_EVERY = 1, 10 (shipped) and 60 samples.
Predict first: which interval misses the 2,000 h target, and what happens to freshness (p95 sample->gateway)?
Run from the lab folder:  python try_it/sync_interval.py      (Windows: py try_it\\sync_interval.py)"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fleet_sim  # noqa: E402

if __name__ == "__main__":
    for every in (1, 10, 60):
        r = fleet_sim.run(sync_every=every)
        print(json.dumps({"sync_every_min": every, "life_h_min": r["life_h_min"], "tries": r["tries"],
                          "frames": r["frames"], "p95_to_gateway_s": r["p95_to_gateway_s"], "lost": r["lost"],
                          "dropped_flash_full": r["dropped_flash_full"], "peak_log": r["peak_log"]}))
