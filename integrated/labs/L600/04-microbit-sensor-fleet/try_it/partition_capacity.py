"""Try it 2: offline-first has a capacity. Keep d15-d19 out of radio range for 3 h (shipped) and for 8 h,
then 8 h again with cumulative-only acks (no exact dots). The flash log holds MAX_LOG = 400 readings = 400 min
at one per minute. Predict the loss for 8 h, and whether the ack format changes it.
Run from the lab folder:  python try_it/partition_capacity.py   (Windows: py try_it\\partition_capacity.py)"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fleet_sim  # noqa: E402

if __name__ == "__main__":
    for (start, end), selective in (((120, 300), True), ((120, 600), True), ((120, 600), False)):
        r = fleet_sim.run(radio_partition=(start, end), selective_ack=selective)
        print(json.dumps({"partition_h": (end - start) / 60, "selective_ack": selective, "peak_log": r["peak_log"],
                          "dropped_flash_full": r["dropped_flash_full"], "lost": r["lost"],
                          "logs_empty": r["logs_empty"], "replicas_equal": r["replicas_equal"]}))
